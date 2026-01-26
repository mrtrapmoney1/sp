"""
Flask Extensions Module

Initializes and exports Flask extensions for use throughout the application.
Extensions are initialized without the app instance and bound later using
the init_app pattern for flexibility.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# SQLAlchemy database instance
# Used for all database operations via ORM
db = SQLAlchemy()

# Flask-Migrate instance for database migrations
# Handles schema changes and version control for the database
migrate = Migrate()


def init_extensions(app):
    """
    Initialize all Flask extensions with the application instance.

    This function should be called during application factory setup
    to bind extensions to the Flask app.

    Args:
        app: Flask application instance
    """
    db.init_app(app)
    migrate.init_app(app, db)

    # Register teardown to ensure connections are cleaned up
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
