import os
import tempfile
from hashlib import md5
from unittest.mock import MagicMock, patch

import pytest
from cachelib.file import FileSystemCache

# Set the config environment variable before importing the app
os.environ['CONFIG'] = 'Test'

# Create temp directories at module level so they're available for config patching
_tmp_upload = tempfile.mkdtemp()
_tmp_sessions = tempfile.mkdtemp()

# Patch the Test config class before create_app reads it
import pwnedhub.config
pwnedhub.config.Test.SQLALCHEMY_DATABASE_URI = 'sqlite://'
pwnedhub.config.Test.SQLALCHEMY_BINDS = {'admin': 'sqlite://'}
pwnedhub.config.Test.SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir=_tmp_sessions)
pwnedhub.config.Test.UPLOAD_FOLDER = _tmp_upload
pwnedhub.config.Test.WTF_CSRF_ENABLED = False

from pwnedhub import create_app
from pwnedhub.extensions import db as _db
from pwnedhub.models import Config, Email, User, Tool, Message, Mail, Note


CONFIG_FLAGS = [
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
    # Patch Redis and rq before create_app tries to connect
    mock_redis_class = MagicMock()
    mock_redis_instance = MagicMock()
    mock_redis_class.from_url.return_value = mock_redis_instance
    mock_queue_class = MagicMock()
    mock_queue_instance = MagicMock()
    mock_queue_class.return_value = mock_queue_instance

    with patch('pwnedhub.Redis', mock_redis_class), \
         patch('pwnedhub.rq.Queue', mock_queue_class):
        test_app = create_app()

    test_app.config['TESTING'] = True
    test_app.config['SERVER_NAME'] = 'localhost'
    test_app.config['MESSAGES_PER_PAGE'] = 5

    # Ensure mocks are accessible
    test_app.redis = mock_redis_instance
    test_app.bot_task_queue = mock_queue_instance

    yield test_app


@pytest.fixture(scope='function')
def db_session(app):
    """Set up and tear down all database tables with seed data for each test."""
    with app.app_context():
        _db.create_all()

        # Seed config flags into the admin bind
        for flag in CONFIG_FLAGS:
            config = Config(
                name=flag['name'],
                description=flag['description'],
                type=flag['type'],
                value=flag['value'],
            )
            _db.session.add(config)
        _db.session.commit()

        # Seed admin user (role=0)
        admin = User(
            username='admin',
            email='admin@pwnedhub.com',
            name='Administrator',
            avatar='/static/common/images/avatars/admin.png',
            signature='All your base are belong to me.',
            question=1,
            answer='Diego',
            role=0,
            status=1,
        )
        admin.password = 'adminpassword'
        _db.session.add(admin)
        _db.session.commit()

        # Seed regular user (role=1)
        user = User(
            username='testuser',
            email='testuser@pwnedhub.com',
            name='Test User',
            avatar='',
            signature='Test signature',
            question=0,
            answer='pizza',
            role=1,
            status=1,
        )
        user.password = 'testpassword'
        _db.session.add(user)
        _db.session.commit()

        # Seed a tool
        tool = Tool(
            name='Dig',
            path='dig',
            description='DNS lookup tool.',
        )
        _db.session.add(tool)
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


@pytest.fixture(scope='function')
def admin_user(app, client):
    """Return the admin user from the database."""
    return User.query.filter_by(username='admin').first()


@pytest.fixture(scope='function')
def user(app, client):
    """Return the regular user from the database."""
    return User.query.filter_by(username='testuser').first()


def _login_client(app, test_client, user_obj):
    """Helper to set up a logged-in session for a given user."""
    tmp_upload = tempfile.mkdtemp()
    with test_client.session_transaction() as sess:
        sess['user_id'] = user_obj.id
        sess['upload_folder'] = tmp_upload
    return test_client


@pytest.fixture(scope='function')
def logged_in_client(app, client, user):
    """Provide a test client logged in as the regular user."""
    return _login_client(app, client, user)


@pytest.fixture(scope='function')
def admin_client(app, client, admin_user):
    """Provide a test client logged in as the admin user."""
    return _login_client(app, client, admin_user)
