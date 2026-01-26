"""
Import API Blueprint

Provides endpoints for importing service calls from various sources:
- ServicePower PDF exports
- Excel/CSV files
- Converts imported data to Lotus-compatible DBF format
"""

import io
import logging
import os
import re
import struct
from datetime import datetime
from typing import Dict, List, Tuple

from flask import Blueprint, jsonify, request, send_file

logger = logging.getLogger(__name__)

imports_bp = Blueprint('imports', __name__)


def extract_field(text: str, patterns: List[str], default: str = '') -> str:
    """Extract a field value using multiple regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return default


def parse_servicepower_pdf(pdf_bytes: bytes) -> Tuple[bool, Dict, str]:
    """
    Parse a ServicePower PDF export and extract call data.

    Returns:
        Tuple of (success, call_data, message)
    """
    try:
        import pdfplumber
    except ImportError:
        return False, {}, "pdfplumber not installed. Run: pip install pdfplumber"

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

        if not text.strip():
            return False, {}, "Could not extract text from PDF"

        logger.debug(f"Extracted PDF text ({len(text)} chars): {text[:500]}...")

        # Extract fields using patterns based on SA-1831469.pdf format
        call_data = {}

        # Order/Call Number (e.g., "SA-1831469")
        call_data['BTADDRESS'] = extract_field(text, [
            r'Order\s*(?:Num|Number|#)[:\s]*([A-Z]{2}-?\d+)',
            r'Work\s*Order[:\s]*([A-Z]{2}-?\d+)',
            r'([A-Z]{2}-\d{6,})',
        ])

        # Case Number / Dealer Invoice
        call_data['DLRINVOICE'] = extract_field(text, [
            r'Case\s*(?:Number|#|No)[:\s]*(\d+)',
            r'Reference[:\s]*(\d+)',
        ])

        # Customer Name - try to split into first and last
        full_name = extract_field(text, [
            r'Recipient[:\s]*\n?\s*([A-Za-z]+\s+[A-Za-z]+)',
            r'Name[:\s]*([A-Za-z]+\s+[A-Za-z]+)',
            r'Customer[:\s]*([A-Za-z]+\s+[A-Za-z]+)',
        ])
        name_parts = full_name.split(None, 1) if full_name else ['', '']
        call_data['FIRSTNAME'] = name_parts[0] if name_parts else ''
        call_data['LASTNAME'] = name_parts[1] if len(name_parts) > 1 else ''

        # Address extraction
        address_match = re.search(
            r'(\d+[^,\n]+(?:St|Ave|Rd|Dr|Blvd|Ln|Way|Ct|Pl|Cir|Apt|Unit)[^,\n]*)',
            text, re.IGNORECASE
        )
        call_data['ADDRESS'] = address_match.group(1).strip() if address_match else ''

        # City, State, ZIP - look for pattern like "City, ST 12345"
        csz_match = re.search(
            r'([A-Za-z\s]+),?\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)',
            text
        )
        if csz_match:
            call_data['CITY'] = csz_match.group(1).strip()
            call_data['STATE'] = csz_match.group(2).strip()
            call_data['ZIP'] = csz_match.group(3).strip()
        else:
            call_data['CITY'] = ''
            call_data['STATE'] = ''
            call_data['ZIP'] = ''

        # Phone number
        phone_match = re.search(r'(\d{10}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', text)
        if phone_match:
            # Clean to just digits
            call_data['PHONE'] = re.sub(r'\D', '', phone_match.group(1))
        else:
            call_data['PHONE'] = ''
        call_data['PHONE2'] = ''

        # Product info
        call_data['MAKE'] = extract_field(text, [
            r'Brand[:\s]*([A-Za-z\s]+?)(?:\n|$)',
            r'Manufacturer[:\s]*([A-Za-z\s]+?)(?:\n|$)',
            r'(Ge\s+Cafe|Ge|Whirlpool|Samsung|LG|Frigidaire|Maytag|Kenmore)',
        ])

        call_data['TYP'] = extract_field(text, [
            r'Product[:\s]*([A-Za-z\s]+?)(?:\n|Model|$)',
            r'Appliance[:\s]*([A-Za-z\s]+?)(?:\n|$)',
            r'(Refrigerator|Washer|Dryer|Dishwasher|Range|Oven|Microwave)',
        ])

        call_data['MODEL'] = extract_field(text, [
            r'Model[:\s]*([A-Za-z0-9]+)',
            r'Model\s*(?:Number|#|No)?[:\s]*([A-Za-z0-9]+)',
        ])

        call_data['SERIAL'] = extract_field(text, [
            r'Serial[:\s]*([A-Za-z0-9]+)',
            r'Serial\s*(?:Number|#|No)?[:\s]*([A-Za-z0-9]+)',
        ])

        # Service request description
        desc_match = re.search(
            r'(?:Description|Problem|Issue|Service\s*Request)[:\s]*\n?\s*(.+?)(?:\n\n|\Z)',
            text, re.IGNORECASE | re.DOTALL
        )
        if desc_match:
            call_data['SERVICEREQ'] = desc_match.group(1).strip()[:250]  # Limit length
        else:
            call_data['SERVICEREQ'] = ''

        # Dates
        date_match = re.search(r'Created\s*(?:On|Date)?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
        if date_match:
            call_data['DATEIN'] = date_match.group(1)
        else:
            call_data['DATEIN'] = datetime.now().strftime('%m/%d/%Y')

        # Default fields
        call_data['DATEPUR'] = ''
        call_data['LOCATION'] = ''
        call_data['ACCESSOR'] = 'OW'  # Default to Out of Warranty
        call_data['TICLOC'] = ''
        call_data['INVOICE'] = ''  # Will be auto-generated

        logger.info(f"Parsed PDF: Call {call_data.get('BTADDRESS', 'Unknown')}")
        return True, call_data, "PDF parsed successfully"

    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return False, {}, f"Error parsing PDF: {str(e)}"


def parse_excel_import(file_bytes: bytes, filename: str) -> Tuple[bool, List[Dict], str]:
    """
    Parse an Excel/CSV file with call data.

    Returns:
        Tuple of (success, list of call_data dicts, message)
    """
    try:
        import pandas as pd
    except ImportError:
        return False, [], "pandas not installed"

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))

        # Normalize column names
        df.columns = [str(c).upper().strip().replace(' ', '_') for c in df.columns]

        calls = []
        for _, row in df.iterrows():
            call = {}

            # Map common column names to Lotus fields
            mappings = {
                'BTADDRESS': ['ORDER_NUM', 'ORDER_NUMBER', 'CALL_NUMBER', 'CALLNUMBER', 'WORK_ORDER'],
                'DLRINVOICE': ['CASE_NUMBER', 'CASENUMBER', 'REFERENCE', 'DEALER_INVOICE'],
                'FIRSTNAME': ['FIRST_NAME', 'FIRSTNAME', 'FNAME'],
                'LASTNAME': ['LAST_NAME', 'LASTNAME', 'LNAME', 'NAME'],
                'ADDRESS': ['ADDRESS', 'ADDRESS1', 'STREET'],
                'CITY': ['CITY'],
                'STATE': ['STATE', 'ST'],
                'ZIP': ['ZIP', 'ZIPCODE', 'ZIP_CODE', 'POSTAL'],
                'PHONE': ['PHONE', 'PHONE1', 'PHONE_NUMBER', 'PHONENUMBER'],
                'PHONE2': ['PHONE2', 'ALT_PHONE', 'ALTPHONE'],
                'MAKE': ['BRAND', 'MAKE', 'MANUFACTURER', 'MFG'],
                'TYP': ['PRODUCT', 'TYPE', 'TYP', 'APPLIANCE', 'PRODUCT_TYPE'],
                'MODEL': ['MODEL', 'MODEL_NUMBER', 'MODELNO', 'MODEL_NO'],
                'SERIAL': ['SERIAL', 'SERIAL_NUMBER', 'SERIALNO', 'SERIAL_NO'],
                'SERVICEREQ': ['DESCRIPTION', 'PROBLEM', 'SERVICE_REQUEST', 'ISSUE', 'NOTES'],
                'DATEIN': ['DATE', 'CREATED', 'CREATED_DATE', 'DATE_IN', 'DATEIN'],
            }

            for lotus_field, possible_names in mappings.items():
                for name in possible_names:
                    if name in df.columns:
                        val = row.get(name, '')
                        if pd.notna(val):
                            call[lotus_field] = str(val).strip()
                        break
                if lotus_field not in call:
                    call[lotus_field] = ''

            # Set defaults
            call.setdefault('DATEPUR', '')
            call.setdefault('LOCATION', '')
            call.setdefault('ACCESSOR', 'OW')
            call.setdefault('TICLOC', '')
            call.setdefault('INVOICE', '')

            calls.append(call)

        return True, calls, f"Parsed {len(calls)} records from Excel"

    except Exception as e:
        logger.error(f"Error parsing Excel: {e}")
        return False, [], f"Error parsing Excel: {str(e)}"


def create_lotus_dbf(calls: List[Dict]) -> bytes:
    """
    Create a dBase IV DBF file with the exact 21-field Lotus structure.

    Returns DBF file content as bytes.
    """
    # Lotus field structure (exact order required)
    fields = [
        ('INVOICE', 'C', 10),
        ('LASTNAME', 'C', 25),
        ('FIRSTNAME', 'C', 15),
        ('ADDRESS', 'C', 40),
        ('CITY', 'C', 20),
        ('STATE', 'C', 2),
        ('ZIP', 'C', 10),
        ('PHONE', 'C', 15),
        ('PHONE2', 'C', 15),
        ('LOCATION', 'C', 10),
        ('SERVICEREQ', 'C', 250),
        ('MAKE', 'C', 20),
        ('TYP', 'C', 20),
        ('MODEL', 'C', 25),
        ('SERIAL', 'C', 25),
        ('DATEIN', 'C', 10),
        ('DATEPUR', 'C', 10),
        ('BTADDRESS', 'C', 20),
        ('ACCESSOR', 'C', 50),
        ('TICLOC', 'C', 10),
        ('DLRINVOICE', 'C', 20),
    ]

    # Calculate header size
    header_size = 32 + (len(fields) * 32) + 1
    record_size = sum(f[2] for f in fields) + 1  # +1 for delete flag

    # DBF Header
    num_records = len(calls)
    now = datetime.now()

    header = struct.pack(
        '<BBBB I H H',
        0x03,  # dBase III
        now.year - 1900,
        now.month,
        now.day,
        num_records,
        header_size,
        record_size
    )
    header += b'\x00' * 20  # Reserved

    # Field descriptors
    field_descriptors = b''
    for name, ftype, length in fields:
        desc = name.encode('ascii')[:11].ljust(11, b'\x00')
        desc += ftype.encode('ascii')
        desc += b'\x00' * 4  # Reserved
        desc += struct.pack('B', length)
        desc += b'\x00' * 15  # Reserved
        field_descriptors += desc

    # Header terminator
    field_descriptors += b'\x0D'

    # Records
    records = b''
    for call in calls:
        record = b' '  # Delete flag (space = not deleted)
        for name, ftype, length in fields:
            value = str(call.get(name, '')).encode('latin-1', errors='replace')
            value = value[:length].ljust(length, b' ')
            record += value
        records += record

    # EOF marker
    eof = b'\x1A'

    return header + field_descriptors + records + eof


@imports_bp.route('/import/pdf', methods=['POST'])
def import_pdf():
    """
    Import a ServicePower PDF and return parsed call data.

    Expects multipart form data with 'file' field.

    Returns:
    {
        "success": bool,
        "call": {...},
        "message": "string"
    }
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({
            'success': False,
            'error': 'File must be a PDF'
        }), 400

    try:
        pdf_bytes = file.read()
        success, call_data, message = parse_servicepower_pdf(pdf_bytes)

        if success:
            return jsonify({
                'success': True,
                'call': call_data,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        logger.error(f"Error importing PDF: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@imports_bp.route('/import/excel', methods=['POST'])
def import_excel():
    """
    Import an Excel/CSV file with call data.

    Expects multipart form data with 'file' field.

    Returns:
    {
        "success": bool,
        "calls": [...],
        "count": int,
        "message": "string"
    }
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400

    valid_extensions = ('.xlsx', '.xls', '.csv')
    if not file.filename.lower().endswith(valid_extensions):
        return jsonify({
            'success': False,
            'error': f'File must be one of: {", ".join(valid_extensions)}'
        }), 400

    try:
        file_bytes = file.read()
        success, calls, message = parse_excel_import(file_bytes, file.filename)

        if success:
            return jsonify({
                'success': True,
                'calls': calls,
                'count': len(calls),
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        logger.error(f"Error importing Excel: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@imports_bp.route('/import/export-dbf', methods=['POST'])
def export_imported_dbf():
    """
    Export imported call data to Lotus DBF format.

    Expects JSON body:
    {
        "calls": [
            {
                "INVOICE": "...",
                "LASTNAME": "...",
                ...all 21 Lotus fields
            }
        ]
    }

    Returns: DBF file download
    """
    data = request.get_json()
    if not data or 'calls' not in data:
        return jsonify({
            'success': False,
            'error': 'No calls provided'
        }), 400

    calls = data['calls']
    if not calls:
        return jsonify({
            'success': False,
            'error': 'Empty calls list'
        }), 400

    try:
        dbf_bytes = create_lotus_dbf(calls)

        return send_file(
            io.BytesIO(dbf_bytes),
            mimetype='application/x-dbf',
            as_attachment=True,
            download_name=f'imported-calls-{datetime.now().strftime("%Y%m%d-%H%M%S")}.dbf'
        )

    except Exception as e:
        logger.error(f"Error creating DBF: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
