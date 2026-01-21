#!/usr/bin/env python3
"""
ServiceDispatch API Web Interface
Visualize call data from ServiceDispatch SOAP API
Enhanced with pandas for advanced data processing
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import struct
import io
import secrets
import pandas as pd
from dbfread import DBF
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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
                environment: str, days: int = None, from_date: str = None,
                to_date: str = None) -> Tuple[bool, List[Dict], str]:
    """Fetch calls from ServiceDispatch API"""

    if environment not in ENVIRONMENTS:
        return False, [], f"Invalid environment: {environment}"

    base_url = ENVIRONMENTS[environment]

    # Handle custom date range or days
    if from_date and to_date:
        from_datetime = datetime.strptime(from_date, '%Y-%m-%d').strftime('%m/%d/%Y 00:00:00')
        to_datetime = datetime.strptime(to_date, '%Y-%m-%d').strftime('%m/%d/%Y 23:59:59')
    else:
        days = days or 2
        to_date_obj = datetime.now()
        from_date_obj = to_date_obj - timedelta(days=days)
        from_datetime = from_date_obj.strftime('%m/%d/%Y 00:00:00')
        to_datetime = to_date_obj.strftime('%m/%d/%Y 23:59:59')

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
def login():
    """Render login page"""
    return render_template('login.html', environments=ENVIRONMENTS)


@app.route('/dashboard')
def index():
    """Render main dashboard"""
    if 'credentials' not in session:
        return redirect('/')
    return render_template('index.html', environments=ENVIRONMENTS, active_page='dashboard')


@app.route('/api/calls', methods=['POST'])
def get_calls():
    """API endpoint to fetch calls"""
    data = request.json

    # Get credentials from session
    creds = session.get('credentials', {})
    user_id = creds.get('user_id', '')
    password = creds.get('password', '')
    servicer_account = creds.get('servicer_account', '')
    environment = creds.get('environment', 'production_na')

    if not user_id or not password:
        return jsonify({'success': False, 'error': 'Not authenticated. Please log in again.', 'calls': []})

    days = data.get('days')
    from_date = data.get('from_date')
    to_date = data.get('to_date')

    success, calls, message = fetch_calls(
        user_id, password, servicer_account, environment,
        days=days, from_date=from_date, to_date=to_date
    )

    # Store calls in session for later use
    session['calls'] = calls

    return jsonify({
        'success': success,
        'message': message,
        'calls': calls,
        'count': len(calls)
    })


@app.route('/tickets')
def tickets():
    """Render ticket creator page"""
    if 'credentials' not in session:
        return redirect('/')
    return render_template('tickets.html', environments=ENVIRONMENTS, active_page='tickets')


@app.route('/map')
def map_view():
    """Render map visualization page"""
    if 'credentials' not in session:
        return redirect('/')
    return render_template('map.html', environments=ENVIRONMENTS, active_page='map')


@app.route('/analytics')
def analytics():
    """Render analytics dashboard page"""
    if 'credentials' not in session:
        return redirect('/')
    return render_template('analytics.html', environments=ENVIRONMENTS, active_page='analytics')


@app.route('/diagnosis')
def diagnosis():
    """Render enhanced diagnosis helper page"""
    if 'credentials' not in session:
        return redirect('/')
    return render_template('diagnosis_enhanced.html', environments=ENVIRONMENTS, active_page='diagnosis')


@app.route('/parts')
def parts():
    """Render parts lookup page"""
    if 'credentials' not in session:
        return redirect('/')
    return render_template('parts.html', environments=ENVIRONMENTS, active_page='parts')


@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for login"""
    data = request.json

    user_id = data.get('user_id', '')
    password = data.get('password', '')
    servicer_account = data.get('servicer_account', '')
    environment = data.get('environment', 'production_na')

    if not user_id or not password:
        return jsonify({'success': False, 'error': 'User ID and Password required'})

    # Test connection with ServicePower
    success, calls, message = fetch_calls(user_id, password, servicer_account, environment, days=1)

    if success:
        # Store credentials in session
        session['credentials'] = {
            'user_id': user_id,
            'password': password,
            'servicer_account': servicer_account,
            'environment': environment
        }
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'error': message})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/parts/history', methods=['POST'])
def get_parts_history():
    """Get parts usage history from Partlog.dbf using pandas"""
    data = request.json
    search_term = data.get('search', '').lower()

    try:
        dbf_path = 'Lotus documentation/Partlog.dbf'

        # Read DBF file using dbfread library and convert to pandas DataFrame
        table = DBF(dbf_path, load=True, ignore_missing_memofile=True)

        # Convert to list of dicts
        records = list(table)

        # Create pandas DataFrame
        df = pd.DataFrame(records)

        # Clean up data
        if not df.empty:
            # Strip whitespace from string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()

            # Filter by search term if provided
            if search_term:
                # Search across all columns
                mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(search_term, na=False).any(), axis=1)
                df = df[mask]

            # Limit to 500 most recent records
            df = df.head(500)

            # Convert to dict
            parts_data = df.to_dict('records')
        else:
            parts_data = []

        return jsonify({
            'success': True,
            'parts': parts_data,
            'count': len(parts_data),
            'total_records': len(records)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'parts': [], 'total_records': 0})


def map_call_to_lotus(call: Dict, invoice: str) -> Dict:
    """Map ServicePower call data to Lotus DBF fields"""
    today = datetime.now().strftime('%Y%m%d')

    # Handle phone2 - if "0", make it empty
    phone2 = call.get('ConsumerInfo_Phone2', '')
    if phone2 == '0':
        phone2 = ''

    # Determine accessor based on warranty type
    warranty = call.get('WarrantyType', '')
    accessor_map = {
        'IW': 'If less than $550 then no approval is needed',
        'SC': '$140',
    }
    accessor = accessor_map.get(warranty, '')

    # Extract ZIP (first 5 chars if longer)
    zip_code = call.get('ConsumerInfo_Postcode', '')
    if len(zip_code) > 5:
        zip_code = zip_code.split('-')[0][:5]

    return {
        'INVOICE': invoice,
        'LASTNAME': call.get('ConsumerInfo_ConsumerLastName', '')[:25],
        'FIRSTNAME': call.get('ConsumerInfo_ConsumerFirstName', '')[:15],
        'ADDRESS': call.get('ConsumerInfo_ConsumerAddress1', '')[:25],
        'CITY': call.get('ConsumerInfo_PostcodeLevel3', '')[:30],
        'STATE': call.get('ConsumerInfo_PostcodeLevel1', '')[:2],
        'ZIP': zip_code[:5],
        'PHONE': call.get('ConsumerInfo_Phone1', '')[:12],
        'PHONE2': phone2[:12],
        'LOCATION': 'Service Call',
        'SERVICEREQ': call.get('ProbelmDesc', '')[:250],
        'MAKE': call.get('ProductInfo_SPBrandDesc', '')[:15],
        'TYP': call.get('ProductInfo_SPProductDesc', '')[:15],
        'MODEL': call.get('ProductInfo_MobelNo', '')[:20],
        'SERIAL': call.get('ProductInfo_SerialNo', '')[:26],
        'DATEIN': today,
        'DATEPUR': call.get('ProductInfo_InstallDate', '').replace('/', '')[:8] if call.get('ProductInfo_InstallDate') else '',
        'BTADDRESS': call.get('CallNumber', '')[:30],
        'ACCESSOR': accessor[:150],
        'TICLOC': f"{datetime.now().strftime('%m/%d')} Gail"[:25],
        'DLRINVOICE': call.get('CallNumber', '')[:17],
    }


def create_dbf_file(records: List[Dict]) -> bytes:
    """Create a DBF file from Lotus-formatted records"""

    # DBF field definitions for Lotus import (based on CUSTDATA.DBF)
    # Note: Field name "TYP" appears as "TYP 0" in CUSTDATA.DBF with a space
    fields = [
        ('INVOICE', 'N', 5, 0),
        ('LASTNAME', 'C', 25, 0),
        ('FIRSTNAME', 'C', 15, 0),
        ('ADDRESS', 'C', 25, 0),
        ('CITY', 'C', 30, 0),
        ('STATE', 'C', 2, 0),
        ('ZIP', 'C', 5, 0),
        ('PHONE', 'C', 12, 0),
        ('PHONE2', 'C', 12, 0),
        ('LOCATION', 'C', 15, 0),
        ('SERVICEREQ', 'C', 250, 0),
        ('MAKE', 'C', 15, 0),
        ('TYP', 'C', 15, 0),  # Maps to "TYP 0" in CUSTDATA.DBF
        ('MODEL', 'C', 20, 0),
        ('SERIAL', 'C', 26, 0),
        ('DATEIN', 'D', 8, 0),
        ('DATEPUR', 'D', 8, 0),
        ('BTADDRESS', 'C', 30, 0),
        ('ACCESSOR', 'C', 150, 0),
        ('TICLOC', 'C', 25, 0),
        ('DLRINVOICE', 'C', 17, 0),  # Dealer invoice = CallNumber
    ]

    # Calculate record length (1 byte for deletion flag + sum of field lengths)
    record_len = 1 + sum(f[2] for f in fields)
    header_len = 32 + (len(fields) * 32) + 1  # Header + field descriptors + terminator

    now = datetime.now()
    num_records = len(records)

    # Build DBF file in memory
    buffer = io.BytesIO()

    # Write header
    buffer.write(struct.pack('B', 0x03))  # dBase III
    buffer.write(struct.pack('B', now.year - 1900))
    buffer.write(struct.pack('B', now.month))
    buffer.write(struct.pack('B', now.day))
    buffer.write(struct.pack('<I', num_records))
    buffer.write(struct.pack('<H', header_len))
    buffer.write(struct.pack('<H', record_len))
    buffer.write(bytes(20))  # Reserved bytes

    # Write field descriptors
    for field_name, field_type, field_len, decimals in fields:
        field_name_bytes = field_name.encode('ascii')[:11].ljust(11, b'\x00')
        buffer.write(field_name_bytes)
        buffer.write(field_type.encode('ascii'))
        buffer.write(bytes(4))  # Reserved
        buffer.write(struct.pack('B', field_len))
        buffer.write(struct.pack('B', decimals))
        buffer.write(bytes(14))  # Reserved

    # Write field descriptor terminator
    buffer.write(b'\x0D')

    # Write records
    for record in records:
        buffer.write(b' ')  # Deletion flag (space = not deleted)

        for field_name, field_type, field_len, decimals in fields:
            value = record.get(field_name, '')

            if field_type == 'C':  # Character
                value_bytes = str(value).encode('ascii', errors='ignore')[:field_len]
                buffer.write(value_bytes.ljust(field_len, b' '))
            elif field_type == 'N':  # Numeric
                value_str = str(value).rjust(field_len, ' ')
                buffer.write(value_str.encode('ascii'))
            elif field_type == 'D':  # Date (YYYYMMDD)
                if value and len(value) == 8:
                    buffer.write(value.encode('ascii'))
                else:
                    buffer.write(b' ' * 8)

    # Write end-of-file marker
    buffer.write(b'\x1A')

    return buffer.getvalue()


@app.route('/api/export/dbf', methods=['POST'])
def export_dbf():
    """Export selected calls as DBF file"""
    data = request.json
    selected_calls = data.get('calls', [])

    if not selected_calls:
        return jsonify({'success': False, 'error': 'No calls selected'})

    # Map calls to Lotus format
    lotus_records = []
    for call_data in selected_calls:
        invoice = call_data.get('invoice', '')
        if not invoice:
            continue
        lotus_record = map_call_to_lotus(call_data, invoice)
        lotus_records.append(lotus_record)

    if not lotus_records:
        return jsonify({'success': False, 'error': 'No valid records to export'})

    # Create DBF file
    dbf_data = create_dbf_file(lotus_records)

    # Send as download
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'lotus_tickets_{timestamp}.dbf'

    return send_file(
        io.BytesIO(dbf_data),
        mimetype='application/x-dbase',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/update/status', methods=['POST'])
def update_status():
    """Update call status in ServicePower"""
    data = request.json
    call = data.get('call', {})
    new_status = data.get('status', 'ACCEPTED')
    new_substatus = data.get('substatus', 'WAITING ON CUSTOMER')

    # Get credentials from session
    creds = session.get('credentials', {})
    if not creds.get('user_id') or not creds.get('password'):
        return jsonify({'success': False, 'error': 'Not authenticated. Please log in again.'})

    user_id = creds['user_id']
    password = creds['password']
    servicer_account = creds.get('servicer_account', '')
    environment = creds.get('environment', 'production_na')

    if environment not in ENVIRONMENTS:
        return jsonify({'success': False, 'error': 'Invalid environment'})

    base_url = ENVIRONMENTS[environment]
    user_info = create_user_info(user_id, password, servicer_account)

    # Build update call SOAP request
    call_number = call.get('CallNumber', '')
    fss_call_id = call.get('FSSCallId', '')
    mfg_id = call.get('MfgId', '')

    body = f"""        <urn:updateCallInfoObj>
{user_info}
            <CallNumber>{call_number}</CallNumber>
            <MfgId>{mfg_id}</MfgId>
            <FSSCallId>{fss_call_id}</FSSCallId>
            <CallStatus>{new_status}</CallStatus>
            <CallSubStatus>{new_substatus}</CallSubStatus>
        </urn:updateCallInfoObj>"""

    soap_request = create_soap_envelope(body)

    try:
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }
        response = requests.post(base_url, data=soap_request, headers=headers, timeout=30)

        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'HTTP Error {response.status_code}'})

        # Parse response
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
                return jsonify({'success': False, 'error': error_msg})

        return jsonify({'success': True, 'message': 'Status updated successfully'})

    except Exception as e:
        return jsonify({'success': False, 'error': f'Update error: {str(e)}'})


@app.route('/api/parts/analytics', methods=['POST'])
def get_parts_analytics():
    """Get advanced analytics from parts history using pandas"""
    data = request.json
    make = data.get('make', '').upper()
    model = data.get('model', '').upper()
    problem = data.get('problem', '').lower()

    try:
        dbf_path = 'Lotus documentation/Partlog.dbf'

        # Read DBF file
        table = DBF(dbf_path, load=True, ignore_missing_memofile=True)
        records = list(table)

        # Create DataFrame
        df = pd.DataFrame(records)

        if df.empty:
            return jsonify({'success': True, 'analytics': {}, 'recommendations': []})

        # Clean data
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Filter by make/model if provided
        filtered_df = df.copy()
        if make and 'MAKE' in df.columns:
            filtered_df = filtered_df[filtered_df['MAKE'].str.upper().str.contains(make, na=False)]
        if model and 'MODEL' in df.columns:
            filtered_df = filtered_df[filtered_df['MODEL'].str.upper().str.contains(model, na=False)]

        # Identify part number columns (P1, P2, P3, PART_NUM, etc.)
        part_cols = [col for col in df.columns if 'P1' in col or 'P2' in col or 'P3' in col or 'PART' in col.upper()]
        desc_cols = [col for col in df.columns if 'PD1' in col or 'PD2' in col or 'PD3' in col or 'DESC' in col.upper()]

        # Get most common parts
        all_parts = []
        for col in part_cols:
            if col in filtered_df.columns:
                parts = filtered_df[col].dropna()
                parts = parts[parts != '']
                all_parts.extend(parts.tolist())

        if all_parts:
            parts_series = pd.Series(all_parts)
            top_parts = parts_series.value_counts().head(10)
            most_common_parts = [{'part': part, 'count': int(count)} for part, count in top_parts.items()]
        else:
            most_common_parts = []

        # Get common problems
        problem_col = None
        for col in ['SERVICEREQ', 'SYMPT', 'PROBLEM']:
            if col in filtered_df.columns:
                problem_col = col
                break

        if problem_col:
            problems = filtered_df[problem_col].dropna()
            problems = problems[problems != '']
            top_problems = problems.value_counts().head(10)
            common_problems = [{'problem': prob, 'count': int(count)} for prob, count in top_problems.items()]
        else:
            common_problems = []

        # Get recommendations if problem specified
        recommendations = []
        if problem and problem_col:
            problem_matches = filtered_df[filtered_df[problem_col].str.lower().str.contains(problem, na=False)]

            if not problem_matches.empty:
                # Get parts used for similar problems
                recommended_parts = []
                for col in part_cols:
                    if col in problem_matches.columns:
                        parts = problem_matches[col].dropna()
                        parts = parts[parts != '']
                        recommended_parts.extend(parts.tolist())

                if recommended_parts:
                    parts_series = pd.Series(recommended_parts)
                    top_recommended = parts_series.value_counts().head(5)
                    recommendations = [
                        {'part': part, 'frequency': int(count), 'confidence': f"{(count/len(problem_matches))*100:.1f}%"}
                        for part, count in top_recommended.items()
                    ]

        # Calculate statistics
        analytics = {
            'total_records': len(df),
            'filtered_records': len(filtered_df),
            'most_common_parts': most_common_parts,
            'common_problems': common_problems,
            'unique_makes': df['MAKE'].nunique() if 'MAKE' in df.columns else 0,
            'unique_models': df['MODEL'].nunique() if 'MODEL' in df.columns else 0,
        }

        return jsonify({
            'success': True,
            'analytics': analytics,
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'analytics': {}, 'recommendations': []})


@app.route('/api/customer/analytics', methods=['POST'])
def get_customer_analytics():
    """Get customer database analytics using pandas"""
    try:
        dbf_path = 'Lotus documentation/CUSTDATA.dbf'

        if not os.path.exists(dbf_path):
            return jsonify({'success': False, 'error': 'Customer database not found', 'analytics': {}})

        # Read customer database
        table = DBF(dbf_path, load=True, ignore_missing_memofile=True)
        records = list(table)

        # Create DataFrame
        df = pd.DataFrame(records)

        if df.empty:
            return jsonify({'success': True, 'analytics': {}})

        # Clean data
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Calculate analytics
        analytics = {
            'total_customers': len(df),
            'unique_cities': df['CITY'].nunique() if 'CITY' in df.columns else 0,
            'unique_zips': df['ZIP'].nunique() if 'ZIP' in df.columns else 0,
        }

        # Top cities
        if 'CITY' in df.columns:
            city_counts = df['CITY'].value_counts().head(10)
            analytics['top_cities'] = [{'city': city, 'count': int(count)} for city, count in city_counts.items() if city and city != 'nan']

        # Top makes
        if 'MAKE' in df.columns:
            make_counts = df['MAKE'].value_counts().head(10)
            analytics['top_makes'] = [{'make': make, 'count': int(count)} for make, count in make_counts.items() if make and make != 'nan']

        # Top product types
        if 'TYP' in df.columns or 'TYPE' in df.columns:
            type_col = 'TYP' if 'TYP' in df.columns else 'TYPE'
            type_counts = df[type_col].value_counts().head(10)
            analytics['top_product_types'] = [{'type': ptype, 'count': int(count)} for ptype, count in type_counts.items() if ptype and ptype != 'nan']

        # Recent entries (if DATEIN exists)
        if 'DATEIN' in df.columns:
            df['DATEIN_dt'] = pd.to_datetime(df['DATEIN'], format='%Y%m%d', errors='coerce')
            recent = df.nlargest(10, 'DATEIN_dt')
            analytics['recent_entries'] = len(recent)

        return jsonify({'success': True, 'analytics': analytics})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'analytics': {}})


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Get AI-like recommendations based on historical data"""
    data = request.json
    make = data.get('make', '').upper()
    model = data.get('model', '').upper()
    product_type = data.get('product_type', '').upper()
    problem = data.get('problem', '').lower()

    try:
        dbf_path = 'Lotus documentation/Partlog.dbf'

        # Read parts history
        table = DBF(dbf_path, load=True, ignore_missing_memofile=True)
        records = list(table)

        df = pd.DataFrame(records)

        if df.empty:
            return jsonify({'success': True, 'recommendations': [], 'confidence': 'low'})

        # Clean data
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Multi-level filtering
        filtered_df = df.copy()
        filters_applied = []

        if make and 'MAKE' in df.columns:
            filtered_df = filtered_df[filtered_df['MAKE'].str.upper().str.contains(make, na=False)]
            filters_applied.append('make')

        if model and 'MODEL' in df.columns:
            filtered_df = filtered_df[filtered_df['MODEL'].str.upper().str.contains(model, na=False)]
            filters_applied.append('model')

        if problem:
            problem_cols = [col for col in df.columns if 'SERVICEREQ' in col or 'SYMPT' in col or 'PROBLEM' in col]
            if problem_cols:
                problem_mask = filtered_df[problem_cols[0]].str.lower().str.contains(problem, na=False)
                filtered_df = filtered_df[problem_mask]
                filters_applied.append('problem')

        # Extract parts
        part_cols = [col for col in df.columns if col in ['P1', 'P2', 'P3', 'PART_NUM']]
        desc_cols = [col for col in df.columns if col in ['PD1', 'PD2', 'PD3', 'PART_DESC']]

        parts_with_desc = []
        for idx, row in filtered_df.iterrows():
            for i, part_col in enumerate(part_cols):
                if part_col in row and row[part_col] and str(row[part_col]).strip():
                    part_num = str(row[part_col]).strip()
                    desc = ''
                    if i < len(desc_cols) and desc_cols[i] in row:
                        desc = str(row[desc_cols[i]]).strip()
                    parts_with_desc.append({'part': part_num, 'description': desc})

        # Count frequency
        if parts_with_desc:
            parts_df = pd.DataFrame(parts_with_desc)
            part_counts = parts_df.groupby(['part', 'description']).size().reset_index(name='frequency')
            part_counts = part_counts.sort_values('frequency', ascending=False).head(10)

            # Calculate confidence
            total_matches = len(filtered_df)
            if total_matches > 20:
                confidence = 'high'
            elif total_matches > 5:
                confidence = 'medium'
            else:
                confidence = 'low'

            recommendations = []
            for _, row in part_counts.iterrows():
                recommendations.append({
                    'part_number': row['part'],
                    'description': row['description'],
                    'frequency': int(row['frequency']),
                    'success_rate': f"{(row['frequency']/total_matches)*100:.1f}%",
                    'sample_size': total_matches
                })

            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'confidence': confidence,
                'filters_applied': filters_applied,
                'total_matches': total_matches
            })
        else:
            return jsonify({
                'success': True,
                'recommendations': [],
                'confidence': 'none',
                'message': 'No matching records found. Try broader search criteria.'
            })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'recommendations': [], 'confidence': 'error'})


@app.route('/api/update/bulk', methods=['POST'])
def update_bulk_status():
    """Update multiple calls to WAITING ON CUSTOMER status"""
    data = request.json
    calls = data.get('calls', [])

    # Get credentials from session
    creds = session.get('credentials', {})
    if not creds.get('user_id') or not creds.get('password'):
        return jsonify({'success': False, 'error': 'Not authenticated. Please log in again.'})

    user_id = creds['user_id']
    password = creds['password']
    servicer_account = creds.get('servicer_account', '')
    environment = creds.get('environment', 'production_na')

    if environment not in ENVIRONMENTS:
        return jsonify({'success': False, 'error': 'Invalid environment'})

    base_url = ENVIRONMENTS[environment]
    user_info = create_user_info(user_id, password, servicer_account)

    results = []
    success_count = 0
    fail_count = 0

    for call in calls:
        call_number = call.get('CallNumber', '')
        fss_call_id = call.get('FSSCallId', '')
        mfg_id = call.get('MfgId', '')

        body = f"""        <urn:updateCallInfoObj>
{user_info}
            <CallNumber>{call_number}</CallNumber>
            <MfgId>{mfg_id}</MfgId>
            <FSSCallId>{fss_call_id}</FSSCallId>
            <CallStatus>ACCEPTED</CallStatus>
            <CallSubStatus>WAITING ON CUSTOMER</CallSubStatus>
        </urn:updateCallInfoObj>"""

        soap_request = create_soap_envelope(body)

        try:
            headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': ''
            }
            response = requests.post(base_url, data=soap_request, headers=headers, timeout=30)

            if response.status_code == 200:
                root = ET.fromstring(response.text)
                for elem in root.iter():
                    if '}' in elem.tag:
                        elem.tag = elem.tag.split('}', 1)[1]

                error_occurred = root.find('.//erroroccurred')
                if error_occurred is not None and error_occurred.text == 'Y':
                    fail_count += 1
                    error_data = root.find('.//errorData')
                    error_msg = 'Unknown error'
                    if error_data is not None:
                        code = error_data.find('Code')
                        desc = error_data.find('Description')
                        error_msg = f"{code.text if code is not None else ''}: {desc.text if desc is not None else ''}"
                    results.append({'call': call_number, 'success': False, 'error': error_msg})
                else:
                    success_count += 1
                    results.append({'call': call_number, 'success': True})
            else:
                fail_count += 1
                results.append({'call': call_number, 'success': False})

        except Exception as e:
            fail_count += 1
            results.append({'call': call_number, 'success': False, 'error': str(e)})

    return jsonify({
        'success': True,
        'message': f'Updated {success_count} calls successfully, {fail_count} failed',
        'success_count': success_count,
        'fail_count': fail_count,
        'results': results
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
