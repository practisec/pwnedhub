import json
import tempfile
from unittest.mock import patch, MagicMock

from pwnedhub.extensions import db as _db
from pwnedhub.models import Config, User, Tool, Message, Mail, Note


class TestPublicRoutes:

    def test_index(self, client):
        """GET / returns 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_diagnostics(self, client):
        """GET /diagnostics returns 200 with platform info."""
        response = client.get('/diagnostics')
        assert response.status_code == 200
        assert b'platform' in response.data.lower() or b'architecture' in response.data.lower() or b'python' in response.data.lower()


class TestHome:

    def test_home_unauthenticated(self, client):
        """GET /home when not logged in redirects to /."""
        response = client.get('/home', follow_redirects=False)
        assert response.status_code == 302
        location = response.headers['Location']
        assert location.endswith('/') or location == '/'

    def test_home_admin(self, admin_client):
        """GET /home as admin redirects to /admin/users."""
        response = admin_client.get('/home', follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/users' in response.headers['Location']

    def test_home_user(self, logged_in_client):
        """GET /home as regular user redirects to /notes."""
        response = logged_in_client.get('/home', follow_redirects=False)
        assert response.status_code == 302
        assert '/notes' in response.headers['Location']


class TestAdminTools:

    def test_admin_tools_requires_admin(self, logged_in_client):
        """Regular user gets 403 on /admin/tools."""
        response = logged_in_client.get('/admin/tools')
        assert response.status_code == 403

    def test_admin_tools_list(self, admin_client, app):
        """Admin can see the tools page."""
        response = admin_client.get('/admin/tools')
        assert response.status_code == 200
        assert b'Dig' in response.data

    def test_admin_tools_add(self, admin_client, app):
        """POST /admin/tools/add creates a new tool."""
        response = admin_client.post('/admin/tools/add', data={
            'name': 'Nmap',
            'path': 'nmap',
            'description': 'Network mapper.',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/tools' in response.headers['Location']
        _db.session.expire_all()
        tool = Tool.query.filter_by(name='Nmap').first()
        assert tool is not None
        assert tool.path == 'nmap'

    def test_admin_tools_remove(self, admin_client, app):
        """Admin can remove a tool."""
        tool = Tool.query.first()
        tool_id = tool.id
        response = admin_client.get(f'/admin/tools/remove/{tool_id}', follow_redirects=False)
        assert response.status_code == 302
        assert '/admin/tools' in response.headers['Location']
        _db.session.expire_all()
        removed = _db.session.get(Tool, tool_id)
        assert removed is None


class TestAdminUsers:

    def test_admin_users_list(self, admin_client):
        """Admin can see the user list."""
        response = admin_client.get('/admin/users')
        assert response.status_code == 200
        assert b'testuser' in response.data

    def test_admin_users_modify_promote(self, admin_client, app, user):
        """Admin can promote a user to admin."""
        response = admin_client.get(f'/admin/users/promote/{user.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'User promoted.' in response.data
        _db.session.expire_all()
        u = _db.session.get(User, user.id)
        assert u.role == 0

    def test_admin_users_modify_demote(self, admin_client, app, user):
        """Admin can demote a user."""
        # First promote, then demote
        user.role = 0
        _db.session.commit()
        response = admin_client.get(f'/admin/users/demote/{user.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'User demoted.' in response.data
        _db.session.expire_all()
        u = _db.session.get(User, user.id)
        assert u.role == 1

    def test_admin_users_modify_disable(self, admin_client, app, user):
        """Admin can disable a user."""
        response = admin_client.get(f'/admin/users/disable/{user.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'User disabled.' in response.data
        _db.session.expire_all()
        u = _db.session.get(User, user.id)
        assert u.status == 0

    def test_admin_users_modify_enable(self, admin_client, app, user):
        """Admin can enable a user."""
        user.status = 0
        _db.session.commit()
        response = admin_client.get(f'/admin/users/enable/{user.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'User enabled.' in response.data
        _db.session.expire_all()
        u = _db.session.get(User, user.id)
        assert u.status == 1

    def test_admin_users_self_modification_denied(self, admin_client, app, admin_user):
        """Admin cannot modify themselves."""
        response = admin_client.get(f'/admin/users/promote/{admin_user.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Self-modification denied.' in response.data


class TestProfile:

    def test_profile_get(self, logged_in_client):
        """Logged in user can see their profile page."""
        response = logged_in_client.get('/profile')
        assert response.status_code == 200
        assert b'testuser' in response.data or b'Test User' in response.data

    def test_profile_update(self, logged_in_client, app):
        """POST /profile updates the user's name, question, and answer."""
        # set a CSRF token in the session so the @csrf_protect decorator accepts the request
        import uuid
        csrf_token = str(uuid.uuid4())
        with logged_in_client.session_transaction() as sess:
            sess['csrf_token'] = csrf_token
        response = logged_in_client.post('/profile', data={
            'name': 'Updated Name',
            'question': '2',
            'answer': 'newanswer',
            'password': '',
            'avatar': '',
            'signature': 'new sig',
            'csrf_token': csrf_token,
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Account information changed.' in response.data
        _db.session.expire_all()
        u = User.query.filter_by(username='testuser').first()
        assert u.name == 'Updated Name'
        assert u.question == 2
        assert u.answer == 'newanswer'

    def test_profile_requires_login(self, client):
        """Unauthenticated access to /profile redirects to login."""
        response = client.get('/profile', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_profile_view_other_user(self, logged_in_client, app, admin_user):
        """Logged in user can view another user's profile."""
        response = logged_in_client.get(f'/profile/view/{admin_user.id}')
        assert response.status_code == 200
        assert b'Administrator' in response.data


class TestMail:

    def test_mail_inbox(self, logged_in_client):
        """GET /mail shows the inbox."""
        response = logged_in_client.get('/mail')
        assert response.status_code == 200

    def test_mail_compose_and_send(self, logged_in_client, app, admin_user):
        """POST /mail/compose creates a mail and redirects to inbox."""
        app.bot_task_queue.enqueue = MagicMock()
        response = logged_in_client.post('/mail/compose', data={
            'receiver': str(admin_user.id),
            'subject': 'Test Subject',
            'content': 'Test content body.',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/mail' in response.headers['Location']
        _db.session.expire_all()
        mail = Mail.query.filter_by(subject='Test Subject').first()
        assert mail is not None
        assert mail.content == 'Test content body.'

    def test_mail_view(self, logged_in_client, app, admin_user, user):
        """Viewing a mail marks it as read."""
        letter = Mail(
            subject='Unread Mail',
            content='Some content',
            sender_id=admin_user.id,
            receiver_id=user.id,
            read=0,
        )
        _db.session.add(letter)
        _db.session.commit()
        letter_id = letter.id
        response = logged_in_client.get(f'/mail/view/{letter_id}')
        assert response.status_code == 200
        _db.session.expire_all()
        letter = _db.session.get(Mail, letter_id)
        assert letter.read == 1

    def test_mail_delete(self, logged_in_client, app, admin_user, user):
        """Deleting a mail removes it from the database."""
        letter = Mail(
            subject='Delete Me',
            content='Content',
            sender_id=admin_user.id,
            receiver_id=user.id,
        )
        _db.session.add(letter)
        _db.session.commit()
        letter_id = letter.id
        response = logged_in_client.get(f'/mail/delete/{letter_id}', follow_redirects=False)
        assert response.status_code == 302
        assert '/mail' in response.headers['Location']
        _db.session.expire_all()
        deleted = _db.session.get(Mail, letter_id)
        assert deleted is None


class TestMessages:

    def test_messages_list(self, logged_in_client):
        """GET /messages returns paginated messages."""
        response = logged_in_client.get('/messages')
        assert response.status_code == 200

    def test_messages_create(self, logged_in_client, app):
        """POST /messages/create adds a message."""
        response = logged_in_client.post('/messages/create', data={
            'message': 'Hello, world!',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/messages' in response.headers['Location']
        _db.session.expire_all()
        msg = Message.query.filter_by(comment='Hello, world!').first()
        assert msg is not None

    def test_messages_delete_own(self, logged_in_client, app, user):
        """User can delete their own message."""
        msg = Message(comment='My message', user_id=user.id)
        _db.session.add(msg)
        _db.session.commit()
        msg_id = msg.id
        response = logged_in_client.get(f'/messages/delete/{msg_id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Message deleted.' in response.data
        _db.session.expire_all()
        deleted = _db.session.get(Message, msg_id)
        assert deleted is None

    def test_messages_delete_others_forbidden(self, logged_in_client, app, admin_user):
        """User cannot delete another user's message."""
        msg = Message(comment='Admin message', user_id=admin_user.id)
        _db.session.add(msg)
        _db.session.commit()
        msg_id = msg.id
        response = logged_in_client.get(f'/messages/delete/{msg_id}')
        assert response.status_code == 403

    def test_messages_delete_admin_can(self, admin_client, app, user):
        """Admin can delete any user's message."""
        msg = Message(comment='User message for admin delete', user_id=user.id)
        _db.session.add(msg)
        _db.session.commit()
        msg_id = msg.id
        response = admin_client.get(f'/messages/delete/{msg_id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Message deleted.' in response.data
        _db.session.expire_all()
        deleted = _db.session.get(Message, msg_id)
        assert deleted is None


class TestNotes:

    def test_notes_get(self, logged_in_client):
        """GET /notes shows the default note when the user has no notes."""
        response = logged_in_client.get('/notes')
        assert response.status_code == 200
        assert b'Welcome to PwnedHub' in response.data

    def test_notes_update(self, logged_in_client, app, user):
        """PUT /notes updates the note content."""
        response = logged_in_client.put('/notes',
            data=json.dumps({'notes': 'Updated note content'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['notes'] == 'Updated note content'
        _db.session.expire_all()
        note = Note.query.filter_by(user_id=user.id).first()
        assert note is not None
        assert note.content == 'Updated note content'


class TestArtifacts:

    def test_artifacts_list(self, logged_in_client):
        """GET /artifacts returns 200."""
        response = logged_in_client.get('/artifacts')
        assert response.status_code == 200


class TestTools:

    def test_tools_list(self, logged_in_client):
        """GET /tools returns 200."""
        response = logged_in_client.get('/tools')
        assert response.status_code == 200

    def test_tools_info(self, logged_in_client, app):
        """GET /tools/info/<id> returns tool JSON."""
        tool = Tool.query.first()
        tool_id = tool.id
        response = logged_in_client.get(f'/tools/info/{tool_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('name') == 'Dig'
        assert data.get('path') == 'dig'

    @patch('pwnedhub.routes.core.subprocess.Popen')
    def test_tools_execute(self, mock_popen, logged_in_client, app):
        """POST /tools/execute/<id> with valid args runs the tool."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'tool output here', b'')
        mock_popen.return_value = mock_process
        tool = Tool.query.first()
        tool_id = tool.id
        response = logged_in_client.post(f'/tools/execute/{tool_id}',
            data=json.dumps({'args': 'example.com'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('error') is False
        assert 'tool output here' in data.get('output', '')

    @patch('pwnedhub.routes.core.subprocess.Popen')
    def test_tools_execute_invalid_command(self, mock_popen, logged_in_client, app):
        """POST /tools/execute/<id> with invalid characters is blocked."""
        tool = Tool.query.first()
        tool_id = tool.id
        response = logged_in_client.post(f'/tools/execute/{tool_id}',
            data=json.dumps({'args': 'example.com; cat /etc/passwd'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('error') is True
        assert 'invalid characters' in data.get('output', '').lower()
        mock_popen.assert_not_called()


class TestUnfurl:

    @patch('pwnedhub.utils.requests.get')
    def test_unfurl_valid_url(self, mock_get, logged_in_client):
        """POST /messages/unfurl with a valid URL extracts meta tags."""
        mock_response = MagicMock()
        mock_response.content = b'''
        <html>
        <head>
            <meta property="og:title" content="Test Title" />
            <meta property="og:description" content="Test Description" />
            <meta property="og:site_name" content="TestSite" />
        </head>
        <body></body>
        </html>
        '''
        mock_get.return_value = mock_response
        response = logged_in_client.post('/messages/unfurl',
            data=json.dumps({'url': 'https://example.com'}),
            content_type='application/json',
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get('title') == 'Test Title'
        assert data.get('description') == 'Test Description'
        assert data.get('site_name') == 'TestSite'

    def test_unfurl_no_url(self, logged_in_client):
        """POST /messages/unfurl without a URL returns 400."""
        response = logged_in_client.post('/messages/unfurl',
            data=json.dumps({}),
            content_type='application/json',
        )
        assert response.status_code == 400


class TestLoginRequired:

    PROTECTED_ROUTES = [
        ('/profile', 'GET'),
        ('/mail', 'GET'),
        ('/mail/compose', 'GET'),
        ('/messages', 'GET'),
        ('/notes', 'GET'),
        ('/artifacts', 'GET'),
        ('/tools', 'GET'),
        ('/admin/tools', 'GET'),
        ('/admin/users', 'GET'),
    ]

    def test_login_required_routes(self, client):
        """All protected routes redirect to login when not authenticated."""
        for path, method in self.PROTECTED_ROUTES:
            if method == 'GET':
                response = client.get(path, follow_redirects=False)
            else:
                response = client.post(path, follow_redirects=False)
            assert response.status_code == 302, f'{method} {path} did not redirect (got {response.status_code})'
            assert '/login' in response.headers['Location'], f'{method} {path} did not redirect to login'
