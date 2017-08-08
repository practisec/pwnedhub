from flask import current_app
import re

# anything except blank
PASSWORD_REGEX = r'.+'
EMAIL_REGEX = r'[^@]+@[a-zA-Z\d-]+(?:\.[a-zA-Z\d-]+)+'

def is_valid_quantity(quantity):
    return quantity.isdigit()

def is_valid_email(email):
    if not re.match(r'^{}$'.format(EMAIL_REGEX), email):
        return False
    return True

def is_valid_password(password):
    if not re.match(r'^{}$'.format(PASSWORD_REGEX), password):
        return False
    return True

def is_valid_file(filename):
    return any([x for x in current_app.config['ALLOWED_EXTENSIONS'] if '.'+x in filename])

from urlparse import urlparse, urljoin

def is_safe_url(url, origin):
    host = urlparse(origin).netloc
    proto = urlparse(origin).scheme
    # reject blank urls
    if not url:
        return False
    url = url.strip()
    url = url.replace('\\', '/')
    # simplify down to proto://, //, and /
    if url.startswith('///'):
        return False
    url_info = urlparse(url)
    # prevent browser manipulation via proto:///...
    if url_info.scheme and not url_info.netloc:
        return False
    # no proto for relative paths, or a matching proto for absolute paths
    if not url_info.scheme or url_info.scheme == proto:
        # no host for relative paths, or a matching host for absolute paths
        if not url_info.netloc or url_info.netloc == host:
            return True
    return False
