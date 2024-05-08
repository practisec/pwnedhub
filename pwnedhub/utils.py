from flask import session, current_app
from pwnedhub.constants import EMAIL_TEMPLATE
from datetime import datetime
from hashlib import md5
from itertools import cycle
from lxml import etree
from uuid import uuid4
import base64
import hashlib
import os
import random
import requests

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
    return md5(str(int(datetime.now().timestamp()*100)).encode()).hexdigest()

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

def send_email(sender, recipient, subject, body):
    # check for and create an inbox folder
    inbox = f"{current_app.config['INBOX_PATH']}/{recipient}"
    if not os.path.exists(inbox):
        os.makedirs(inbox)
    # create a filename based on the subject and nonce
    filename = f"{subject} {generate_nonce(6)}.html".replace(' ', '_')
    # write the email to a file
    filepath = os.path.join(inbox, filename)
    email = EMAIL_TEMPLATE.format(sender=sender, recipient=recipient, subject=subject, body=body)
    with open(filepath, 'w') as fp:
        fp.write(email)
    return filepath
