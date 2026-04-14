import os
import pytest

os.environ['CONFIG'] = 'Test'

import pwnedadmin.config
pwnedadmin.config.Test.SQLALCHEMY_DATABASE_URI = 'sqlite://'

from pwnedadmin import create_app
from pwnedadmin.extensions import db as _db
from pwnedadmin.models import Config, Email


CONFIG_ENTRIES = [
    {'name': 'CSRF_PROTECT', 'description': 'Profile CSRF Protection (PwnedHub)', 'type': 'security control', 'value': True},
    {'name': 'OSCI_PROTECT', 'description': 'Tools OSCI Protection (PwnedHub)', 'type': 'security control', 'value': False},
    {'name': 'SQLI_PROTECT', 'description': 'Login SQLi Protection (PwnedHub)', 'type': 'security control', 'value': False},
    {'name': 'CSP_PROTECT', 'description': 'Content Security Policy (PwnedHub)', 'type': 'security control', 'value': False},
    {'name': 'CORS_RESTRICT', 'description': 'Restricted CORS (PwnedAPI)', 'type': 'security control', 'value': True},
    {'name': 'JWT_VERIFY', 'description': 'Verify JWT Signatures (PwnedAPI)', 'type': 'security control', 'value': True},
    {'name': 'JWT_ENCRYPT', 'description': 'Encrypt JWTs (PwnedAPI)', 'type': 'security control', 'value': False},
    {'name': 'BEARER_AUTH_ENABLE', 'description': 'Bearer Token Authentication (PwnedAPI)', 'type': 'feature', 'value': True},
    {'name': 'OIDC_ENABLE', 'description': 'OpenID Connect Authentication (PwnedHub)', 'type': 'feature', 'value': False},
    {'name': 'SSO_ENABLE', 'description': 'SSO Authentication (PwnedHub)', 'type': 'feature', 'value': False},
    {'name': 'OOB_RESET_ENABLE', 'description': 'Out-of-Band Password Reset (PwnedHub)', 'type': 'feature', 'value': False},
    {'name': 'CTF_MODE', 'description': 'CTF Mode (Warning: Disables this interface!)', 'type': 'feature', 'value': False},
]


@pytest.fixture(scope='session')
def app():
    """Create and configure the Flask application for testing."""
    test_app = create_app()

    test_app.config['TESTING'] = True
    test_app.config['SERVER_NAME'] = 'localhost'

    yield test_app


@pytest.fixture(scope='function')
def db_session(app):
    """Set up and tear down all database tables with seed data for each test."""
    with app.app_context():
        _db.create_all()

        for entry in CONFIG_ENTRIES:
            config = Config(
                name=entry['name'],
                description=entry['description'],
                type=entry['type'],
                value=entry['value'],
            )
            _db.session.add(config)
        _db.session.commit()

        yield _db.session

        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db_session):
    """Provide a Flask test client with the database session active."""
    with app.app_context():
        with app.test_client() as test_client:
            yield test_client
