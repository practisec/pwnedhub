def detect_user_agent(s):
    if any([x for x in ('iphone', 'ipad', 'android') if x in s.lower()]):
        return 'Mobile coming soon!'
    elif any([x for x in ('googlebot', 'bingbot') if x in s.lower()]):
        return 'Nothing to see here, bot. Move along.'

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
