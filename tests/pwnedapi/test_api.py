import json
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_cookie_and_get(client, app, user, url, **kwargs):
    """Make an authenticated GET request by setting the access_token cookie."""
    from pwnedapi.utils import encode_jwt
    token = encode_jwt(user.id)
    client.set_cookie('access_token', token, domain='localhost')
    return client.get(url, **kwargs)


def _set_cookie_and_request(client, app, user, method, url, json_data=None, extra_headers=None):
    """Make an authenticated request with JWT cookie and optional CSRF + JSON body."""
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


def _get_db():
    from pwnedapi.extensions import db
    return db


def _get_models():
    from pwnedapi.models import Config, Email, User, Note, Message, Tool, Scan, Room
    return Config, Email, User, Note, Message, Tool, Scan, Room


# ===========================================================================
# TokenList
# ===========================================================================

class TestTokenList:

    def test_create_token_passwordless_init(self, client, app, user):
        """POST /access-token with email returns 403 with code_token for passwordless flow."""
        resp = client.post('/access-token', json={'email': user.email})
        assert resp.status_code == 403
        data = resp.get_json()
        assert data['error'] == 'code_required'
        assert 'code_token' in data

    def test_create_token_passwordless_complete(self, client, app, user):
        """POST /access-token with code + code_token returns 201 with access token cookie."""
        # Step 1: initiate
        resp = client.post('/access-token', json={'email': user.email})
        assert resp.status_code == 403
        data = resp.get_json()
        code_token = data['code_token']

        # Decode code_token to get the code
        from pwnedapi.utils import decode_jwt
        payload = decode_jwt(code_token)
        code = payload['code']

        # Step 2: complete
        resp = client.post('/access-token', json={
            'code': code,
            'code_token': code_token,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'csrf_token' in data
        # Check that the access_token cookie was set
        assert client.get_cookie('access_token') is not None

    def test_delete_token(self, client, app, user):
        """DELETE /access-token returns 204."""
        resp = client.delete('/access-token')
        assert resp.status_code == 204


# ===========================================================================
# UserList
# ===========================================================================

class TestUserList:

    def test_get_users_authenticated(self, client, app, user):
        """GET /users with auth returns user list."""
        resp = _set_cookie_and_get(client, app, user, '/users')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'users' in data
        assert isinstance(data['users'], list)
        assert len(data['users']) >= 1

    def test_get_users_unauthenticated(self, client, app):
        """GET /users without auth returns 401."""
        client.delete_cookie('access_token', domain='localhost')
        resp = client.get('/users')
        assert resp.status_code == 401

    def test_create_user_signup_init(self, client, app):
        """POST /users with email + name returns 201 (signup init)."""
        resp = client.post(
            '/users',
            json={'email': 'newuser@test.com', 'name': 'New User'},
            headers={'Origin': 'http://www.pwnedhub.com'},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['success'] is True


# ===========================================================================
# UserInst
# ===========================================================================

class TestUserInst:

    def test_get_user_me(self, client, app, user):
        """GET /users/me returns current user."""
        resp = _set_cookie_and_get(client, app, user, '/users/me')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['email'] == user.email
        assert data['name'] == user.name

    def test_get_user_by_id(self, client, app, user):
        """GET /users/<id> returns user by ID."""
        resp = _set_cookie_and_get(client, app, user, f'/users/{user.id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['email'] == user.email

    def test_patch_user_self(self, client, app, user):
        """PATCH /users/me updates profile fields."""
        resp = _set_cookie_and_request(client, app, user, 'PATCH', '/users/me', json_data={
            'email': user.email,
            'name': 'Updated Name',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['name'] == 'Updated Name'
        # Reset name for other tests
        _set_cookie_and_request(client, app, user, 'PATCH', '/users/me', json_data={
            'email': user.email,
            'name': 'Test User',
        })

    def test_patch_user_other_forbidden(self, client, app, user, admin_user):
        """PATCH /users/<other_id> returns 403."""
        resp = _set_cookie_and_request(client, app, user, 'PATCH', f'/users/{admin_user.id}', json_data={
            'email': 'hacker@test.com',
            'name': 'Hacker',
        })
        assert resp.status_code == 403


# ===========================================================================
# AdminUserInst
# ===========================================================================

class TestAdminUserInst:

    def test_admin_patch_user(self, client, app, admin_user, user):
        """Admin can change role/status of another user."""
        resp = _set_cookie_and_request(client, app, admin_user, 'PATCH', f'/admin/users/{user.id}', json_data={
            'role': 0,
            'status': 1,
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['role'] == 'admin'
        # Reset role
        _set_cookie_and_request(client, app, admin_user, 'PATCH', f'/admin/users/{user.id}', json_data={
            'role': 1,
        })

    def test_admin_patch_user_non_admin(self, client, app, user, admin_user):
        """Regular user gets 403 when trying admin endpoint."""
        resp = _set_cookie_and_request(client, app, user, 'PATCH', f'/admin/users/{admin_user.id}', json_data={
            'role': 0,
        })
        assert resp.status_code == 403

    def test_admin_self_admin_denied(self, client, app, admin_user):
        """Admin cannot modify self via admin endpoint."""
        resp = _set_cookie_and_request(client, app, admin_user, 'PATCH', f'/admin/users/{admin_user.id}', json_data={
            'role': 1,
        })
        assert resp.status_code == 400


# ===========================================================================
# NoteInst
# ===========================================================================

class TestNoteInst:

    def test_get_notes_default(self, client, app, user):
        """GET /notes returns default note content when no notes exist."""
        resp = _set_cookie_and_get(client, app, user, '/notes')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'content' in data
        # Default note contains the welcome message
        assert 'Welcome to PwnedHub' in data['content']

    def test_put_notes(self, client, app, user):
        """PUT /notes updates note content."""
        resp = _set_cookie_and_request(client, app, user, 'PUT', '/notes', json_data={
            'content': 'My updated test note content',
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True

    def test_get_notes_after_update(self, client, app, user):
        """GET /notes returns updated content after a PUT."""
        # First update
        _set_cookie_and_request(client, app, user, 'PUT', '/notes', json_data={
            'content': 'Content after update',
        })
        # Then read
        resp = _set_cookie_and_get(client, app, user, '/notes')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['content'] == 'Content after update'


# ===========================================================================
# RoomMessageList
# ===========================================================================

class TestRoomMessageList:

    def test_get_messages_member(self, client, app, user):
        """GET /rooms/<rid>/messages returns messages for room user is in."""
        _, _, _, _, _, _, _, Room = _get_models()
        public_room = Room.query.filter_by(name='General').first()
        room_id = public_room.id
        resp = _set_cookie_and_get(client, app, user, f'/rooms/{room_id}/messages')
        assert resp.status_code == 200
        data = resp.get_json(force=True)
        assert 'messages' in data
        assert isinstance(data['messages'], list)

    def test_get_messages_non_member(self, client, app, user):
        """GET /rooms/<rid>/messages returns 403 for room user is NOT in."""
        _, _, _, _, _, _, _, Room = _get_models()
        db = _get_db()
        private_room = Room.query.filter_by(name='PrivateTestRoom').first()
        if not private_room:
            private_room = Room(name='PrivateTestRoom', private=True)
            db.session.add(private_room)
            db.session.commit()
        room_id = private_room.id
        resp = _set_cookie_and_get(client, app, user, f'/rooms/{room_id}/messages')
        assert resp.status_code == 403


# ===========================================================================
# UnfurlList
# ===========================================================================

class TestUnfurlList:

    @patch('pwnedapi.utils.requests.get')
    def test_unfurl_valid(self, mock_get, client, app):
        """POST /unfurl with valid URL returns meta data."""
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
        <head>
            <meta property="og:site_name" content="TestSite" />
            <meta property="og:title" content="Test Title" />
            <meta property="og:description" content="Test Description" />
        </head>
        <body></body>
        </html>
        '''
        mock_get.return_value = mock_response

        resp = client.post('/unfurl', json={'url': 'http://example.com'})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['url'] == 'http://example.com'
        assert data['title'] == 'Test Title'
        assert data['description'] == 'Test Description'

    def test_unfurl_no_url(self, client, app):
        """POST /unfurl without URL returns 400."""
        resp = client.post('/unfurl', json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data['error'] == 'RequestError'

    @patch('pwnedapi.utils.requests.get')
    def test_unfurl_no_auth_required(self, mock_get, client, app):
        """POST /unfurl works without authentication."""
        mock_response = MagicMock()
        mock_response.content = b'<html><head></head><body></body></html>'
        mock_get.return_value = mock_response

        # Ensure no cookie is set
        client.delete_cookie('access_token', domain='localhost')
        resp = client.post('/unfurl', json={'url': 'http://example.com'})
        assert resp.status_code == 201


# ===========================================================================
# ToolList
# ===========================================================================

class TestToolList:

    def test_get_tools(self, client, app, user):
        """GET /tools returns tool list."""
        resp = _set_cookie_and_get(client, app, user, '/tools')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'tools' in data
        assert isinstance(data['tools'], list)

    def test_create_tool_admin(self, client, app, admin_user):
        """Admin can create a tool via POST /tools."""
        _, _, _, _, _, Tool, _, _ = _get_models()
        db = _get_db()
        resp = _set_cookie_and_request(client, app, admin_user, 'POST', '/tools', json_data={
            'name': 'Test Tool',
            'path': '/usr/bin/testtool',
            'description': 'A test tool',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['name'] == 'Test Tool'
        assert data['path'] == '/usr/bin/testtool'
        # Cleanup
        tool = Tool.query.filter_by(name='Test Tool').first()
        if tool:
            db.session.delete(tool)
            db.session.commit()

    def test_create_tool_non_admin(self, client, app, user):
        """Regular user gets 403 when creating a tool."""
        resp = _set_cookie_and_request(client, app, user, 'POST', '/tools', json_data={
            'name': 'Hacker Tool',
            'path': '/usr/bin/hackertool',
            'description': 'Should not be created',
        })
        assert resp.status_code == 403


# ===========================================================================
# ToolInst
# ===========================================================================

class TestToolInst:

    def _create_tool(self, app):
        _, _, _, _, _, Tool, _, _ = _get_models()
        db = _get_db()
        tool = Tool(name='LookupTool', path='/usr/bin/lookup', description='Lookup tool')
        db.session.add(tool)
        db.session.commit()
        return tool.id

    def _cleanup_tool(self, app, tool_id):
        _, _, _, _, _, Tool, _, _ = _get_models()
        db = _get_db()
        tool = db.session.get(Tool, tool_id)
        if tool:
            db.session.delete(tool)
            db.session.commit()

    def test_get_tool(self, client, app, user):
        """GET /tools/<id> returns tool info."""
        tool_id = self._create_tool(app)
        try:
            resp = _set_cookie_and_get(client, app, user, f'/tools/{tool_id}')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['name'] == 'LookupTool'
        finally:
            self._cleanup_tool(app, tool_id)

    def test_delete_tool_admin(self, client, app, admin_user):
        """Admin can delete a tool."""
        tool_id = self._create_tool(app)
        resp = _set_cookie_and_request(client, app, admin_user, 'DELETE', f'/tools/{tool_id}')
        assert resp.status_code == 204

    def test_delete_tool_non_admin(self, client, app, user):
        """Regular user gets 403 when deleting a tool."""
        tool_id = self._create_tool(app)
        try:
            resp = _set_cookie_and_request(client, app, user, 'DELETE', f'/tools/{tool_id}')
            assert resp.status_code == 403
        finally:
            self._cleanup_tool(app, tool_id)


# ===========================================================================
# ScanList
# ===========================================================================

class TestScanList:

    def _create_tool_for_scan(self, app):
        _, _, _, _, _, Tool, _, _ = _get_models()
        db = _get_db()
        tool = Tool.query.filter_by(name='ScanTool').first()
        if not tool:
            tool = Tool(name='ScanTool', path='/usr/bin/scantool', description='Scan tool')
            db.session.add(tool)
            db.session.commit()
        return tool.id

    def test_get_scans(self, client, app, user):
        """GET /scans returns user's scans."""
        resp = _set_cookie_and_get(client, app, user, '/scans')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'scans' in data
        assert isinstance(data['scans'], list)

    def test_create_scan(self, client, app, user):
        """POST /scans creates a scan with valid tool and args (task queue mocked)."""
        _, _, _, _, _, Tool, Scan, _ = _get_models()
        db = _get_db()
        tool_id = self._create_tool_for_scan(app)

        # Mock the task queue enqueue to return a job-like object
        import uuid
        scan_id = str(uuid.uuid4())
        mock_job = MagicMock()
        mock_job.get_id.return_value = scan_id
        app.api_task_queue.enqueue.return_value = mock_job

        resp = _set_cookie_and_request(client, app, user, 'POST', '/scans', json_data={
            'tid': tool_id,
            'args': '127.0.0.1',
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['id'] == scan_id
        assert data['complete'] is False

        # Cleanup
        scan = db.session.get(Scan, scan_id)
        if scan:
            db.session.delete(scan)
            db.session.commit()
        tool = Tool.query.filter_by(name='ScanTool').first()
        if tool:
            db.session.delete(tool)
            db.session.commit()


# ===========================================================================
# ScanInst / ResultsInst
# ===========================================================================

class TestScanInst:

    def _create_scan_for_user(self, app, user_obj):
        import uuid
        _, _, _, _, _, Tool, Scan, _ = _get_models()
        db = _get_db()
        tool = Tool.query.filter_by(name='ScanToolInst').first()
        if not tool:
            tool = Tool(name='ScanToolInst', path='/usr/bin/scantoolinst', description='Scan tool inst')
            db.session.add(tool)
            db.session.commit()
        scan = Scan(
            id=str(uuid.uuid4()),
            command='/usr/bin/scantoolinst 127.0.0.1',
            results='scan output here',
            complete=True,
            user_id=user_obj.id,
        )
        db.session.add(scan)
        db.session.commit()
        return scan.id

    def _cleanup_scan(self, app, scan_id):
        _, _, _, _, _, Tool, Scan, _ = _get_models()
        db = _get_db()
        scan = db.session.get(Scan, scan_id)
        if scan:
            db.session.delete(scan)
            db.session.commit()

    def test_delete_scan_owner(self, client, app, user):
        """Owner can delete their own scan."""
        scan_id = self._create_scan_for_user(app, user)
        resp = _set_cookie_and_request(client, app, user, 'DELETE', f'/scans/{scan_id}')
        assert resp.status_code == 204
        self._cleanup_scan(app, scan_id)

    def test_delete_scan_non_owner(self, client, app, user, admin_user):
        """Non-owner gets 403 when deleting another user's scan."""
        scan_id = self._create_scan_for_user(app, user)
        try:
            resp = _set_cookie_and_request(client, app, admin_user, 'DELETE', f'/scans/{scan_id}')
            assert resp.status_code == 403
        finally:
            self._cleanup_scan(app, scan_id)

    def test_get_results(self, client, app, user):
        """GET /scans/<scan_id>/results returns scan results."""
        scan_id = self._create_scan_for_user(app, user)
        try:
            resp = _set_cookie_and_get(client, app, user, f'/scans/{scan_id}/results')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['results'] == 'scan output here'
        finally:
            self._cleanup_scan(app, scan_id)
