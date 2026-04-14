import jwt
import pytest
from urllib.parse import urlparse, parse_qs


class TestAuthenticate:
    """Tests for the /authenticate SSO endpoint."""

    def test_authenticate_valid_credentials(self, client, app, user):
        """POST /authenticate with valid credentials redirects with a valid id_token."""
        response = client.post('/authenticate', data={
            'username': 'testuser',
            'password': 'password123',
        })
        assert response.status_code == 302
        location = response.headers['Location']
        assert 'www.pwnedhub.com/sso/login' in location
        # Extract and decode the id_token
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        assert 'id_token' in params
        id_token = params['id_token'][0]
        payload = jwt.decode(id_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        assert payload['sub'] == 'testuser'

    def test_authenticate_invalid_password(self, client, app):
        """POST /authenticate with wrong password redirects with id_token containing None sub."""
        response = client.post('/authenticate', data={
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        assert response.status_code == 302
        location = response.headers['Location']
        assert 'www.pwnedhub.com/sso/login' in location
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        assert 'id_token' in params
        id_token = params['id_token'][0]
        payload = jwt.decode(id_token, app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_sub': False})
        assert payload['sub'] is None

    def test_authenticate_invalid_username(self, client, app):
        """POST /authenticate with nonexistent username redirects with id_token containing None sub."""
        response = client.post('/authenticate', data={
            'username': 'nonexistent',
            'password': 'password123',
        })
        assert response.status_code == 302
        location = response.headers['Location']
        assert 'www.pwnedhub.com/sso/login' in location
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        assert 'id_token' in params
        id_token = params['id_token'][0]
        payload = jwt.decode(id_token, app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_sub': False})
        assert payload['sub'] is None

    def test_authenticate_missing_credentials(self, client, app):
        """POST /authenticate with missing form fields still redirects with None sub."""
        response = client.post('/authenticate', data={})
        assert response.status_code == 302
        location = response.headers['Location']
        assert 'www.pwnedhub.com/sso/login' in location
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        assert 'id_token' in params
        id_token = params['id_token'][0]
        payload = jwt.decode(id_token, app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_sub': False})
        assert payload['sub'] is None
