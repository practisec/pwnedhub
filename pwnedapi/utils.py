from flask import current_app, url_for
from datetime import datetime, timedelta
from hashlib import md5
from lxml import etree
import base64
import hmac
import jsonpickle
import jwt
import random
import requests

def generate_code(length=6):
    """Generates a pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

def get_bearer_token(headers):
    auth_header = headers.get('Authorization')
    if auth_header:
        return auth_header.split()[1]
    return None

def encode_jwt(subscriber, claims={}, expire_delta={'days': 1, 'seconds': 0}):
    payload = {
        'exp': datetime.now() + timedelta(**expire_delta),
        'iat': datetime.now(),
        'sub': subscriber
    }
    for claim, value in claims.items():
        payload[claim] = value
    from pwnedapi.models import Config
    if Config.get_value('JWT_ENCRYPT'):
        return encrypt_jwt(jwt.encode(payload, key=current_app.config['SECRET_KEY'], algorithm='HS256'))
    return jwt.encode(payload, key=current_app.config['SECRET_KEY'], algorithm='HS256')

def decode_jwt(token, options={}):
    from pwnedapi.models import Config
    if Config.get_value('JWT_ENCRYPT'):
        return jwt.decode(decrypt_jwt(token), key=current_app.config['SECRET_KEY'], algorithms=['HS256'], options=options)
    return jwt.decode(token, key=current_app.config['SECRET_KEY'], algorithms=['HS256'], options=options)

from jwcrypto import jwt as _jwt, jwk
import hashlib

def encrypt_jwt(signed_token):
    secret_key = hashlib.md5(current_app.config['SECRET_KEY'].encode('utf-8')).hexdigest()
    key = jwk.JWK.from_password(secret_key)
    encrypted_token = _jwt.JWT(header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=signed_token)
    encrypted_token.make_encrypted_token(key)
    return encrypted_token.serialize()

def decrypt_jwt(encrypted_token):
    secret_key = hashlib.md5(current_app.config['SECRET_KEY'].encode('utf-8')).hexdigest()
    key = jwk.JWK.from_password(secret_key)
    decrypted_token = _jwt.JWT(key=key, jwt=encrypted_token, expected_type="JWE")
    return decrypted_token.claims

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


class CsrfToken(object):

    def __init__(self, uid, ts=None):
        self.uid = uid
        self.ts = ts or int(datetime.now().timestamp())
        self.sig = None

    def sign(self, key):
        body = f"{self.uid}{self.ts}"
        self.sig = hmac.new(key.encode(), body.encode(), md5).hexdigest()

    def serialize(self):
        if not self.sig:
            raise ValueError('Token signature missing.')
        return base64.b64encode(jsonpickle.encode(self).encode()).decode()


class ParamValidator(object):

    def __init__(self, input_dict, params):
        self.input_dict = input_dict
        self.params = params
        self.passed = True
        self.failed_params = []

    @property
    def reason(self):
        if not self.failed_params:
            return 'Validation successful.'
        else:
            return f"Required field(s) missing or invalid: {', '.join(self.failed_params)}"

    def validate(self):
        for param in self.params:
            value = self.input_dict.get(param)
            func = getattr(self, 'validate_'+param, self.validator_missing)
            if not func(value):
                self.passed = False
                self.failed_params.append(param)

    def validator_missing(self, *args, **kwargs):
        return False

    def any_int(self, value):
        try:
            value = int(value)
            return True
        except:
            pass
        return False

    def non_zero_len_str(self, value):
        return isinstance(value, str) and len(value) > 0

    def boolean(self, value):
        return isinstance(value, bool)

    def array_of_ints(self, value):
        if isinstance(value, list):
            return all(isinstance(x, int) for x in value)
        return False

    validate_tid = any_int
    validate_args = validate_name = validate_email = validate_path = validate_description = validate_content = non_zero_len_str


class PaginationHelper():

    def __init__(self, request, query, resource_for_url, key_name):
        self.request = request
        self.query = query
        self.resource_for_url = resource_for_url
        self.key_name = key_name

    def paginate_query(self):
        # If no page number is specified, we assume the request wants page #1
        size = self.request.args.get('size', 8, type=int)
        page_number = self.request.args.get('page', 1, type=int)
        paginated_objects = self.query.paginate(
            page_number,
            per_page=size,
            error_out=False)
        objects = paginated_objects.items
        if paginated_objects.has_prev:
            previous_page_url = url_for(
                self.resource_for_url,
                page=page_number-1,
                size=size,
                _external=True)
        else:
            previous_page_url = None
        if paginated_objects.has_next:
            next_page_url = url_for(
                self.resource_for_url,
                page=page_number+1,
                size=size,
                _external=True)
        else:
            next_page_url = None
        dumped_objects = [o.serialize() for o in objects]
        return ({
            self.key_name: dumped_objects,
            'previous': previous_page_url,
            'next': next_page_url,
            'count': paginated_objects.total
        })
