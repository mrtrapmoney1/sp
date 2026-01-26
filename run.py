#!/usr/bin/env python3
"""
ServiceDispatch Application Entry Point

This module serves as the entry point for running the ServiceDispatch
Flask application. It creates an application instance using the factory
pattern and starts the development server.

Usage:
    python run.py                    # Development mode (default)
    python run.py --env production   # Production mode
    python run.py --port 8000        # Custom port

Environment Variables:
    FLASK_ENV: Set to 'production' for production mode
    SECRET_KEY: Override the default secret key
    DATABASE_URL: PostgreSQL connection string
"""

import os
import sys
import argparse

# Load .env file before importing app
from dotenv import load_dotenv
load_dotenv()

from app import create_app


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run the ServiceDispatch application'
    )
    parser.add_argument(
        '--env', '-e',
        choices=['development', 'staging', 'production', 'testing'],
        default=os.getenv('FLASK_ENV', 'development'),
        help='Environment to run in (default: development)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=int(os.getenv('PORT', 5000)),
        help='Port to run on (default: 5000)'
    )
    parser.add_argument(
        '--host', '-H',
        default=os.getenv('HOST', '127.0.0.1'),
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=None,
        help='Enable debug mode (overrides environment setting)'
    )
    return parser.parse_args()


def main():
    """Create and run the Flask application."""
    args = parse_args()

    # Print startup banner
    print("\n" + "=" * 60)
    print("ServiceDispatch - Field Service Management")
    print("=" * 60)

    # Create application
    app = create_app(args.env)

    # Override debug if specified
    if args.debug is not None:
        app.debug = args.debug

    # Print configuration info
    print(f"\nEnvironment: {args.env}")
    print(f"Debug mode: {'ON' if app.debug else 'OFF'}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')[:50]}...")
    print(f"\nStarting server at http://{args.host}:{args.port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    # Run the application
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=app.debug,
            use_reloader=app.debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)


if __name__ == '__main__':
    main()
