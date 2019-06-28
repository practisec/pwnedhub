from flask import g
from pwnedhub import create_app, db
from common.models import User, Message
import unittest

class PwnedHubTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('Test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        user = User(username='tim', name='Tim', password='password', question='0', answer='tacos', role='1')
        db.session.add(user)
        admin = User(username='admin', name='Administrator', password='engagements', question='1', answer='Ralf', role='0')
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        rv = self.client.get('/login')
        from hashlib import md5
        from lxml.html import fromstring
        tree = fromstring(rv.data)
        nonce = tree.xpath('//input[@name="nonce"]/@value')[0]
        token = md5(password+nonce).hexdigest()
        return self.client.post('/login', data=dict(
            username=username,
            password=password,
            token=token
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def _test_login_logout(self):
        rv = self.login('tim', 'password')
        assert 'Welcome to PwnedHub!' in rv.data
        rv = self.logout()
        assert 'log in' in rv.data
        rv = self.login('admin', 'engagements')
        assert '>admin<' in rv.data
        rv = self.logout()
        assert 'log in' in rv.data

    def test_xss_messages(self):
        self.login('tim', 'password')
        payload = '<script>alert(42)</script>'
        msg = Message(comment=payload, user=g.user)
        db.session.add(msg)
        db.session.commit()
        rv = self.client.get('/messages', follow_redirects=True)
        self.assertNotIn(payload, rv.data, 'XSS payload reflected in the response.')

    def test_cookie_httponly(self):
        rv = self.client.get('/')
        for header in rv.headers:
            if header[0] == 'Set-Cookie' and header[1].startswith('session='):
                self.assertIn('httponly', header[1].lower(), 'HttpOnly flag not present on session cookie.')

class CustomTestResult(unittest._TextTestResult):

    def addSuccess(self, test):
        print '[*] {} test passed.'.format(test._testMethodName[5:])

    def addFailure(self, test, err):
        print '[!] {} test failed!'.format(test._testMethodName[5:])
        unittest.TestResult.addFailure(self, test, err)

class CustomTestRunner(unittest.TextTestRunner):

    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner, verbosity=0)
