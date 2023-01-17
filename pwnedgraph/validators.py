import re

# 6 or more characters
PASSWORD_REGEX = r'.{8,}'

def is_valid_password(password):
    if not re.match(r'^{}$'.format(PASSWORD_REGEX), password):
        return False
    return True
