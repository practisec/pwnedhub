from flask import current_app, url_for, session
from time import time
from urllib.parse import urlencode
import base64
import hashlib
import json
import os
import random
import requests

def generate_state(length=1024):
    """Generates a random string of characters."""
    return hashlib.sha256(os.urandom(1024)).hexdigest()

def generate_nonce(length=8):
    """Generates a pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def parse_jwt(token):
    """Parses the payload from a JWT."""
    jwt = token.split('.')
    return json.loads(base64.b64decode(jwt[1] + "==="))

def validate_id_token(token, provider, client, c_time, nonce=None):
    """Validates an ID Token."""
    # validate the issuer (provider)
    if token.get('iss') != provider:
        return False
    # validate the audience (client)
    if token.get('aud') != client:
        return False
    # validate the token's expiry
    if token.get('exp') <= c_time:
        return False
    # validate the anti-replay nonce's existence
    if nonce and not token.get('nonce'):
        return False
    # validate the anti-replay nonce's value
    if token.get('nonce') != nonce:
        return False
    return True

def get_provider_doc(url):
    try:
        return requests.get(url).json()
    except requests.exceptions.ConnectionError:
        pass
    return

class OAuthCallbackError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)

class OAuthSignIn(object):

    def __init__(self, provider):
        self.provider = provider
        p = current_app.config['OAUTH_PROVIDERS'][self.provider]
        self.client_id = p['CLIENT_ID']
        self.client_secret = p['CLIENT_SECRET']
        self.doc = get_provider_doc(p['DISCOVERY_DOC'])

    def authorize(self):
        # create an anti-forgery state token
        state = generate_state()
        session['state'] = state
        # create an anti-replay nonce
        nonce = generate_nonce()
        session['nonce'] = nonce
        payload = {
            'client_id': self.client_id,
            'response_type': 'code',
            # Google only shows an account picker form for this scope, as it
            # doubles as the consent form. Google shows a separate consent
            # form when a more sensitive scope is requested
            'scope': 'openid email profile',
            'redirect_uri': url_for('auth.oauth_callback', provider=self.provider, _external=True),
            'state': state,
            'nonce': nonce,
            'prompt': 'consent',
        }
        return '?'.join((self.doc['authorization_endpoint'], urlencode(payload)))

    def callback(self, request):
        # pop both values from the session to ensure
        # a full reset if state validation fails
        state = session.pop('state')
        nonce = session.pop('nonce')
        # validate the anti-forgery state token
        if request.args.get('state') == state:
            # exchange the code for an access token and ID token
            code = request.args.get('code')
            payload = {
                'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': url_for('auth.oauth_callback', provider=self.provider, _external=True),
                'grant_type': 'authorization_code',
            }
            resp = requests.post(self.doc['token_endpoint'], payload)
            if resp.status_code == requests.codes.ok:
                #access_token = resp.json().get('access_token')
                #user_resp = requests.get(self.doc['userinfo_endpoint'], headers={'Authorization': 'Bearer '+access_token})
                id_token = resp.json().get('id_token')
                # obtain payload information from the ID token
                jwt_payload = parse_jwt(id_token)
                # validate the received ID token
                if validate_id_token(
                        token=jwt_payload,
                        provider=self.doc['issuer'],
                        client=self.client_id,
                        c_time=time(),
                        nonce=nonce):
                    return jwt_payload
                else:
                    raise OAuthCallbackError('Invalid ID token.')
            else:
                raise OAuthCallbackError('Error contacting provider.')
        else:
            raise OAuthCallbackError('Invalid state parameter.')
        return {}
