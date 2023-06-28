from itertools import cycle
import base64

def xor_encrypt(s, k):
    ciphertext = ''.join([ chr(ord(c)^ord(k)) for c,k in zip(s, cycle(k)) ])
    return base64.b64encode(ciphertext.encode()).decode()

def xor_decrypt(c, k):
    ciphertext = base64.b64decode(c.encode()).decode()
    return ''.join([ chr(ord(c)^ord(k)) for c,k in zip(ciphertext, cycle(k)) ])
