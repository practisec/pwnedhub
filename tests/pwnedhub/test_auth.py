import jwt
import tempfile
from pwnedhub.models import User
from pwnedhub.extensions import db as _db


class TestRegister:

    def test_register_success(self, client, app):
        """POST /register with valid data creates an account and redirects to login."""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@pwnedhub.com',
            'name': 'New User',
            'password': 'password123',
            'question': '0',
            'answer': 'tacos',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']
        _db.session.expire_all()
        created = User.query.filter_by(username='newuser').first()
        assert created is not None
        assert created.email == 'newuser@pwnedhub.com'

    def test_register_duplicate_username(self, client, app):
        """Registering with an existing username flashes an error."""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'unique@pwnedhub.com',
            'name': 'Duplicate',
            'password': 'password123',
            'question': '0',
            'answer': 'answer',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Username already exists.' in response.data

    def test_register_duplicate_email(self, client, app):
        """Registering with an existing email flashes an error."""
        response = client.post('/register', data={
            'username': 'uniqueuser',
            'email': 'testuser@pwnedhub.com',
            'name': 'Duplicate Email',
            'password': 'password123',
            'question': '0',
            'answer': 'answer',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Email already exists.' in response.data

    def test_register_weak_password(self, client, app):
        """Registering with a password less than 6 characters flashes an error."""
        response = client.post('/register', data={
            'username': 'weakuser',
            'email': 'weak@pwnedhub.com',
            'name': 'Weak Pass',
            'password': 'abc',
            'question': '0',
            'answer': 'answer',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Password does not meet complexity requirements.' in response.data


class TestLogin:

    def test_login_success(self, client, app):
        """POST /login with valid credentials redirects to home and sets session."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/home' in response.headers['Location']
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None

    def test_login_invalid_credentials(self, client, app):
        """POST /login with wrong password redirects back to login with error."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.headers['Location']
        assert 'error' in response.headers['Location']

    def test_login_disabled_user(self, client, app):
        """A disabled user cannot log in."""
        u = User.query.filter_by(username='testuser').first()
        u.status = 0
        _db.session.commit()
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.headers['Location']
        assert 'error' in response.headers['Location']


class TestLogout:

    def test_logout(self, logged_in_client):
        """GET /logout clears the session and redirects to index."""
        response = logged_in_client.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        assert '/' in response.headers['Location']
        with logged_in_client.session_transaction() as sess:
            assert 'user_id' not in sess


class TestSSOLogin:

    def test_sso_login_valid_token(self, client, app):
        """GET /sso/login with a valid HS256 JWT authenticates the user."""
        token = jwt.encode(
            {'sub': 'testuser'},
            app.config['SECRET_KEY'],
            algorithm='HS256',
        )
        response = client.get(f'/sso/login?id_token={token}', follow_redirects=False)
        assert response.status_code == 302
        assert '/home' in response.headers['Location']
        with client.session_transaction() as sess:
            assert sess.get('user_id') is not None

    def test_sso_login_invalid_token(self, client, app):
        """GET /sso/login with an invalid JWT redirects to login with error."""
        response = client.get('/sso/login?id_token=invalid.token.value', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.headers['Location']
        assert 'error' in response.headers['Location']


class TestPasswordReset:

    def test_reset_init_valid_user(self, client, app):
        """POST /reset with a valid username redirects to the question step."""
        response = client.post('/reset', data={
            'username': 'testuser',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/reset/question' in response.headers['Location']

    def test_reset_init_invalid_user(self, client, app):
        """POST /reset with an unknown username flashes an error."""
        response = client.post('/reset', data={
            'username': 'nonexistent',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'User not recognized.' in response.data

    def test_reset_question_correct(self, client, app):
        """POST /reset/question with the correct answer advances to password step."""
        # First initialize the reset flow
        client.post('/reset', data={'username': 'testuser'}, follow_redirects=False)
        response = client.post('/reset/question', data={
            'answer': 'pizza',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/reset/password' in response.headers['Location']

    def test_reset_question_incorrect(self, client, app):
        """POST /reset/question with the wrong answer flashes an error."""
        # First initialize the reset flow
        client.post('/reset', data={'username': 'testuser'}, follow_redirects=False)
        response = client.post('/reset/question', data={
            'answer': 'wronganswer',
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Incorrect answer.' in response.data

    def test_reset_password_success(self, client, app):
        """POST /reset/password with a valid password resets it and redirects to login."""
        # Initialize the reset flow and answer the question
        client.post('/reset', data={'username': 'testuser'}, follow_redirects=False)
        client.post('/reset/question', data={'answer': 'pizza'}, follow_redirects=False)
        response = client.post('/reset/password', data={
            'password': 'newpassword123',
        }, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']
        # Verify the password was actually changed by logging in with the new password
        login_response = client.post('/login', data={
            'username': 'testuser',
            'password': 'newpassword123',
        }, follow_redirects=False)
        assert login_response.status_code == 302
        assert '/home' in login_response.headers['Location']
