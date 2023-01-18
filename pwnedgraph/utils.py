from flask import current_app
from datetime import datetime, timedelta
from itertools import cycle
import base64
import jwt

def xor_encrypt(s, k):
    ciphertext = ''.join([ chr(ord(c)^ord(k)) for c,k in zip(s, cycle(k)) ])
    return base64.b64encode(ciphertext.encode()).decode()

def xor_decrypt(c, k):
    ciphertext = base64.b64decode(c.encode()).decode()
    return ''.join([ chr(ord(c)^ord(k)) for c,k in zip(ciphertext, cycle(k)) ])

def get_bearer_token(headers):
    auth_header = headers.get('Authorization')
    if auth_header:
        return auth_header.split()[1]
    return None

def encode_jwt(user_id, claims={}, expire_delta={'days': 1, 'seconds': 0}):
    payload = {
        'exp': datetime.utcnow() + timedelta(**expire_delta),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    for claim, value in claims.items():
        payload[claim] = value
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
