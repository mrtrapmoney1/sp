"""
Calls API Blueprint

Provides endpoints for fetching and updating service calls from
the ServicePower API.
"""

import logging
from flask import Blueprint, jsonify, request, session

from .auth import get_client_from_session, require_auth

logger = logging.getLogger(__name__)

calls_bp = Blueprint('calls', __name__)


@calls_bp.route('/calls', methods=['POST'])
@require_auth
def get_calls():
    """
    Fetch service calls from ServicePower.

    Expects JSON body:
    {
        "days": int (optional, default: 2),
        "from_date": "YYYY-MM-DD" (optional),
        "to_date": "YYYY-MM-DD" (optional)
    }

    Returns:
    {
        "success": bool,
        "message": "string",
        "calls": [...],
        "count": int
    }
    """
    data = request.get_json() or {}

    days = data.get('days')
    from_date = data.get('from_date')
    to_date = data.get('to_date')

    try:
        client = get_client_from_session()

        # Parse date strings if provided
        from datetime import datetime
        from_dt = datetime.strptime(from_date, '%Y-%m-%d') if from_date else None
        to_dt = datetime.strptime(to_date, '%Y-%m-%d') if to_date else None

        success, calls, message = client.get_calls(
            from_date=from_dt,
            to_date=to_dt,
            days=days or 2
        )

        # Convert ServicePowerCall objects to dictionaries
        calls_data = [call.to_dict() if hasattr(call, 'to_dict') else call for call in calls]

        # Store in session for later use (e.g., export)
        session['calls'] = calls_data

        return jsonify({
            'success': success,
            'message': message,
            'calls': calls_data,
            'count': len(calls_data)
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'calls': []
        }), 401
    except Exception as e:
        logger.error(f'Error fetching calls: {e}')
        return jsonify({
            'success': False,
            'error': f'Error fetching calls: {str(e)}',
            'calls': []
        }), 500


@calls_bp.route('/calls/<call_number>', methods=['GET'])
@require_auth
def get_call(call_number: str):
    """
    Fetch a specific service call by call number.

    Returns:
    {
        "success": bool,
        "call": {...},
        "message": "string"
    }
    """
    try:
        client = get_client_from_session()

        success, calls, message = client.get_calls(call_number=call_number, days=30)

        if not success:
            return jsonify({
                'success': False,
                'error': message,
                'call': None
            }), 400

        if not calls:
            return jsonify({
                'success': False,
                'error': f'Call {call_number} not found',
                'call': None
            }), 404

        call = calls[0]
        call_data = call.to_dict() if hasattr(call, 'to_dict') else call

        return jsonify({
            'success': True,
            'message': f'Found call {call_number}',
            'call': call_data
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'call': None
        }), 401
    except Exception as e:
        logger.error(f'Error fetching call {call_number}: {e}')
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}',
            'call': None
        }), 500


@calls_bp.route('/update/status', methods=['POST'])
@require_auth
def update_status():
    """
    Update a single call's status in ServicePower.

    Expects JSON body:
    {
        "call": {
            "CallNumber": "string",
            "MfgId": "string",
            "FSSCallId": "string"
        },
        "status": "string" (default: "ACCEPTED"),
        "substatus": "string" (default: "WAITING ON CUSTOMER")
    }

    Returns:
    {
        "success": bool,
        "message": "string"
    }
    """
    data = request.get_json() or {}
    call = data.get('call', {})
    new_status = data.get('status', 'ACCEPTED')
    new_substatus = data.get('substatus', 'WAITING ON CUSTOMER')

    call_number = call.get('CallNumber', call.get('call_number', ''))
    mfg_id = call.get('MfgId', call.get('mfg_id', ''))
    fss_call_id = call.get('FSSCallId', call.get('fss_call_id', ''))

    if not call_number:
        return jsonify({
            'success': False,
            'error': 'Call number is required'
        }), 400

    try:
        client = get_client_from_session()

        success, message = client.update_call_status(
            call_number=call_number,
            status=new_status,
            substatus=new_substatus,
            mfg_id=mfg_id,
            fss_call_id=fss_call_id
        )

        if success:
            logger.info(f'Updated call {call_number}: status={new_status}, substatus={new_substatus}')
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            logger.warning(f'Failed to update call {call_number}: {message}')
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    except Exception as e:
        logger.error(f'Error updating call {call_number}: {e}')
        return jsonify({
            'success': False,
            'error': f'Update error: {str(e)}'
        }), 500


@calls_bp.route('/update/bulk', methods=['POST'])
@require_auth
def update_bulk_status():
    """
    Update multiple calls with the same status.

    Expects JSON body:
    {
        "calls": [
            {
                "CallNumber": "string",
                "MfgId": "string",
                "FSSCallId": "string"
            },
            ...
        ],
        "status": "string" (default: "ACCEPTED"),
        "substatus": "string" (default: "WAITING ON CUSTOMER")
    }

    Returns:
    {
        "success": bool,
        "message": "string",
        "success_count": int,
        "fail_count": int,
        "results": [...]
    }
    """
    data = request.get_json() or {}
    calls = data.get('calls', [])
    new_status = data.get('status', 'ACCEPTED')
    new_substatus = data.get('substatus', 'WAITING ON CUSTOMER')

    if not calls:
        return jsonify({
            'success': False,
            'error': 'No calls provided'
        }), 400

    logger.info(f'Bulk update request: {len(calls)} calls, status={new_status}, substatus={new_substatus}')

    try:
        client = get_client_from_session()

        success_count, fail_count, results = client.bulk_update_status(
            calls=calls,
            status=new_status,
            substatus=new_substatus
        )

        logger.info(f'Bulk update complete: {success_count} success, {fail_count} failed')

        return jsonify({
            'success': True,
            'message': f'Updated {success_count} calls successfully, {fail_count} failed',
            'success_count': success_count,
            'fail_count': fail_count,
            'results': results
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 401
    except Exception as e:
        logger.error(f'Error in bulk update: {e}')
        return jsonify({
            'success': False,
            'error': f'Bulk update error: {str(e)}'
        }), 500


@calls_bp.route('/statuses', methods=['GET'])
def get_statuses():
    """
    Get list of available status and substatus values.

    Returns:
    {
        "success": true,
        "statuses": [...],
        "substatuses": [...]
    }
    """
    # Common ServicePower statuses
    statuses = [
        'NEW',
        'ACCEPTED',
        'SCHEDULED',
        'IN PROGRESS',
        'COMPLETED',
        'CANCELLED',
        'ON HOLD',
    ]

    substatuses = [
        'WAITING ON CUSTOMER',
        'WAITING ON PARTS',
        'PARTS ORDERED',
        'PARTS RECEIVED',
        'SCHEDULED',
        'COMPLETED',
        'CANCELLED BY CUSTOMER',
        'UNABLE TO CONTACT',
    ]

    return jsonify({
        'success': True,
        'statuses': statuses,
        'substatuses': substatuses
    })


@calls_bp.route('/tickets/lookup', methods=['POST'])
def lookup_ticket():
    """
    Look up a ticket from Lotus DBF files by reference number.

    Searches CUSTDATA.dbf by invoice number, call number (BTADDRESS/DLRINVOICE),
    customer name, or phone number.

    Expects JSON body:
    {
        "reference": "string" - Invoice #, call #, name, or phone
    }

    Returns:
    {
        "success": bool,
        "tickets": [...],
        "count": int
    }
    """
    import os
    import pandas as pd
    from dbfread import DBF

    data = request.get_json() or {}
    reference = data.get('reference', '').strip()

    if not reference:
        return jsonify({
            'success': False,
            'error': 'Reference number is required',
            'tickets': []
        }), 400

    dbf_path = 'data/lotus-database/CUSTDATA.dbf'

    if not os.path.exists(dbf_path):
        return jsonify({
            'success': False,
            'error': 'Customer database not found',
            'tickets': []
        }), 404

    try:
        # Read DBF file
        table = DBF(dbf_path, load=True, ignore_missing_memofile=True)
        records = list(table)

        if not records:
            return jsonify({
                'success': True,
                'tickets': [],
                'count': 0,
                'message': 'No records in database'
            })

        # Create DataFrame
        df = pd.DataFrame(records)

        # Clean data
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Search across multiple fields
        reference_upper = reference.upper()
        reference_lower = reference.lower()

        # Build search mask
        mask = pd.Series([False] * len(df))

        # Search by invoice
        if 'INVOICE' in df.columns:
            mask |= df['INVOICE'].astype(str).str.contains(reference, case=False, na=False)

        # Search by call number (BTADDRESS = ServicePower call number)
        if 'BTADDRESS' in df.columns:
            mask |= df['BTADDRESS'].astype(str).str.upper().str.contains(reference_upper, na=False)

        # Search by dealer invoice
        if 'DLRINVOICE' in df.columns:
            mask |= df['DLRINVOICE'].astype(str).str.upper().str.contains(reference_upper, na=False)

        # Search by customer name
        if 'LASTNAME' in df.columns:
            mask |= df['LASTNAME'].astype(str).str.upper().str.contains(reference_upper, na=False)

        if 'FIRSTNAME' in df.columns:
            mask |= df['FIRSTNAME'].astype(str).str.upper().str.contains(reference_upper, na=False)

        # Search by phone
        if 'PHONE' in df.columns:
            # Remove non-digits for phone comparison
            ref_digits = ''.join(filter(str.isdigit, reference))
            if len(ref_digits) >= 4:
                mask |= df['PHONE'].astype(str).str.replace(r'\D', '', regex=True).str.contains(ref_digits, na=False)

        if 'PHONE2' in df.columns:
            ref_digits = ''.join(filter(str.isdigit, reference))
            if len(ref_digits) >= 4:
                mask |= df['PHONE2'].astype(str).str.replace(r'\D', '', regex=True).str.contains(ref_digits, na=False)

        # Apply filter
        filtered = df[mask]

        # Limit results
        filtered = filtered.head(50)

        # Convert to list of dicts
        tickets = filtered.to_dict('records')

        # Clean up NaN values
        for ticket in tickets:
            for key, value in ticket.items():
                if pd.isna(value) or value == 'nan' or value == 'None':
                    ticket[key] = ''

        logger.info(f'Ticket lookup for "{reference}": found {len(tickets)} results')

        return jsonify({
            'success': True,
            'tickets': tickets,
            'count': len(tickets),
            'total_records': len(records)
        })

    except Exception as e:
        logger.error(f'Error looking up ticket: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'tickets': []
        }), 500


@calls_bp.route('/tickets/<invoice>', methods=['GET'])
def get_ticket(invoice: str):
    """
    Get a specific ticket by invoice number from Lotus DBF.

    Returns:
    {
        "success": bool,
        "ticket": {...}
    }
    """
    import os
    import pandas as pd
    from dbfread import DBF

    dbf_path = 'data/lotus-database/CUSTDATA.dbf'

    if not os.path.exists(dbf_path):
        return jsonify({
            'success': False,
            'error': 'Customer database not found',
            'ticket': None
        }), 404

    try:
        table = DBF(dbf_path, load=True, ignore_missing_memofile=True)
        records = list(table)

        df = pd.DataFrame(records)

        # Clean data
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()

        # Find by invoice
        match = df[df['INVOICE'].astype(str) == str(invoice)]

        if match.empty:
            # Try BTADDRESS (call number)
            match = df[df['BTADDRESS'].astype(str).str.upper() == invoice.upper()]

        if match.empty:
            # Try DLRINVOICE
            match = df[df['DLRINVOICE'].astype(str).str.upper() == invoice.upper()]

        if match.empty:
            return jsonify({
                'success': False,
                'error': f'Ticket {invoice} not found',
                'ticket': None
            }), 404

        ticket = match.iloc[0].to_dict()

        # Clean up NaN values
        for key, value in ticket.items():
            if pd.isna(value) or value == 'nan' or value == 'None':
                ticket[key] = ''

        return jsonify({
            'success': True,
            'ticket': ticket
        })

    except Exception as e:
        logger.error(f'Error fetching ticket {invoice}: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'ticket': None
        }), 500
