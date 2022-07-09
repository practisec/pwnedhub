from flask import session
from common.utils import generate_token

def generate_csrf_token():
    session['csrf_token'] = generate_token()
    return session['csrf_token']
