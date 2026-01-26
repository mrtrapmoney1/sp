"""
Application Configuration Module

Provides environment-specific configuration for the ServiceDispatch application.
Supports development, staging, and production environments with different
database connections and ServicePower API endpoints.
"""

import os
from typing import Dict


class Config:
    """Base configuration class with common settings."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    SESSION_TYPE = 'filesystem'

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # ServicePower API endpoints
    SERVICEPOWER_ENVIRONMENTS: Dict[str, str] = {
        'staging_na': 'https://fssstag.servicepower.com/sms/services/SPDService',
        'staging_eu': 'https://fss-stg.hostedservicepower.eu/sms/services/SPDService',
        'production_na': 'https://fss.servicepower.com/sms/services/SPDService',
        'production_eu': 'https://fss.servicepower.eu/sms/services/SPDService',
    }
    SERVICEPOWER_NAMESPACE = 'urn:SPDServicerService'
    SERVICEPOWER_WSDL = None  # Will use zeep with direct URL

    # Lotus/DBF file paths
    LOTUS_DATABASE_PATH = os.environ.get('LOTUS_DATABASE_PATH') or 'data/lotus-database'
    LOTUS_NETWORK_PATH = os.environ.get('LOTUS_NETWORK_PATH') or 'Y:\\Lotus'

    # DBF field mappings for export (matches Lotus CUSTDATA.DBF structure)
    DBF_FIELDS = [
        ('INVOICE', 'N', 5, 0),
        ('LASTNAME', 'C', 25, 0),
        ('FIRSTNAME', 'C', 15, 0),
        ('ADDRESS', 'C', 25, 0),
        ('CITY', 'C', 30, 0),
        ('STATE', 'C', 2, 0),
        ('ZIP', 'C', 5, 0),
        ('PHONE', 'C', 12, 0),
        ('PHONE2', 'C', 12, 0),
        ('LOCATION', 'C', 15, 0),
        ('SERVICEREQ', 'C', 250, 0),
        ('MAKE', 'C', 15, 0),
        ('TYP', 'C', 15, 0),
        ('MODEL', 'C', 20, 0),
        ('SERIAL', 'C', 26, 0),
        ('DATEIN', 'D', 8, 0),
        ('DATEPUR', 'D', 8, 0),
        ('BTADDRESS', 'C', 30, 0),
        ('ACCESSOR', 'C', 150, 0),
        ('TICLOC', 'C', 25, 0),
        ('DLRINVOICE', 'C', 17, 0),
    ]

    # Warranty accessor mapping
    WARRANTY_ACCESSOR_MAP = {
        'IW': 'If less than $550 then no approval is needed',
        'SC': '$140',
    }

    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'servicepower_debug.log'


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False

    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///servicedispatch_dev.db'

    # Default to staging API for development
    SERVICEPOWER_DEFAULT_ENV = 'staging_na'

    LOG_LEVEL = 'DEBUG'


class StagingConfig(Config):
    """Staging environment configuration."""

    DEBUG = False
    TESTING = False

    # PostgreSQL for staging
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://servicedispatch:password@localhost:5432/servicedispatch_staging'

    SERVICEPOWER_DEFAULT_ENV = 'staging_na'

    LOG_LEVEL = 'INFO'


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # PostgreSQL for production - require environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///servicedispatch.db'

    # Additional production safety settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    SERVICEPOWER_DEFAULT_ENV = 'production_na'

    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG = True
    TESTING = True

    # In-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    SERVICEPOWER_DEFAULT_ENV = 'staging_na'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    LOG_LEVEL = 'DEBUG'


# Configuration mapping by environment name
config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config(env_name: str = None) -> Config:
    """
    Get configuration class for the specified environment.

    Args:
        env_name: Environment name ('development', 'staging', 'production', 'testing')
                 If None, uses FLASK_ENV environment variable or defaults to 'development'

    Returns:
        Configuration class for the specified environment
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(env_name, config['default'])
