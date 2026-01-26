"""
Parts API Blueprint

Provides endpoints for parts history, analytics, and recommendations.
"""

import logging
from flask import Blueprint, jsonify, request

from ..services import PartsAnalyticsService
from .auth import require_auth

logger = logging.getLogger(__name__)

parts_bp = Blueprint('parts', __name__)


@parts_bp.route('/parts/history', methods=['POST'])
@require_auth
def get_parts_history():
    """
    Get parts usage history with optional search filtering.

    Expects JSON body:
    {
        "search": "string" (optional)
    }

    Returns:
    {
        "success": bool,
        "parts": [...],
        "count": int,
        "total_records": int
    }
    """
    data = request.get_json() or {}
    search_term = data.get('search', '').lower()

    try:
        service = PartsAnalyticsService()
        parts, total = service.get_parts_history(
            search_term=search_term if search_term else None,
            limit=500
        )

        return jsonify({
            'success': True,
            'parts': parts,
            'count': len(parts),
            'total_records': total
        })

    except Exception as e:
        logger.error(f'Error fetching parts history: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'parts': [],
            'total_records': 0
        }), 500


@parts_bp.route('/parts/analytics', methods=['POST'])
@require_auth
def get_parts_analytics():
    """
    Get advanced analytics from parts history.

    Expects JSON body:
    {
        "make": "string" (optional),
        "model": "string" (optional),
        "problem": "string" (optional)
    }

    Returns:
    {
        "success": bool,
        "analytics": {
            "total_records": int,
            "filtered_records": int,
            "most_common_parts": [...],
            "common_problems": [...],
            "unique_makes": int,
            "unique_models": int
        },
        "recommendations": [...]
    }
    """
    data = request.get_json() or {}
    make = data.get('make', '').upper() if data.get('make') else None
    model = data.get('model', '').upper() if data.get('model') else None
    problem = data.get('problem', '').lower() if data.get('problem') else None

    try:
        service = PartsAnalyticsService()
        analytics = service.get_parts_analytics(
            make=make,
            model=model,
            problem=problem
        )

        # Get recommendations if problem was specified
        recommendations = []
        if problem:
            rec_result = service.get_recommendations(
                make=make,
                model=model,
                problem=problem
            )
            recommendations = rec_result.get('recommendations', [])

        return jsonify({
            'success': True,
            'analytics': analytics,
            'recommendations': recommendations
        })

    except Exception as e:
        logger.error(f'Error getting parts analytics: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'analytics': {},
            'recommendations': []
        }), 500


@parts_bp.route('/recommendations', methods=['POST'])
@require_auth
def get_recommendations():
    """
    Get AI-like recommendations based on historical data.

    Expects JSON body:
    {
        "make": "string" (optional),
        "model": "string" (optional),
        "product_type": "string" (optional),
        "problem": "string" (optional)
    }

    Returns:
    {
        "success": bool,
        "recommendations": [
            {
                "part_number": "string",
                "description": "string",
                "frequency": int,
                "success_rate": "string",
                "sample_size": int
            },
            ...
        ],
        "confidence": "high|medium|low|none",
        "filters_applied": [...],
        "total_matches": int
    }
    """
    data = request.get_json() or {}
    make = data.get('make', '').upper() if data.get('make') else None
    model = data.get('model', '').upper() if data.get('model') else None
    product_type = data.get('product_type', '').upper() if data.get('product_type') else None
    problem = data.get('problem', '').lower() if data.get('problem') else None

    try:
        service = PartsAnalyticsService()
        result = service.get_recommendations(
            make=make,
            model=model,
            product_type=product_type,
            problem=problem
        )

        return jsonify({
            'success': True,
            **result
        })

    except Exception as e:
        logger.error(f'Error getting recommendations: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendations': [],
            'confidence': 'error'
        }), 500


@parts_bp.route('/customer/analytics', methods=['POST'])
@require_auth
def get_customer_analytics():
    """
    Get customer database analytics.

    Returns:
    {
        "success": bool,
        "analytics": {
            "total_customers": int,
            "unique_cities": int,
            "unique_zips": int,
            "top_cities": [...],
            "top_makes": [...],
            "top_product_types": [...]
        }
    }
    """
    try:
        service = PartsAnalyticsService()
        analytics = service.get_customer_analytics()

        return jsonify({
            'success': True,
            'analytics': analytics
        })

    except Exception as e:
        logger.error(f'Error getting customer analytics: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'analytics': {}
        }), 500


@parts_bp.route('/parts/search', methods=['GET'])
@require_auth
def search_parts():
    """
    Search parts by part number or description.

    Query params:
        q: Search query
        limit: Max results (default 50)

    Returns:
    {
        "success": bool,
        "parts": [...],
        "count": int
    }
    """
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 50)), 500)

    if not query:
        return jsonify({
            'success': False,
            'error': 'Search query is required',
            'parts': []
        }), 400

    try:
        service = PartsAnalyticsService()
        parts, _ = service.get_parts_history(
            search_term=query,
            limit=limit
        )

        return jsonify({
            'success': True,
            'parts': parts,
            'count': len(parts)
        })

    except Exception as e:
        logger.error(f'Error searching parts: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'parts': []
        }), 500


@parts_bp.route('/parts/<part_num>/history', methods=['GET'])
@require_auth
def get_part_history(part_num: str):
    """
    Get usage history for a specific part number.

    Returns:
    {
        "success": bool,
        "part_number": "string",
        "history": [...],
        "total_used": int
    }
    """
    try:
        from ..models import PartsHistory

        records = PartsHistory.query.filter(
            PartsHistory.part_num.ilike(f'%{part_num}%')
        ).order_by(PartsHistory.created_at.desc()).limit(100).all()

        history = [r.to_dict() for r in records]
        total_used = sum(r.quantity or 1 for r in records)

        return jsonify({
            'success': True,
            'part_number': part_num,
            'history': history,
            'total_used': total_used,
            'usage_count': len(records)
        })

    except Exception as e:
        logger.error(f'Error getting history for part {part_num}: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'history': []
        }), 500
