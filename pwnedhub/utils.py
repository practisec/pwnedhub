from flask import session
from datetime import datetime, timezone
from hashlib import md5
from itertools import cycle
from lxml import etree
from uuid import uuid4
import base64
import hashlib
import os
import random
import requests

def get_current_utc_time():
    return datetime.now(tz=timezone.utc)

def get_local_from_utc(dtg):
    return dtg.replace(tzinfo=timezone.utc).astimezone(tz=None)

def xor_encrypt(s, k):
    ciphertext = ''.join([ chr(ord(c)^ord(k)) for c,k in zip(s, cycle(k)) ])
    return base64.b64encode(ciphertext.encode()).decode()

def xor_decrypt(c, k):
    ciphertext = base64.b64decode(c.encode()).decode()
    return ''.join([ chr(ord(c)^ord(k)) for c,k in zip(ciphertext, cycle(k)) ])

def generate_state(length=1024):
    """Generates a random string of characters."""
    return hashlib.sha256(os.urandom(length)).hexdigest()

def generate_nonce(length=8):
    """Generates a pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def generate_token():
    return str(uuid4())

def generate_timestamp_token():
    return md5(str(int(get_current_utc_time().timestamp()*100)).encode()).hexdigest()

def generate_csrf_token():
    session['csrf_token'] = generate_token()
    return session['csrf_token']

def unfurl_url(url, headers={}):
    # request resource
    resp = requests.get(url, headers=headers)
    # parse meta tags
    html = etree.HTML(resp.content)
    data = {'url': url}
    for kw in ('site_name', 'title', 'description'):
        # standard
        prop = kw
        values = html.xpath('//meta[@property=\'{}\']/@content'.format(prop))
        data[kw] = ' '.join(values) or None
        # OpenGraph
        prop = 'og:{}'.format(kw)
        values = html.xpath('//meta[@property=\'{}\']/@content'.format(prop))
        data[kw] = ' '.join(values) or None
    return data
