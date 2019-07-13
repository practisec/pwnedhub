from itertools import cycle
import base64

def xor_encrypt(s, k):
    ciphertext = ''.join([ chr(ord(c)^ord(k)) for c,k in zip(s, cycle(k)) ])
    return base64.b64encode(ciphertext.encode()).decode()

def xor_decrypt(c, k):
    ciphertext = base64.b64decode(c.encode()).decode()
    return ''.join([ chr(ord(c)^ord(k)) for c,k in zip(ciphertext, cycle(k)) ])

import binascii
import os

def get_token(n=40):
    return binascii.hexlify(os.urandom(n))

def get_jaccard_sim(str1, str2):
    a = set(str1.split())
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))

from lxml import etree
import requests

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
