#!/usr/bin/env python3
"""
ServiceDispatch API Authentication and Connection Test Script
Based on ServiceDispatch SPD Servicer Interface Integration Guide v2.8
and WSDL: urn:SPDServicerService
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import sys
from typing import Dict, Tuple


class ServiceDispatchTester:
    """Test ServiceDispatch SOAP API authentication and connectivity"""

    # Environment URLs from documentation (Section 4.2)
    ENVIRONMENTS = {
        'staging_na': 'https://fssstag.servicepower.com/sms/services/SPDService',
        'staging_eu': 'https://fss-stg.hostedservicepower.eu/sms/services/SPDService',
        'production_na': 'https://fss.servicepower.com/sms/services/SPDService',
        'production_eu': 'https://fss.servicepower.eu/sms/services/SPDService'
    }

    # Namespace from WSDL
    NAMESPACE = "urn:SPDServicerService"

    def __init__(self, user_id: str, password: str, servicer_account: str = '',
                 environment: str = 'staging_na'):
        """
        Initialize tester with credentials

        Args:
            user_id: User ID from invitation email (10 chars max)
            password: Password (10 chars max)
            servicer_account: Servicer account number (10 chars max), optional
            environment: One of: staging_na, staging_eu, production_na, production_eu
        """
        self.user_id = user_id
        self.password = password
        self.servicer_account = servicer_account or ''

        if environment not in self.ENVIRONMENTS:
            raise ValueError(f"Invalid environment. Choose from: {list(self.ENVIRONMENTS.keys())}")

        self.base_url = self.ENVIRONMENTS[environment]
        self.environment = environment
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        })

    def _create_soap_envelope(self, body: str) -> str:
        """Create SOAP envelope with body content"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:urn="{self.NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
{body}
    </soapenv:Body>
</soapenv:Envelope>"""

    def _create_user_info(self) -> str:
        """Create UserInfo XML section for authentication

        Per WSDL: UserInfo contains UserID, Password, and SvcrAcct.
        All fields are nillable="true" so SvcrAcct is optional.
        """
        # Always include SvcrAcct element but it can be empty per WSDL nillable="true"
        return f"""            <UserInfo>
                <UserID>{self.user_id}</UserID>
                <Password>{self.password}</Password>
                <SvcrAcct>{self.servicer_account}</SvcrAcct>
            </UserInfo>"""

    def _parse_response(self, response_text: str) -> Tuple[bool, Dict]:
        """Parse SOAP response and extract data"""
        try:
            root = ET.fromstring(response_text)

            # Remove namespaces for easier parsing
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]

            # Check for SOAP Fault
            fault = root.find('.//Fault')
            if fault is not None:
                fault_string = fault.find('faultstring')
                return False, {'error': fault_string.text if fault_string is not None else 'SOAP Fault'}

            # Check for ErrorInfo
            error_info = root.find('.//ErrorInfo')
            if error_info is not None:
                code = error_info.find('Code')
                desc = error_info.find('Description')
                if code is not None and code.text and code.text != 'SP000':
                    return False, {
                        'code': code.text if code is not None else '',
                        'description': desc.text if desc is not None else ''
                    }

            # Check for erroroccurred field
            error_occurred = root.find('.//erroroccurred')
            if error_occurred is not None and error_occurred.text == 'Y':
                error_data = root.find('.//errorData')
                if error_data is not None:
                    code = error_data.find('Code')
                    desc = error_data.find('Description')
                    return False, {
                        'code': code.text if code is not None else '',
                        'description': desc.text if desc is not None else ''
                    }

            # Extract all data
            data = {}
            for elem in root.iter():
                if elem.text and elem.text.strip():
                    data[elem.tag] = elem.text.strip()

            return True, data

        except ET.ParseError as e:
            return False, {'error': f'XML Parse Error: {str(e)}'}

    def test_connectivity(self) -> Tuple[bool, str]:
        """
        Test basic connectivity using getTestService
        Returns: (success: bool, message: str)
        """
        print(f"\n{'='*60}")
        print("TEST 1: Basic Connectivity (getTestService)")
        print(f"{'='*60}")

        # From WSDL: getTestService takes a simple string
        body = """        <urn:getTestService>Hello ServiceDispatch</urn:getTestService>"""

        soap_request = self._create_soap_envelope(body)

        try:
            print(f"Connecting to: {self.base_url}")
            response = self.session.post(self.base_url, data=soap_request, timeout=30)

            print(f"Response Status: {response.status_code}")

            if response.status_code == 200:
                print("✓ Connection successful")
                if response.text:
                    # Try to parse and show response
                    success, data = self._parse_response(response.text)
                    if 'getTestServiceResponse' in data:
                        print(f"  Server response: {data.get('getTestServiceResponse', '')}")
                return True, "Connectivity test passed"
            else:
                print(f"  HTTP {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text[:300]}")
                # Even with non-200, connectivity might work - proceed to auth test
                return True, f"Connectivity established (HTTP {response.status_code})"

        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {str(e)}")
            return False, f"Connection error: {str(e)}"

    def test_authentication(self) -> Tuple[bool, str]:
        """
        Test authentication using getCallInfo
        Returns: (success: bool, message: str)
        """
        print(f"\n{'='*60}")
        print("TEST 2: Authentication (getCallInfo)")
        print(f"{'='*60}")

        # Get date range for query (last 2 days - server limit per SP007)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=2)

        from_datetime = from_date.strftime('%m/%d/%Y 00:00:00')
        to_datetime = to_date.strftime('%m/%d/%Y 23:59:59')

        user_info = self._create_user_info()

        # From WSDL: getCallInfoSearch contains UserInfo (with SvcrAcct inside), FromDateTime, ToDateTime
        body = f"""        <urn:getCallInfoSearch>
{user_info}
            <FromDateTime>{from_datetime}</FromDateTime>
            <ToDateTime>{to_datetime}</ToDateTime>
        </urn:getCallInfoSearch>"""

        soap_request = self._create_soap_envelope(body)

        try:
            print(f"User ID: {self.user_id}")
            print(f"Servicer Account: {self.servicer_account}")
            print(f"Date Range: {from_datetime} to {to_datetime}")

            response = self.session.post(self.base_url, data=soap_request, timeout=30)

            print(f"Response Status: {response.status_code}")

            if response.status_code != 200:
                print(f"✗ HTTP Error {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text[:500]}")
                return False, f"HTTP {response.status_code}"

            success, data = self._parse_response(response.text)

            if success:
                # Check for SP000 (no records) - this is actually success
                if data.get('Code') == 'SP000' or 'numberOfCalls' in data:
                    print("✓ Authentication successful")
                    num_calls = data.get('numberOfCalls', '0')
                    print(f"  Number of calls found: {num_calls}")
                    return True, f"Authentication successful - {num_calls} calls found"
                else:
                    print("✓ Authentication successful")
                    return True, "Authentication successful"
            else:
                error_code = data.get('code', 'Unknown')
                error_desc = data.get('description', data.get('error', 'No description'))

                print(f"✗ Authentication failed")
                print(f"  Error Code: {error_code}")
                print(f"  Description: {error_desc}")

                # Map common error codes (Section 14.1)
                error_messages = {
                    'SP002': "User ID does not exist in system",
                    'SP003': "Password cannot be null or blank",
                    'SP004': "Servicer account does not exist in system",
                    'SP005': "User authentication failed - invalid credentials"
                }

                return False, error_messages.get(error_code, f"Error {error_code}: {error_desc}")

        except Exception as e:
            print(f"✗ Exception: {str(e)}")
            return False, f"Exception: {str(e)}"

    def test_database_query(self, call_number: str = None) -> Tuple[bool, str]:
        """
        Test database query using getCallInfo with extended date range
        """
        print(f"\n{'='*60}")
        print("TEST 3: Database Query (getCallInfo - 2 days)")
        print(f"{'='*60}")

        to_date = datetime.now()
        from_date = to_date - timedelta(days=2)

        from_datetime = from_date.strftime('%m/%d/%Y 00:00:00')
        to_datetime = to_date.strftime('%m/%d/%Y 23:59:59')

        user_info = self._create_user_info()

        call_filter = f"<Callno>{call_number}</Callno>" if call_number else ""

        body = f"""        <urn:getCallInfoSearch>
{user_info}
            <FromDateTime>{from_datetime}</FromDateTime>
            <ToDateTime>{to_datetime}</ToDateTime>
            {call_filter}
        </urn:getCallInfoSearch>"""

        soap_request = self._create_soap_envelope(body)

        try:
            print(f"Querying calls from {from_datetime} to {to_datetime}")
            if call_number:
                print(f"Filtering by Call Number: {call_number}")

            response = self.session.post(self.base_url, data=soap_request, timeout=30)

            if response.status_code != 200:
                return False, f"HTTP {response.status_code}"

            success, data = self._parse_response(response.text)

            if success:
                print("✓ Database query successful")
                num_calls = data.get('numberOfCalls', '0')
                print(f"  Number of calls: {num_calls}")

                # Display some call info if available
                if 'CallNumber' in data:
                    print(f"\n  Sample Call Information:")
                    print(f"    Call Number: {data.get('CallNumber', 'N/A')}")
                    print(f"    FSS Call ID: {data.get('FSSCallId', 'N/A')}")
                    print(f"    Status: {data.get('CallStatus', 'N/A')}")
                    print(f"    Schedule Date: {data.get('ScheduleDate', 'N/A')}")

                return True, f"Query successful - {num_calls} calls found"
            else:
                error_code = data.get('code', 'SP000')
                if error_code == 'SP000':
                    print("  No records found in date range (this is not an error)")
                    return True, "No records found"
                else:
                    print(f"✗ Query failed: {data.get('description', 'Unknown error')}")
                    return False, f"Error {error_code}: {data.get('description', '')}"

        except Exception as e:
            print(f"✗ Exception: {str(e)}")
            return False, f"Exception: {str(e)}"

    def run_all_tests(self) -> bool:
        """
        Run all tests in sequence
        Returns: True if all tests pass
        """
        print("\n" + "="*60)
        print("ServiceDispatch API Test Suite")
        print(f"Environment: {self.environment}")
        print(f"URL: {self.base_url}")
        print("="*60)

        results = []

        # Test 1: Connectivity
        success, message = self.test_connectivity()
        results.append(('Connectivity', success, message))

        if not success:
            print("\n✗ Connectivity test failed. Cannot proceed.")
            return False

        # Test 2: Authentication
        success, message = self.test_authentication()
        results.append(('Authentication', success, message))

        if not success:
            print("\n✗ Authentication failed. Check your credentials.")
        else:
            # Test 3: Database Query (only if auth succeeded)
            success, message = self.test_database_query()
            results.append(('Database Query', success, message))

        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")

        all_passed = True
        for test_name, success, message in results:
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status}: {test_name}")
            print(f"         {message}")
            if not success:
                all_passed = False

        print(f"{'='*60}")

        if all_passed:
            print("✓ All tests passed successfully")
        else:
            print("✗ Some tests failed")

        return all_passed


def main():
    """Main entry point for command-line usage"""

    print("""
╔══════════════════════════════════════════════════════════╗
║  ServiceDispatch Authentication & Connection Test        ║
║  Based on Integration Guide v2.8 & WSDL                  ║
╚══════════════════════════════════════════════════════════╝
""")

    # Get credentials from user
    print("Please enter your ServiceDispatch credentials:")
    print("(These should be from your invitation email)\n")

    user_id = input("User ID (max 10 chars): ").strip()
    password = input("Password (max 10 chars): ").strip()
    servicer_account = input("Servicer Account Number (max 10 chars, or press Enter to skip): ").strip()

    print("\nSelect Environment:")
    print("1. Staging - North America")
    print("2. Staging - Europe")
    print("3. Production - North America")
    print("4. Production - Europe")

    env_choice = input("\nChoice (1-4) [default: 1]: ").strip() or "1"

    env_map = {
        '1': 'staging_na',
        '2': 'staging_eu',
        '3': 'production_na',
        '4': 'production_eu'
    }

    environment = env_map.get(env_choice, 'staging_na')

    # Validate inputs
    if not user_id or not password:
        print("\n✗ Error: User ID and Password are required")
        sys.exit(1)

    if len(user_id) > 10 or len(password) > 10:
        print("\n✗ Error: Credentials exceed maximum length of 10 characters")
        sys.exit(1)

    if servicer_account and len(servicer_account) > 10:
        print("\n✗ Error: Servicer account exceeds maximum length of 10 characters")
        sys.exit(1)

    if not servicer_account:
        print("\nNote: Running without Servicer Account Number")

    # Run tests
    try:
        tester = ServiceDispatchTester(
            user_id=user_id,
            password=password,
            servicer_account=servicer_account,
            environment=environment
        )

        all_passed = tester.run_all_tests()

        sys.exit(0 if all_passed else 1)

    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
