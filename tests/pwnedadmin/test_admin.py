import pytest
from pwnedadmin.models import Config, Email


class TestConfigRoutes:
    """Tests for the /config/ admin routes."""

    def test_config_get(self, client):
        """GET /config/ returns 200 with the config page."""
        response = client.get('/config/')
        assert response.status_code == 200

    def test_config_post_toggle(self, client, db_session):
        """POST /config/ with sqli_protect=on changes the config value to True."""
        # Verify it starts as False
        config = Config.get_by_name('SQLI_PROTECT')
        assert config.value is False

        response = client.post('/config/', data={
            'sqli_protect': 'on',
        }, follow_redirects=True)
        assert response.status_code == 200

        # Verify the config value was toggled
        db_session.expire_all()
        config = Config.get_by_name('SQLI_PROTECT')
        assert config.value is True

    def test_config_ctf_mode_blocks(self, client, db_session):
        """When CTF_MODE is True, GET /config/ returns 404."""
        config = Config.get_by_name('CTF_MODE')
        config.value = True
        db_session.commit()

        response = client.get('/config/')
        assert response.status_code == 404


class TestInboxRoutes:
    """Tests for the /inbox/ admin routes."""

    def test_inbox_get(self, client):
        """GET /inbox/ returns 200."""
        response = client.get('/inbox/')
        assert response.status_code == 200

    def test_inbox_get_filtered(self, client, db_session):
        """GET /inbox/?user=test@example.com filters emails by receiver."""
        email = Email(
            sender='sender@example.com',
            receiver='test@example.com',
            subject='Test Subject',
            body='Test body content.',
        )
        db_session.add(email)
        db_session.commit()

        response = client.get('/inbox/?user=test@example.com')
        assert response.status_code == 200
        assert b'Test Subject' in response.data

        # Emails for a different receiver should not appear
        response = client.get('/inbox/?user=other@example.com')
        assert response.status_code == 200
        assert b'Test Subject' not in response.data

    def test_inbox_empty(self, client, db_session):
        """GET /inbox/empty deletes all emails and redirects."""
        email = Email(
            sender='sender@example.com',
            receiver='test@example.com',
            subject='To be deleted',
            body='This will be removed.',
        )
        db_session.add(email)
        db_session.commit()
        assert Email.query.count() == 1

        response = client.get('/inbox/empty')
        assert response.status_code == 302

        assert Email.query.count() == 0

    def test_no_auth_required(self, client):
        """All routes work without any authentication - this IS the vulnerability."""
        # Config route
        response = client.get('/config/')
        assert response.status_code == 200

        # Inbox route
        response = client.get('/inbox/')
        assert response.status_code == 200

        # Inbox empty route (redirects, but does not require auth)
        response = client.get('/inbox/empty')
        assert response.status_code == 302
