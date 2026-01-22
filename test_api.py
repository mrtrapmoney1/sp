#!/usr/bin/env python3
"""
ServicePower API Diagnostic Script
Run this to test your API connection and see the actual response.

Usage:
    python test_api.py <user_id> <password> <servicer_account> [environment]

Example:
    python test_api.py myuser mypass 12345 staging_na
"""

import sys
import requests
from datetime import datetime, timedelta

# Environment URLs
ENVIRONMENTS = {
    'staging_na': 'https://fssstag.servicepower.com/sms/services/SPDService',
    'staging_eu': 'https://fss-stg.hostedservicepower.eu/sms/services/SPDService',
    'production_na': 'https://fss.servicepower.com/sms/services/SPDService',
    'production_eu': 'https://fss.servicepower.eu/sms/services/SPDService'
}

NAMESPACE = "urn:SPDServicerService"


def create_soap_request(user_id: str, password: str, servicer_account: str) -> str:
    """Create the SOAP request for getCallInfo"""

    # Date range: last 7 days
    to_date = datetime.now()
    from_date = to_date - timedelta(days=7)
    from_datetime = from_date.strftime('%m/%d/%Y 00:00:00')
    to_datetime = to_date.strftime('%m/%d/%Y 23:59:59')

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:urn="{NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
        <urn:getCallInfoSearch>
            <UserInfo>
                <UserID>{user_id}</UserID>
                <Password>{password}</Password>
                <SvcrAcct>{servicer_account}</SvcrAcct>
            </UserInfo>
            <FromDateTime>{from_datetime}</FromDateTime>
            <ToDateTime>{to_datetime}</ToDateTime>
        </urn:getCallInfoSearch>
    </soapenv:Body>
</soapenv:Envelope>"""


def test_api(user_id: str, password: str, servicer_account: str, environment: str):
    """Test the API connection"""

    if environment not in ENVIRONMENTS:
        print(f"ERROR: Invalid environment '{environment}'")
        print(f"Valid options: {', '.join(ENVIRONMENTS.keys())}")
        return

    url = ENVIRONMENTS[environment]
    soap_request = create_soap_request(user_id, password, servicer_account)

    print("=" * 60)
    print("ServicePower API Diagnostic Test")
    print("=" * 60)
    print(f"\nEnvironment: {environment}")
    print(f"URL: {url}")
    print(f"User ID: {user_id}")
    print(f"Servicer Account: {servicer_account}")
    print("\n--- SOAP Request ---")
    print(soap_request)
    print("\n--- Sending Request ---")

    try:
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }

        response = requests.post(url, data=soap_request, headers=headers, timeout=30)

        print(f"\nHTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("\n--- SOAP Response ---")
        print(response.text[:3000])  # First 3000 chars

        if len(response.text) > 3000:
            print(f"\n... (response truncated, total length: {len(response.text)} chars)")

        # Quick analysis
        print("\n--- Analysis ---")
        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
        elif 'Fault' in response.text:
            print("ERROR: SOAP Fault detected in response")
        elif 'erroroccurred>Y<' in response.text:
            print("ERROR: API returned error (erroroccurred=Y)")
            # Try to extract error message
            import re
            code_match = re.search(r'<Code>([^<]+)</Code>', response.text)
            desc_match = re.search(r'<Description>([^<]+)</Description>', response.text)
            if code_match:
                print(f"  Error Code: {code_match.group(1)}")
            if desc_match:
                print(f"  Error Description: {desc_match.group(1)}")
        elif 'CallInfo' in response.text:
            print("SUCCESS: CallInfo found in response")
            # Count calls
            call_count = response.text.count('<CallInfo>')
            print(f"  Number of calls: {call_count}")
        else:
            print("UNKNOWN: Could not determine success/failure")

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection failed - {e}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__} - {e}")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        print("\nAvailable environments:")
        for env in ENVIRONMENTS:
            print(f"  - {env}")
        sys.exit(1)

    user_id = sys.argv[1]
    password = sys.argv[2]
    servicer_account = sys.argv[3]
    environment = sys.argv[4] if len(sys.argv) > 4 else 'production_na'

    test_api(user_id, password, servicer_account, environment)


if __name__ == '__main__':
    main()
