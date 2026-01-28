"""
ServiceDispatch Flask Application Factory

This module provides the application factory pattern for creating Flask
application instances. The factory allows for flexible configuration
and testing by creating new app instances with different settings.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from .config import get_config
from .extensions import init_extensions, db


def create_app(config_name: str = None) -> Flask:
    """
    Create and configure a Flask application instance.

    Uses the application factory pattern to allow for flexible configuration
    and testing. The function initializes extensions, registers blueprints,
    and sets up logging.

    Args:
        config_name: Configuration environment name ('development', 'staging',
                    'production', 'testing'). If None, uses FLASK_ENV
                    environment variable or defaults to 'development'.

    Returns:
        Configured Flask application instance
    """
    app = Flask(
        __name__,
        static_folder='../static',
        template_folder='templates'
    )

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize extensions
    init_extensions(app)

    # Configure logging
    configure_logging(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Create database tables if they don't exist
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from . import models  # noqa: F401
        db.create_all()

    app.logger.info(f'ServiceDispatch application started in {config_name or "default"} mode')

    return app


def configure_logging(app: Flask) -> None:
    """
    Configure application logging.

    Sets up both file and console logging handlers with appropriate
    formatters and log levels based on configuration.

    Args:
        app: Flask application instance
    """
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_file = app.config.get('LOG_FILE', 'servicepower_debug.log')

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    # Configure app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # Suppress noisy loggers in production
    if not app.debug:
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.

    Imports and registers API and view blueprints with appropriate
    URL prefixes.

    Args:
        app: Flask application instance
    """
    # API blueprints
    from .api.auth import auth_bp
    from .api.calls import calls_bp
    from .api.parts import parts_bp
    from .api.export import export_bp
    from .api.imports import imports_bp
    from .api.bulk_operations import bulk_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(calls_bp, url_prefix='/api')
    app.register_blueprint(parts_bp, url_prefix='/api')
    app.register_blueprint(export_bp, url_prefix='/api')
    app.register_blueprint(imports_bp, url_prefix='/api')
    app.register_blueprint(bulk_bp)  # No prefix - routes already include /api/bulk/

    # View blueprints
    from .views.main import main_bp

    app.register_blueprint(main_bp)


def register_error_handlers(app: Flask) -> None:
    """
    Register application error handlers.

    Sets up handlers for common HTTP errors to return appropriate
    JSON or HTML responses based on request type.

    Args:
        app: Flask application instance
    """
    from flask import jsonify, render_template, request

    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Bad Request',
                'message': str(error.description)
            }), 400
        return render_template('pages/error.html', error=error), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Authentication required'
            }), 401
        return render_template('pages/error.html', error=error), 401

    @app.errorhandler(404)
    def not_found(error):
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        return render_template('pages/error.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Server Error: {error}')
        db.session.rollback()
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            }), 500
        return render_template('pages/error.html', error=error), 500
