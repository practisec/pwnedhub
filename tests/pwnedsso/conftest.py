import os
import pytest

os.environ['CONFIG'] = 'Test'

import pwnedsso.config
pwnedsso.config.Test.SQLALCHEMY_DATABASE_URI = 'sqlite://'

from pwnedsso import create_app
from pwnedsso.extensions import db as _db
from pwnedsso.models import User
from pwnedsso.utils import xor_encrypt


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
        user.password_hash = xor_encrypt('password123', app.config['SECRET_KEY'])
        _db.session.add(user)
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
def user(app, client):
    """Return the seeded test user from the database."""
    return User.query.filter_by(username='testuser').first()
