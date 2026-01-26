"""
Authentication API Blueprint

Provides endpoints for user authentication with ServicePower API.
Stores credentials in session for subsequent API calls.
"""

import logging
from flask import Blueprint, jsonify, request, session, current_app

from ..services import ServicePowerClient

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with ServicePower.

    Expects JSON body:
    {
        "user_id": "string",
        "password": "string",
        "servicer_account": "string" (optional),
        "environment": "string" (optional, default: production_na)
    }

    Returns:
    {
        "success": bool,
        "message": "string",
        "error": "string" (on failure)
    }
    """
    data = request.get_json() or {}

    user_id = data.get('user_id', '').strip()
    password = data.get('password', '')
    servicer_account = data.get('servicer_account', '').strip()
    environment = data.get('environment', 'production_na')

    logger.info(f'Login attempt: user={user_id}, environment={environment}')

    # Validate required fields
    if not user_id or not password:
        logger.warning('Login failed: missing credentials')
        return jsonify({
            'success': False,
            'error': 'User ID and Password are required'
        }), 400

    # Test connection with ServicePower
    try:
        client = ServicePowerClient(
            user_id=user_id,
            password=password,
            servicer_account=servicer_account,
            environment=environment
        )

        # Fetch calls with small date range to verify credentials
        success, calls, message = client.get_calls(days=1)

        # Check for authentication errors
        auth_error_keywords = [
            'authentication', 'unauthorized', 'invalid', 'credential',
            'password', 'user', 'access denied', 'login', 'SP002', 'SP003', 'SP004', 'SP005'
        ]
        message_lower = message.lower()
        is_auth_error = any(keyword in message_lower for keyword in auth_error_keywords)

        if not success:
            logger.warning(f'Login failed for user {user_id}: {message}')
            return jsonify({
                'success': False,
                'error': message
            }), 401

        if is_auth_error:
            logger.warning(f'Login failed (auth error) for user {user_id}: {message}')
            return jsonify({
                'success': False,
                'error': message
            }), 401

        # Store credentials in session
        session['credentials'] = {
            'user_id': user_id,
            'password': password,
            'servicer_account': servicer_account,
            'environment': environment,
        }

        logger.info(f'Login successful for user {user_id}')
        return jsonify({
            'success': True,
            'message': f'Login successful. Found {len(calls)} calls in last day.',
            'data': {
                'user_id': user_id,
                'environment': environment,
                'calls_count': len(calls),
            }
        })

    except Exception as e:
        logger.error(f'Login exception for user {user_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': f'Connection error: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Clear user session.

    Returns:
    {
        "success": true,
        "message": "Logged out successfully"
    }
    """
    session.clear()
    logger.info('User logged out')
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@auth_bp.route('/session', methods=['GET'])
def check_session():
    """
    Check if user has an active session.

    Returns:
    {
        "success": bool,
        "authenticated": bool,
        "data": {
            "user_id": "string",
            "environment": "string"
        } (if authenticated)
    }
    """
    creds = session.get('credentials', {})

    if not creds.get('user_id'):
        return jsonify({
            'success': True,
            'authenticated': False
        })

    return jsonify({
        'success': True,
        'authenticated': True,
        'data': {
            'user_id': creds.get('user_id'),
            'environment': creds.get('environment'),
            'servicer_account': creds.get('servicer_account'),
        }
    })


def get_client_from_session() -> ServicePowerClient:
    """
    Create a ServicePowerClient from session credentials.

    Returns:
        ServicePowerClient instance

    Raises:
        ValueError: If not authenticated
    """
    creds = session.get('credentials', {})

    if not creds.get('user_id') or not creds.get('password'):
        raise ValueError('Not authenticated. Please log in again.')

    return ServicePowerClient(
        user_id=creds['user_id'],
        password=creds['password'],
        servicer_account=creds.get('servicer_account', ''),
        environment=creds.get('environment', 'production_na')
    )


def require_auth(func):
    """
    Decorator to require authentication for an endpoint.

    Usage:
        @require_auth
        def my_endpoint():
            ...
    """
    from functools import wraps

    @wraps(func)
    def decorated_function(*args, **kwargs):
        creds = session.get('credentials', {})
        if not creds.get('user_id') or not creds.get('password'):
            return jsonify({
                'success': False,
                'error': 'Not authenticated. Please log in again.'
            }), 401
        return func(*args, **kwargs)

    return decorated_function
