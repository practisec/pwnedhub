from flask import g, request, current_app, abort
from pwnedapi.utils import CsrfToken, ParamValidator
from common.constants import ROLES
from common.models import Config
from functools import wraps
import base64
import pickle

def token_auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        abort(401)
    return wrapped

def key_auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        key = request.headers.get(current_app.config['API_CONFIG_KEY_NAME'])
        if key == current_app.config['API_CONFIG_KEY_VALUE']:
            return func(*args, **kwargs)
        abort(401)
    return wrapped

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if ROLES[g.user.role] not in roles:
                return abort(403)
            return func(*args, **kwargs)
        return wrapped
    return wrapper

def validate_json(params):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            input_dict = getattr(request, 'json', {})
            v = ParamValidator(input_dict, params)
            v.validate()
            if not v.passed:
                abort(400, v.reason)
            return func(*args, **kwargs)
        return wrapped
    return wrapper

def csrf_protect(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not Config.get_value('BEARER_AUTH_ENABLE'):
            # no Bearer token means cookies (default) are used and CSRF is an issue
            csrf_token = request.headers.get(current_app.config['CSRF_TOKEN_NAME'])
            try:
                csrf_obj = pickle.loads(base64.b64decode(csrf_token))
            except:
                csrf_obj = None
            if not csrf_obj or CsrfToken(g.user.id, csrf_obj.ts).sig != csrf_obj.sig:
                abort(400, 'CSRF detected.')
        return func(*args, **kwargs)
    return wrapped
