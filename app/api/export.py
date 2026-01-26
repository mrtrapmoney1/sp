"""
Export API Blueprint

Provides endpoints for exporting data to DBF format for
Lotus Approach compatibility.
"""

import io
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, session

from ..services import DBFExportService
from .auth import require_auth

logger = logging.getLogger(__name__)

export_bp = Blueprint('export', __name__)


@export_bp.route('/export/dbf', methods=['POST'])
@require_auth
def export_dbf():
    """
    Export selected calls as DBF file for Lotus import.

    Expects JSON body:
    {
        "calls": [
            {
                "invoice": "string",
                "CallNumber": "string",
                "ConsumerInfo_ConsumerLastName": "string",
                ...
            },
            ...
        ]
    }

    Returns:
        DBF file download
    """
    data = request.get_json() or {}
    selected_calls = data.get('calls', [])

    if not selected_calls:
        return jsonify({
            'success': False,
            'error': 'No calls selected'
        }), 400

    try:
        service = DBFExportService()

        # Map calls to Lotus format and create DBF
        dbf_data, filename = service.export_calls(selected_calls)

        if not dbf_data:
            return jsonify({
                'success': False,
                'error': 'No valid records to export'
            }), 400

        logger.info(f'Exported {len(selected_calls)} calls to {filename}')

        return send_file(
            io.BytesIO(dbf_data),
            mimetype='application/x-dbase',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f'Error exporting to DBF: {e}')
        return jsonify({
            'success': False,
            'error': f'Export error: {str(e)}'
        }), 500


@export_bp.route('/export/session', methods=['POST'])
@require_auth
def export_session_calls():
    """
    Export calls from session (previously fetched) as DBF file.

    Expects JSON body:
    {
        "invoice_start": int (optional)
    }

    Returns:
        DBF file download
    """
    calls = session.get('calls', [])

    if not calls:
        return jsonify({
            'success': False,
            'error': 'No calls in session. Please fetch calls first.'
        }), 400

    data = request.get_json() or {}
    invoice_start = data.get('invoice_start')

    try:
        service = DBFExportService()
        dbf_data, filename = service.export_calls(calls, invoice_start=invoice_start)

        if not dbf_data:
            return jsonify({
                'success': False,
                'error': 'No valid records to export'
            }), 400

        logger.info(f'Exported {len(calls)} session calls to {filename}')

        return send_file(
            io.BytesIO(dbf_data),
            mimetype='application/x-dbase',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f'Error exporting session calls: {e}')
        return jsonify({
            'success': False,
            'error': f'Export error: {str(e)}'
        }), 500


@export_bp.route('/export/tickets', methods=['POST'])
@require_auth
def export_tickets():
    """
    Export tickets from database as DBF file.

    Expects JSON body:
    {
        "ticket_ids": [int, ...] (optional - if not provided, exports all)
        "from_date": "YYYY-MM-DD" (optional),
        "to_date": "YYYY-MM-DD" (optional)
    }

    Returns:
        DBF file download
    """
    data = request.get_json() or {}
    ticket_ids = data.get('ticket_ids', [])
    from_date = data.get('from_date')
    to_date = data.get('to_date')

    try:
        from ..models import Ticket

        query = Ticket.query

        if ticket_ids:
            query = query.filter(Ticket.id.in_(ticket_ids))

        if from_date:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Ticket.date_in >= from_dt)

        if to_date:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(Ticket.date_in <= to_dt)

        tickets = query.order_by(Ticket.date_in.desc()).all()

        if not tickets:
            return jsonify({
                'success': False,
                'error': 'No tickets found matching criteria'
            }), 404

        service = DBFExportService()
        dbf_data, filename = service.export_tickets(tickets)

        logger.info(f'Exported {len(tickets)} tickets to {filename}')

        return send_file(
            io.BytesIO(dbf_data),
            mimetype='application/x-dbase',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f'Error exporting tickets: {e}')
        return jsonify({
            'success': False,
            'error': f'Export error: {str(e)}'
        }), 500


@export_bp.route('/export/preview', methods=['POST'])
@require_auth
def preview_export():
    """
    Preview export data without generating file.

    Expects JSON body:
    {
        "calls": [...] (optional - uses session if not provided)
    }

    Returns:
    {
        "success": bool,
        "preview": [
            {
                "INVOICE": "string",
                "LASTNAME": "string",
                ...
            },
            ...
        ],
        "count": int
    }
    """
    data = request.get_json() or {}
    calls = data.get('calls') or session.get('calls', [])

    if not calls:
        return jsonify({
            'success': False,
            'error': 'No calls to preview',
            'preview': []
        }), 400

    try:
        service = DBFExportService()

        # Generate preview (first 10 records)
        preview_calls = calls[:10]
        preview_records = []

        invoice_start = int(datetime.now().strftime('%y%m%d')) * 100
        for i, call in enumerate(preview_calls):
            invoice = str(invoice_start + i)
            lotus_record = service.map_servicepower_call(call, invoice)
            preview_records.append(lotus_record)

        return jsonify({
            'success': True,
            'preview': preview_records,
            'total_count': len(calls),
            'preview_count': len(preview_records)
        })

    except Exception as e:
        logger.error(f'Error generating export preview: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'preview': []
        }), 500
