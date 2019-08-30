from flask import current_app, g, request, session, redirect, url_for, abort, make_response, flash
from common.constants import ROLES
from functools import wraps
from threading import Thread
from urllib.parse import urlparse

def validate(params, method='POST'):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if request.method == method:
                for param in params:
                    valid = None
                    # iterate through all request inputs
                    for attr in ('args', 'form', 'files'):
                        valid = getattr(request, attr).get(param)
                        if valid:
                            break
                    if not valid:
                        flash('Required field(s) missing.')
                        return redirect(request.referrer)
            return func(*args, **kwargs)
        return wrapped
    return wrapper

def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        parsed_url = urlparse(request.url)
        location = parsed_url.path
        if parsed_url.query:
            location += '?{}'.format(parsed_url.query)
        return redirect(url_for('auth.login', next=location))
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

def csrf_protect(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if current_app.config['CSRF_PROTECT']:
            # only apply CSRF protection to POSTs
            if request.method == 'POST':
                csrf_token = session.pop('csrf_token', None)
                untrusted_token = request.values.get('csrf_token')
                if not csrf_token or untrusted_token != csrf_token:
                    return abort(400)
        return func(*args, **kwargs)
    return wrapped

def no_cache(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Expires'] = '0'
        return response
    return wrapped
