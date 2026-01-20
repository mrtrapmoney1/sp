#!/usr/bin/env python3
"""
ServiceDispatch API Web Interface
Visualize call data from ServiceDispatch SOAP API
"""

from flask import Flask, render_template, request, jsonify
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

app = Flask(__name__)

# Environment URLs
ENVIRONMENTS = {
    'staging_na': 'https://fssstag.servicepower.com/sms/services/SPDService',
    'staging_eu': 'https://fss-stg.hostedservicepower.eu/sms/services/SPDService',
    'production_na': 'https://fss.servicepower.com/sms/services/SPDService',
    'production_eu': 'https://fss.servicepower.eu/sms/services/SPDService'
}

NAMESPACE = "urn:SPDServicerService"


def create_soap_envelope(body: str) -> str:
    """Create SOAP envelope with body content"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:urn="{NAMESPACE}">
    <soapenv:Header/>
    <soapenv:Body>
{body}
    </soapenv:Body>
</soapenv:Envelope>"""


def create_user_info(user_id: str, password: str, servicer_account: str = '') -> str:
    """Create UserInfo XML section"""
    return f"""            <UserInfo>
                <UserID>{user_id}</UserID>
                <Password>{password}</Password>
                <SvcrAcct>{servicer_account}</SvcrAcct>
            </UserInfo>"""


def parse_calls_from_response(response_text: str) -> Tuple[bool, List[Dict], str]:
    """Parse SOAP response and extract call data"""
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
            return False, [], fault_string.text if fault_string is not None else 'SOAP Fault'

        # Check for error
        error_occurred = root.find('.//erroroccurred')
        if error_occurred is not None and error_occurred.text == 'Y':
            error_data = root.find('.//errorData')
            if error_data is not None:
                code = error_data.find('Code')
                desc = error_data.find('Description')
                error_msg = f"{code.text if code is not None else ''}: {desc.text if desc is not None else ''}"
                return False, [], error_msg

        # Extract calls
        calls = []
        call_elements = root.findall('.//CallInfo')

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

        return True, calls, f"Found {num} calls"

    except ET.ParseError as e:
        return False, [], f'XML Parse Error: {str(e)}'


def fetch_calls(user_id: str, password: str, servicer_account: str,
                environment: str, days: int = 2) -> Tuple[bool, List[Dict], str]:
    """Fetch calls from ServiceDispatch API"""

    if environment not in ENVIRONMENTS:
        return False, [], f"Invalid environment: {environment}"

    base_url = ENVIRONMENTS[environment]

    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)

    from_datetime = from_date.strftime('%m/%d/%Y 00:00:00')
    to_datetime = to_date.strftime('%m/%d/%Y 23:59:59')

    user_info = create_user_info(user_id, password, servicer_account)

    body = f"""        <urn:getCallInfoSearch>
{user_info}
            <FromDateTime>{from_datetime}</FromDateTime>
            <ToDateTime>{to_datetime}</ToDateTime>
        </urn:getCallInfoSearch>"""

    soap_request = create_soap_envelope(body)

    try:
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }
        response = requests.post(base_url, data=soap_request, headers=headers, timeout=30)

        if response.status_code != 200:
            return False, [], f"HTTP Error {response.status_code}"

        return parse_calls_from_response(response.text)

    except requests.exceptions.RequestException as e:
        return False, [], f"Connection error: {str(e)}"


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', environments=ENVIRONMENTS)


@app.route('/api/calls', methods=['POST'])
def get_calls():
    """API endpoint to fetch calls"""
    data = request.json

    user_id = data.get('user_id', '')
    password = data.get('password', '')
    servicer_account = data.get('servicer_account', '')
    environment = data.get('environment', 'production_na')
    days = int(data.get('days', 2))

    if not user_id or not password:
        return jsonify({'success': False, 'error': 'User ID and Password required', 'calls': []})

    success, calls, message = fetch_calls(user_id, password, servicer_account, environment, days)

    return jsonify({
        'success': success,
        'message': message,
        'calls': calls,
        'count': len(calls)
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ServiceDispatch Data Viewer")
    print("="*60)
    print("\nStarting web server...")
    print("Open http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
