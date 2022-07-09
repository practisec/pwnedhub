from uuid import uuid4
import base64
import hashlib
import json
import os
import random

def get_bearer_token(headers):
    auth_header = headers.get('Authorization')
    if auth_header:
        return auth_header.split()[1]
    return None

def get_jaccard_sim(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

def generate_state(length=1024):
    """Generates a random string of characters."""
    return hashlib.sha256(os.urandom(length)).hexdigest()

def generate_nonce(length=8):
    """Generates a pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def generate_token():
    return str(uuid4())

def get_unverified_jwt_payload(token):
    """Parses the payload from a JWT."""
    jwt = token.split('.')
    return json.loads(base64.b64decode(jwt[1] + "==="))

# borrowed from Django and modified to work in Python 2

_js_escapes = {
    ord('\\'): '\\u005C',
    ord('\''): '\\u0027',
    ord('"'): '\\u0022',
    ord('>'): '\\u003E',
    ord('<'): '\\u003C',
    ord('&'): '\\u0026',
    ord('='): '\\u003D',
    ord('-'): '\\u002D',
    ord(';'): '\\u003B',
    ord('`'): '\\u0060',
    ord('\u2028'): '\\u2028',
    ord('\u2029'): '\\u2029'
}

# escape every ASCII character with a value less than 32.
_js_escapes.update((ord('%c' % z), '\\u%04X' % z) for z in range(32))

def escapejs(value):
    """hex encode characters for use in JavaScript strings."""
    # both str and bytes types have a translate method, but
    # the bytes method requires a bytes object for the map
    return value.decode().translate(_js_escapes)
