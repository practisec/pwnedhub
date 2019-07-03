from itertools import izip, cycle
import base64

def xor_encrypt(s, k):
    return base64.b64encode(''.join([ chr(ord(c)^ord(k)) for c,k in izip(s, cycle(k)) ]))

def xor_decrypt(c, k):
    return ''.join([ chr(ord(c)^ord(k)) for c,k in izip(base64.b64decode(c), cycle(k)) ])

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
    ord(u'\\'): u'\\u005C',
    ord(u'\''): u'\\u0027',
    ord(u'"'): u'\\u0022',
    ord(u'>'): u'\\u003E',
    ord(u'<'): u'\\u003C',
    ord(u'&'): u'\\u0026',
    ord(u'='): u'\\u003D',
    ord(u'-'): u'\\u002D',
    ord(u';'): u'\\u003B',
    ord(u'`'): u'\\u0060',
    ord(u'\u2028'): u'\\u2028',
    ord(u'\u2029'): u'\\u2029'
}

# escape every ASCII character with a value less than 32.
_js_escapes.update((ord(u'%c' % z), u'\\u%04X' % z) for z in range(32))

def escapejs(value):
    """hex encode characters for use in JavaScript strings."""
    return unicode(value).translate(_js_escapes)
