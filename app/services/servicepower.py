"""
ServicePower SOAP Client Service

Provides a raw SOAP client for interacting with the ServicePower
API. Uses direct HTTP requests with manually constructed XML
for maximum compatibility.

API quirks handled:
- ProbelmDesc (typo in API for ProblemDescription)
- MobelNo (typo in API for ModelNo)
- Phone2 = "0" means empty
- Max 2-day query range (undocumented - auto-splits larger ranges)
"""

import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


# ServicePower environment URLs (no WSDL - direct endpoints)
SERVICEPOWER_ENVIRONMENTS = {
    'staging_na': 'https://fssstag.servicepower.com/sms/services/SPDService',
    'staging_eu': 'https://fss-stg.hostedservicepower.eu/sms/services/SPDService',
    'production_na': 'https://fss.servicepower.com/sms/services/SPDService',
    'production_eu': 'https://fss.servicepower.eu/sms/services/SPDService',
}

NAMESPACE = "urn:SPDServicerService"


def create_soap_envelope(body: str) -> str:
    """Create SOAP envelope with body content."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:urn="{NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
{body}
    </soapenv:Body>
</soapenv:Envelope>"""


def create_user_info(user_id: str, password: str, servicer_account: str = '') -> str:
    """Create UserInfo XML section."""
    return f"""            <UserInfo>
                <UserID>{user_id}</UserID>
                <Password>{password}</Password>
                <SvcrAcct>{servicer_account}</SvcrAcct>
            </UserInfo>"""


def parse_calls_from_response(response_text: str) -> Tuple[bool, List[Dict], str]:
    """Parse SOAP response and extract call data."""
    try:
        # Handle encoding issues - ServicePower may return non-UTF8 characters
        if isinstance(response_text, bytes):
            response_text = response_text.decode('utf-8', errors='replace')
        else:
            # Re-encode and decode to handle any problematic characters
            response_text = response_text.encode('utf-8', errors='replace').decode('utf-8')

        root = ET.fromstring(response_text)

        # Remove namespaces for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        # Check for SOAP Fault
        fault = root.find('.//Fault')
        if fault is not None:
            fault_string = fault.find('faultstring')
            fault_msg = fault_string.text if fault_string is not None else 'SOAP Fault'
            logger.error(f"SOAP Fault received: {fault_msg}")
            return False, [], fault_msg

        # Check for error
        error_occurred = root.find('.//erroroccurred')
        if error_occurred is not None and error_occurred.text == 'Y':
            error_data = root.find('.//errorData')
            if error_data is not None:
                code = error_data.find('Code')
                desc = error_data.find('Description')
                error_code = code.text if code is not None else 'UNKNOWN'
                error_desc = desc.text if desc is not None else 'Unknown error'
                error_msg = f"{error_code}: {error_desc}"
                logger.error(f"ServicePower API Error: Code={error_code}, Description={error_desc}")
                return False, [], error_msg
            else:
                logger.error("ServicePower returned erroroccurred=Y but no errorData")
                return False, [], "Unknown ServicePower error"

        # Extract calls
        calls = []
        call_elements = root.findall('.//CallInfo')
        logger.debug(f"Found {len(call_elements)} CallInfo elements in response")

        for call_elem in call_elements:
            call_data = {}
            for child in call_elem:
                if child.text and child.text.strip():
                    call_data[child.tag] = child.text.strip()
                # Handle nested elements
                for subchild in child:
                    if subchild.text and subchild.text.strip():
                        call_data[f"{child.tag}_{subchild.tag}"] = subchild.text.strip()
            if call_data:
                calls.append(call_data)

        # Get number of calls
        num_calls = root.find('.//numberOfCalls')
        num = num_calls.text if num_calls is not None else str(len(calls))
        logger.info(f"Successfully parsed {num} calls from response")

        return True, calls, f"Found {num} calls"

    except ET.ParseError as e:
        logger.error(f"XML Parse Error: {str(e)}")
        logger.debug(f"Raw response that failed to parse: {response_text[:500]}")
        return False, [], f'XML Parse Error: {str(e)}'


class ServicePowerClient:
    """
    Client for ServicePower SOAP API.

    Uses raw HTTP requests with manually constructed XML
    for maximum compatibility with the ServicePower API.
    """

    def __init__(
        self,
        user_id: str,
        password: str,
        servicer_account: str = '',
        environment: str = 'production_na',
        timeout: int = 30
    ):
        """
        Initialize ServicePower client.

        Args:
            user_id: ServicePower user ID
            password: ServicePower password
            servicer_account: Servicer account number (optional)
            environment: Environment name (staging_na, staging_eu, production_na, production_eu)
            timeout: Request timeout in seconds
        """
        self.user_id = user_id
        self.password = password
        self.servicer_account = servicer_account
        self.environment = environment
        self.timeout = timeout

        if environment not in SERVICEPOWER_ENVIRONMENTS:
            raise ValueError(f'Invalid environment: {environment}. '
                           f'Valid options: {list(SERVICEPOWER_ENVIRONMENTS.keys())}')

        self.base_url = SERVICEPOWER_ENVIRONMENTS[environment]
        logger.info(f"ServicePower client initialized for {environment}")

    def _make_request(self, soap_body: str) -> requests.Response:
        """Make SOAP request to ServicePower API."""
        soap_request = create_soap_envelope(soap_body)

        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }

        logger.debug(f"Making SOAP request to {self.base_url}")
        response = requests.post(
            self.base_url,
            data=soap_request,
            headers=headers,
            timeout=self.timeout
        )

        logger.debug(f"HTTP Response Status: {response.status_code}")
        # Ensure UTF-8 encoding for response
        response.encoding = 'utf-8'
        return response

    def _fetch_calls_single_range(
        self,
        from_date_obj: datetime,
        to_date_obj: datetime
    ) -> Tuple[bool, List[Dict], str]:
        """
        Fetch calls for a single date range (internal method).

        ServicePower has an undocumented 2-day max query limit.
        This method handles a single API call.
        """
        from_datetime = from_date_obj.strftime('%m/%d/%Y 00:00:00')
        to_datetime = to_date_obj.strftime('%m/%d/%Y 23:59:59')

        logger.debug(f"Fetching calls from {from_datetime} to {to_datetime}")

        user_info = create_user_info(self.user_id, self.password, self.servicer_account)

        body = f"""        <urn:getCallInfoSearch>
{user_info}
            <FromDateTime>{from_datetime}</FromDateTime>
            <ToDateTime>{to_datetime}</ToDateTime>
        </urn:getCallInfoSearch>"""

        try:
            response = self._make_request(body)

            if response.status_code != 200:
                logger.error(f"HTTP Error {response.status_code}: {response.text[:500]}")
                return False, [], f"HTTP Error {response.status_code}"

            return parse_calls_from_response(response.text)

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {str(e)}")
            return False, [], f"Connection error: {str(e)}"

    def get_calls(
        self,
        from_date = None,
        to_date = None,
        days: int = 2
    ) -> Tuple[bool, List[Dict], str]:
        """
        Fetch service calls from ServicePower.

        Automatically splits date ranges > 2 days into multiple API calls
        due to undocumented ServicePower API limitation.

        Args:
            from_date: Start date (YYYY-MM-DD string or datetime object)
            to_date: End date (YYYY-MM-DD string or datetime object)
            days: Number of days back if dates not specified

        Returns:
            Tuple of (success, list of call dicts, message)
        """
        # Calculate date range
        if from_date and to_date:
            # Handle both string and datetime inputs
            if isinstance(from_date, str):
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            else:
                from_date_obj = from_date

            if isinstance(to_date, str):
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            else:
                to_date_obj = to_date
        else:
            to_date_obj = datetime.now()
            from_date_obj = to_date_obj - timedelta(days=days)

        # Calculate total days in range
        total_days = (to_date_obj - from_date_obj).days

        # If range is 2 days or less, make a single call
        if total_days <= 2:
            logger.info(f"Fetching calls for {total_days + 1} day(s): {from_date_obj.date()} to {to_date_obj.date()}")
            return self._fetch_calls_single_range(from_date_obj, to_date_obj)

        # Split into 2-day chunks for larger ranges
        logger.info(f"Date range is {total_days + 1} days - splitting into 2-day chunks")

        all_calls = []
        seen_call_numbers = set()  # Deduplicate calls
        current_start = from_date_obj
        chunk_count = 0

        while current_start <= to_date_obj:
            chunk_count += 1
            # Each chunk is 2 days (current day + next day)
            current_end = min(current_start + timedelta(days=1), to_date_obj)

            logger.info(f"Chunk {chunk_count}: {current_start.date()} to {current_end.date()}")

            success, calls, message = self._fetch_calls_single_range(current_start, current_end)

            if not success:
                # If one chunk fails, log but continue with others
                logger.warning(f"Chunk {chunk_count} failed: {message}")
            else:
                # Add calls, avoiding duplicates
                for call in calls:
                    call_number = call.get('CallNumber', '')
                    if call_number and call_number not in seen_call_numbers:
                        seen_call_numbers.add(call_number)
                        all_calls.append(call)

            # Move to next chunk (2 days forward)
            current_start = current_end + timedelta(days=1)

        total_count = len(all_calls)
        logger.info(f"Fetched {total_count} unique calls across {chunk_count} API calls")

        return True, all_calls, f"Found {total_count} calls (from {chunk_count} queries)"

    def update_call_status(
        self,
        call_number: str,
        status: str,
        substatus: str,
        mfg_id: str = '',
        fss_call_id: str = ''
    ) -> Tuple[bool, str]:
        """
        Update service call status in ServicePower.

        Args:
            call_number: Call number to update
            status: New status (e.g., 'ACCEPTED', 'COMPLETED')
            substatus: New substatus (e.g., 'WAITING ON CUSTOMER')
            mfg_id: Manufacturer ID
            fss_call_id: FSS Call ID

        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Updating call {call_number}: status={status}, substatus={substatus}")

        user_info = create_user_info(self.user_id, self.password, self.servicer_account)

        body = f"""        <urn:updateCallInfoObj>
{user_info}
            <CallNumber>{call_number}</CallNumber>
            <MfgId>{mfg_id}</MfgId>
            <FSSCallId>{fss_call_id}</FSSCallId>
            <CallStatus>{status}</CallStatus>
            <CallSubStatus>{substatus}</CallSubStatus>
        </urn:updateCallInfoObj>"""

        try:
            response = self._make_request(body)

            if response.status_code != 200:
                return False, f"HTTP Error {response.status_code}"

            # Parse response for errors
            try:
                root = ET.fromstring(response.text)
                for elem in root.iter():
                    if '}' in elem.tag:
                        elem.tag = elem.tag.split('}', 1)[1]

                error_occurred = root.find('.//erroroccurred')
                if error_occurred is not None and error_occurred.text == 'Y':
                    error_data = root.find('.//errorData')
                    if error_data is not None:
                        code = error_data.find('Code')
                        desc = error_data.find('Description')
                        error_msg = f"{code.text if code is not None else ''}: {desc.text if desc is not None else ''}"
                        return False, error_msg
                    return False, "Update failed"

            except ET.ParseError:
                pass  # If we can't parse, assume success if HTTP was 200

            logger.info(f"Successfully updated call {call_number}")
            return True, "Status updated successfully"

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {str(e)}")
            return False, f"Connection error: {str(e)}"

    def bulk_update_status(
        self,
        calls: List[Dict],
        status: str,
        substatus: str
    ) -> Tuple[int, int, List[Dict]]:
        """
        Update multiple calls with the same status.

        Args:
            calls: List of call dictionaries
            status: New status
            substatus: New substatus

        Returns:
            Tuple of (success_count, fail_count, results)
        """
        success_count = 0
        fail_count = 0
        results = []

        for call in calls:
            call_number = call.get('CallNumber', call.get('call_number', ''))
            mfg_id = call.get('MfgId', call.get('mfg_id', ''))
            fss_call_id = call.get('FSSCallId', call.get('fss_call_id', ''))

            success, message = self.update_call_status(
                call_number=call_number,
                status=status,
                substatus=substatus,
                mfg_id=mfg_id,
                fss_call_id=fss_call_id
            )

            if success:
                success_count += 1
            else:
                fail_count += 1

            results.append({
                'call': call_number,
                'success': success,
                'message': message
            })

        logger.info(f"Bulk update complete: {success_count} success, {fail_count} failed")
        return success_count, fail_count, results


# Convenience function for backward compatibility
def fetch_calls(
    user_id: str,
    password: str,
    servicer_account: str,
    environment: str,
    days: int = None,
    from_date: str = None,
    to_date: str = None
) -> Tuple[bool, List[Dict], str]:
    """
    Fetch calls from ServicePower API (convenience function).

    This function provides backward compatibility with the original API.
    """
    client = ServicePowerClient(
        user_id=user_id,
        password=password,
        servicer_account=servicer_account,
        environment=environment
    )

    return client.get_calls(
        from_date=from_date,
        to_date=to_date,
        days=days or 2
    )
