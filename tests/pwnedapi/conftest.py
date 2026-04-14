import os
import pytest
from unittest.mock import MagicMock, patch

# Set config before any app imports
os.environ['CONFIG'] = 'Test'

# Patch config at module level so pwnedapi is importable during test collection
import pwnedapi.config
pwnedapi.config.Test.SQLALCHEMY_DATABASE_URI = 'sqlite://'
pwnedapi.config.Test.SQLALCHEMY_BINDS = {'admin': 'sqlite://'}


@pytest.fixture(scope='session')
def app():
    """Create the Flask application for testing."""
    with patch('pwnedapi.Redis') as mock_redis_cls, \
         patch('pwnedapi.rq') as mock_rq:

        mock_redis_cls.from_url.return_value = MagicMock()
        mock_rq.Queue.return_value = MagicMock()

        from pwnedapi import create_app
        app, socketio = create_app()

    from pwnedapi.extensions import db as _db
    from pwnedapi.models import Config, Room

    # Ensure mocks are on the app for tests that need them
    app.redis = MagicMock()
    app.api_task_queue = MagicMock()
    app.bot_task_queue = MagicMock()

    # Create all tables and seed required data
    with app.app_context():
        _db.create_all()

        # Seed Config entries (admin bind) — must match database/init/04-pwnedhub-admin.sql
        config_entries = [
            Config(name='CSRF_PROTECT', description='Profile CSRF Protection (PwnedHub)', type='security control', value=True),
            Config(name='OSCI_PROTECT', description='Tools OSCI Protection (PwnedHub)', type='security control', value=False),
            Config(name='SQLI_PROTECT', description='Login SQLi Protection (PwnedHub)', type='security control', value=False),
            Config(name='CSP_PROTECT', description='Content Security Policy (PwnedHub)', type='security control', value=False),
            Config(name='CORS_RESTRICT', description='Restricted CORS (PwnedAPI)', type='security control', value=True),
            Config(name='JWT_VERIFY', description='Verify JWT Signatures (PwnedAPI)', type='security control', value=True),
            Config(name='JWT_ENCRYPT', description='Encrypt JWTs (PwnedAPI)', type='security control', value=False),
            Config(name='BEARER_AUTH_ENABLE', description='Bearer Token Authentication (PwnedAPI)', type='feature', value=False),
            Config(name='OIDC_ENABLE', description='OpenID Connect Authentication (PwnedHub)', type='feature', value=False),
            Config(name='SSO_ENABLE', description='SSO Authentication (PwnedHub)', type='feature', value=False),
            Config(name='OOB_RESET_ENABLE', description='Out-of-Band Password Reset (PwnedHub)', type='feature', value=False),
            Config(name='CTF_MODE', description='CTF Mode (Warning: Disables this interface!)', type='feature', value=False),
        ]
        for entry in config_entries:
            _db.session.add(entry)
        _db.session.commit()

        # Seed a public Room (needed before creating Users, since User.__init__ calls Room.get_public_rooms())
        public_room = Room(name='General', private=False)
        _db.session.add(public_room)
        _db.session.commit()

    yield app


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for making requests."""
    with app.app_context():
        with app.test_client() as client:
            yield client


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a database session that rolls back after each test."""
    from pwnedapi.extensions import db as _db
    with app.app_context():
        yield _db.session
        _db.session.rollback()


@pytest.fixture(scope='function')
def admin_user(app, client):
    """Create an admin user for testing."""
    from pwnedapi.extensions import db as _db
    from pwnedapi.models import User, Note
    user = User.query.filter_by(email='admin@test.com').first()
    if not user:
        user = User(
            email='admin@test.com',
            name='Admin User',
            avatar=None,
            signature='Admin signature',
            role=0,
            status=1,
        )
        _db.session.add(user)
        user.join_public_rooms()
        _db.session.commit()
    yield user
    Note.query.filter_by(user_id=user.id).delete()
    _db.session.commit()


@pytest.fixture(scope='function')
def user(app, client):
    """Create a regular user for testing."""
    from pwnedapi.extensions import db as _db
    from pwnedapi.models import User, Note
    user = User.query.filter_by(email='user@test.com').first()
    if not user:
        user = User(
            email='user@test.com',
            name='Test User',
            avatar=None,
            signature='Test signature',
            role=1,
            status=1,
        )
        _db.session.add(user)
        user.join_public_rooms()
        _db.session.commit()
    yield user
    Note.query.filter_by(user_id=user.id).delete()
    _db.session.commit()


def _make_auth_headers(app, user_obj):
    """Build headers with a valid JWT cookie and CSRF token for the given user."""
    from pwnedapi.utils import encode_jwt, CsrfToken
    token = encode_jwt(user_obj.id)
    csrf_obj = CsrfToken(user_obj.id)
    csrf_obj.sign(app.config['SECRET_KEY'])
    csrf_token = csrf_obj.serialize()
    return {
        'access_token_cookie': token,
        'csrf_token': csrf_token,
    }


@pytest.fixture(scope='function')
def auth_headers(app):
    """Return a callable that produces auth headers (JWT cookie + CSRF token) for a given user."""
    def _get_headers(user_obj):
        return _make_auth_headers(app, user_obj)
    return _get_headers


@pytest.fixture(scope='function')
def admin_headers(app, admin_user):
    """Return auth headers for the admin user."""
    return _make_auth_headers(app, admin_user)
