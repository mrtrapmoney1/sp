"""
Main Views Blueprint

Provides page routes for the web application interface.
Uses Jinja2 templates with HTMX for dynamic content.
"""

import logging
from flask import Blueprint, render_template, redirect, session, url_for, request

from ..config import Config

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


# ServicePower environment mapping for templates
ENVIRONMENTS = Config.SERVICEPOWER_ENVIRONMENTS


def login_required(func):
    """Decorator to require login for page views."""
    from functools import wraps

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'credentials' not in session:
            return redirect(url_for('main.login'))
        return func(*args, **kwargs)

    return decorated_function


@main_bp.route('/')
def login():
    """Render login page."""
    # If already logged in, redirect to dashboard
    if 'credentials' in session:
        return redirect(url_for('main.dashboard'))

    return render_template(
        'pages/login.html',
        environments=ENVIRONMENTS
    )


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Render main dashboard."""
    return render_template(
        'pages/index.html',
        environments=ENVIRONMENTS,
        active_page='dashboard'
    )


@main_bp.route('/tickets')
@login_required
def tickets():
    """Render ticket creator page."""
    return render_template(
        'pages/tickets.html',
        environments=ENVIRONMENTS,
        active_page='tickets'
    )


@main_bp.route('/map')
@login_required
def map_view():
    """Render map visualization page."""
    return render_template(
        'pages/map.html',
        environments=ENVIRONMENTS,
        active_page='map'
    )


@main_bp.route('/analytics')
@login_required
def analytics():
    """Render analytics dashboard page."""
    return render_template(
        'pages/analytics.html',
        environments=ENVIRONMENTS,
        active_page='analytics'
    )


@main_bp.route('/diagnosis')
@login_required
def diagnosis():
    """Render enhanced diagnosis helper page."""
    return render_template(
        'pages/diagnosis_enhanced.html',
        environments=ENVIRONMENTS,
        active_page='diagnosis'
    )


@main_bp.route('/parts')
@login_required
def parts():
    """Render parts lookup page."""
    return render_template(
        'pages/parts.html',
        environments=ENVIRONMENTS,
        active_page='parts'
    )


@main_bp.route('/import')
@login_required
def import_calls():
    """Render import page for PDFs and Excel files."""
    return render_template(
        'pages/import.html',
        environments=ENVIRONMENTS,
        active_page='import'
    )


# HTMX partial routes for dynamic content
@main_bp.route('/partials/calls-table')
@login_required
def calls_table_partial():
    """Render calls table partial for HTMX updates."""
    calls = session.get('calls', [])
    return render_template(
        'components/calls_table.html',
        calls=calls
    )


@main_bp.route('/partials/call-detail/<call_number>')
@login_required
def call_detail_partial(call_number: str):
    """Render call detail partial for HTMX modal."""
    calls = session.get('calls', [])
    call = next(
        (c for c in calls if c.get('CallNumber') == call_number or c.get('call_number') == call_number),
        None
    )
    if not call:
        return '<div class="alert alert-danger">Call not found</div>', 404

    return render_template(
        'components/call_detail.html',
        call=call
    )


@main_bp.route('/partials/parts-results')
@login_required
def parts_results_partial():
    """Render parts search results partial for HTMX updates."""
    search = request.args.get('search', '')
    # Results will be fetched via JavaScript
    return render_template(
        'components/parts_results.html',
        search=search
    )


@main_bp.route('/partials/analytics-charts')
@login_required
def analytics_charts_partial():
    """Render analytics charts partial for HTMX updates."""
    return render_template('components/analytics_charts.html')


# Error pages
@main_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return {'success': False, 'error': 'Not found'}, 404
    return render_template('pages/error.html', error=error), 404


@main_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f'Internal error: {error}')
    if request.path.startswith('/api/'):
        return {'success': False, 'error': 'Internal server error'}, 500
    return render_template('pages/error.html', error=error), 500
