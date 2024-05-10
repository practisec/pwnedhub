from flask import current_app
from datetime import datetime, timezone, timedelta
from itertools import cycle
import base64
import jwt

def get_current_utc_time():
    return datetime.now(timezone.utc)

def get_local_from_utc(dtg):
    return dtg.replace(tzinfo=timezone.utc).astimezone(tz=None)

def xor_encrypt(s, k):
    ciphertext = ''.join([ chr(ord(c)^ord(k)) for c,k in zip(s, cycle(k)) ])
    return base64.b64encode(ciphertext.encode()).decode()

def encode_jwt(user_id, claims={}, expire_delta={'days': 1, 'seconds': 0}):
    payload = {
        'exp': get_current_utc_time() + timedelta(**expire_delta),
        'iat': get_current_utc_time(),
        'sub': user_id
    }
    for claim, value in claims.items():
        payload[claim] = value
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
