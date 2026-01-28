"""
Bulk Operations API Blueprint

Provides endpoints for bulk call updates including:
- Bulk substatus updates (primarily WAITING ON CUSTOMER)
- Bulk schedule date changes with automatic substatus
- Adding ticket numbers to notes
- SMS message generation
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session

from ..services.servicepower import ServicePowerClient

logger = logging.getLogger(__name__)

bulk_bp = Blueprint('bulk', __name__)


def require_auth(func):
    """Decorator to require authentication."""
    from functools import wraps

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'credentials' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        return func(*args, **kwargs)

    return decorated_function


def get_client_from_session():
    """Create ServicePowerClient from session credentials."""
    creds = session.get('credentials', {})
    return ServicePowerClient(
        user_id=creds.get('user_id'),
        password=creds.get('password'),
        servicer_account=creds.get('servicer_account'),
        environment=creds.get('environment', 'production_na')
    )


@bulk_bp.route('/api/bulk/update-substatus', methods=['POST'])
@require_auth
def bulk_update_substatus():
    """
    Update substatus for multiple calls.

    Request body:
    {
        "call_numbers": ["ABC123", "DEF456"],
        "substatus_id": "ACT35",
        "notes": "Optional notes to add"
    }
    """
    try:
        data = request.get_json()
        call_numbers = data.get('call_numbers', [])
        substatus_id = data.get('substatus_id', 'ACT35')  # Default: WAITING ON CUSTOMER
        notes = data.get('notes', '')

        if not call_numbers:
            return jsonify({
                'success': False,
                'error': 'No call numbers provided'
            }), 400

        client = get_client_from_session()

        # Get substatus details from mapping
        substatus_info = SUBSTATUS_MAPPING.get(substatus_id, {
            'status': 'ACCEPTED',
            'status_id': '3',
            'name': 'WAITING ON CUSTOMER'
        })

        success_count = 0
        failed_calls = []

        for call_number in call_numbers:
            try:
                # Build update request
                update_data = {
                    'CallNumber': call_number,
                    'CallStatus': substatus_info['status'],
                    'SPCallStatusID': substatus_info['status_id'],
                    'SPCallSubStatusID': substatus_id
                }

                # Add notes if provided
                if notes:
                    update_data['Remarks'] = {
                        'NotesDate': datetime.now().strftime('%Y%m%d %H:%M:%S'),
                        'Notes': notes,
                        'AddedBy': session.get('credentials', {}).get('user_id', 'API')
                    }

                result = client.update_call_status(
                    call_number=call_number,
                    status=substatus_info['status'],
                    substatus=substatus_id,
                    additional_data=update_data
                )

                if result.get('success'):
                    success_count += 1
                else:
                    failed_calls.append({
                        'call_number': call_number,
                        'error': result.get('error', 'Unknown error')
                    })

            except Exception as e:
                logger.error(f'Error updating call {call_number}: {e}')
                failed_calls.append({
                    'call_number': call_number,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'data': {
                'success_count': success_count,
                'failed_count': len(failed_calls),
                'total': len(call_numbers),
                'failed_calls': failed_calls
            },
            'message': f'Updated {success_count} of {len(call_numbers)} calls'
        })

    except Exception as e:
        logger.error(f'Bulk substatus update error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bulk_bp.route('/api/bulk/update-schedule', methods=['POST'])
@require_auth
def bulk_update_schedule():
    """
    Update schedule date for multiple calls and automatically set to WAITING ON CUSTOMER.

    Request body:
    {
        "call_numbers": ["ABC123", "DEF456"],
        "schedule_date": "20260130",
        "notes": "Optional rescheduling notes"
    }
    """
    try:
        data = request.get_json()
        call_numbers = data.get('call_numbers', [])
        schedule_date = data.get('schedule_date', '')
        notes = data.get('notes', '')

        if not call_numbers:
            return jsonify({
                'success': False,
                'error': 'No call numbers provided'
            }), 400

        if not schedule_date:
            return jsonify({
                'success': False,
                'error': 'Schedule date is required'
            }), 400

        client = get_client_from_session()

        success_count = 0
        failed_calls = []

        for call_number in call_numbers:
            try:
                # Build update request with schedule date and WAITING ON CUSTOMER substatus
                update_data = {
                    'CallNumber': call_number,
                    'ScheduleDate': schedule_date,
                    'CallStatus': 'ACCEPTED',
                    'SPCallStatusID': '3',
                    'SPCallSubStatusID': 'ACT35'  # WAITING ON CUSTOMER
                }

                # Add notes if provided
                if notes:
                    update_data['Remarks'] = {
                        'NotesDate': datetime.now().strftime('%Y%m%d %H:%M:%S'),
                        'Notes': f'Rescheduled to {schedule_date}. {notes}',
                        'AddedBy': session.get('credentials', {}).get('user_id', 'API')
                    }

                result = client.update_call_status(
                    call_number=call_number,
                    status='ACCEPTED',
                    substatus='ACT35',
                    additional_data=update_data
                )

                if result.get('success'):
                    success_count += 1
                else:
                    failed_calls.append({
                        'call_number': call_number,
                        'error': result.get('error', 'Unknown error')
                    })

            except Exception as e:
                logger.error(f'Error updating schedule for call {call_number}: {e}')
                failed_calls.append({
                    'call_number': call_number,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'data': {
                'success_count': success_count,
                'failed_count': len(failed_calls),
                'total': len(call_numbers),
                'failed_calls': failed_calls
            },
            'message': f'Rescheduled {success_count} of {len(call_numbers)} calls'
        })

    except Exception as e:
        logger.error(f'Bulk schedule update error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bulk_bp.route('/api/bulk/add-notes', methods=['POST'])
@require_auth
def bulk_add_notes():
    """
    Add notes to multiple calls (e.g., ticket numbers).

    Request body:
    {
        "call_numbers": ["ABC123", "DEF456"],
        "notes": "70590"
    }
    """
    try:
        data = request.get_json()
        call_numbers = data.get('call_numbers', [])
        notes = data.get('notes', '')

        if not call_numbers:
            return jsonify({
                'success': False,
                'error': 'No call numbers provided'
            }), 400

        if not notes:
            return jsonify({
                'success': False,
                'error': 'Notes are required'
            }), 400

        client = get_client_from_session()

        success_count = 0
        failed_calls = []

        for call_number in call_numbers:
            try:
                # Build update request with just notes (no status change)
                update_data = {
                    'CallNumber': call_number,
                    'Remarks': {
                        'NotesDate': datetime.now().strftime('%Y%m%d %H:%M:%S'),
                        'Notes': notes,
                        'AddedBy': session.get('credentials', {}).get('user_id', 'API')
                    }
                }

                result = client.update_call_status(
                    call_number=call_number,
                    status=None,  # Don't change status
                    substatus=None,  # Don't change substatus
                    additional_data=update_data
                )

                if result.get('success'):
                    success_count += 1
                else:
                    failed_calls.append({
                        'call_number': call_number,
                        'error': result.get('error', 'Unknown error')
                    })

            except Exception as e:
                logger.error(f'Error adding notes to call {call_number}: {e}')
                failed_calls.append({
                    'call_number': call_number,
                    'error': str(e)
                })

        return jsonify({
            'success': True,
            'data': {
                'success_count': success_count,
                'failed_count': len(failed_calls),
                'total': len(call_numbers),
                'failed_calls': failed_calls
            },
            'message': f'Added notes to {success_count} of {len(call_numbers)} calls'
        })

    except Exception as e:
        logger.error(f'Bulk add notes error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bulk_bp.route('/api/generate-sms', methods=['POST'])
@require_auth
def generate_sms():
    """
    Generate SMS message for a call with customizable fields.

    Request body:
    {
        "customer_name": "John Smith",
        "product": "Dishwasher",
        "dealer_invoice": "70590" (optional)
    }
    """
    try:
        data = request.get_json()
        customer_name = data.get('customer_name', 'Customer')
        product = data.get('product', 'appliance')
        dealer_invoice = data.get('dealer_invoice', '')

        # Build SMS message
        sms_parts = [
            f"This is Metro TV and Appliance. To schedule your {product} service, we need 4 items to start your ticket."
        ]

        # Add invoice if provided
        if dealer_invoice:
            sms_parts.append(f"{dealer_invoice}")
            sms_parts.append("")  # Blank line

        sms_parts.extend([
            f"Hello {customer_name}, please reply to this text with:",
            "",
            "1. PHOTO of the Model/Serial Tag (Must be a clear picture directly on the appliance, not from paperwork)",
            "",
            "2. PHOTO of the Problem (If the problem isn't visible, please send a photo of the appliance's location/environment)",
            "",
            "3. Problem Description (Please be as descriptive as possible)",
            "",
            "4. Your Address (Full street address and zip code)",
            "",
            "IMPORTANT: Your Appointment",
            "Your warranty company provides an initial request date, but this is NOT a confirmed appointment.",
            "",
            "Your warranty company requires that your ticket first go through our tech review. We use this review to pre-order parts through your warranty company. This process is required by them to reduce turnaround times for claims and attempt a one-visit repair.",
            "",
            "We will contact you directly to schedule your CONFIRMED appointment date."
        ])

        sms_message = "\n".join(sms_parts)

        return jsonify({
            'success': True,
            'data': {
                'sms_message': sms_message,
                'character_count': len(sms_message)
            }
        })

    except Exception as e:
        logger.error(f'SMS generation error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bulk_bp.route('/api/substatuses', methods=['GET'])
@require_auth
def get_substatuses():
    """Get all available call substatuses."""
    return jsonify({
        'success': True,
        'data': {
            'substatuses': [
                {'id': k, 'name': v['name'], 'status': v['status']}
                for k, v in SUBSTATUS_MAPPING.items()
            ]
        }
    })


# Substatus mapping from documentation (Section 14.4)
SUBSTATUS_MAPPING = {
    'ACT01': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'ACCEPTED'},
    'ACT38': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'WAITING ON TECH SUPPORT'},
    'ACT03': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'APPOINTMENT SCHEDULED'},
    'ACT04': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'AUTHORIZATION DENIED'},
    'ACT05': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'AUTHORIZATION RECEIVED'},
    'ACT06': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'AUTHORIZATION REQ. SUBMIT'},
    'ACT10': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'CUSTOMER CONTACTED'},
    'ACT11': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'EN ROUTE'},
    'ACT14': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'ON SITE'},
    'ACT15': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'ORDER PARTS'},
    'ACT16': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'PARTS ON BACKORDER'},
    'ACT17': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'PARTS ORDERED'},
    'ACT18': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'PARTS RECEIVED'},
    'ACT28': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'RESCHEDULED'},
    'ACT29': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'RESCHEDULED- CUSTOMER REQUEST'},
    'ACT30': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'RESCHEDULED- OTHER'},
    'ACT33': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'TRIAGE'},
    'ACT34': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'WAITING ON AUTHORIZATION'},
    'ACT35': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'WAITING ON CUSTOMER'},
    'ACT36': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'WAITING ON PARTS'},
    'ACT37': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'WAITING ON PRODUCT'},
    'ACT02': {'status': 'ACCEPTED', 'status_id': '3', 'name': 'APPOINTMENT CONFIRMED'},
}
