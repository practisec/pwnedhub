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
