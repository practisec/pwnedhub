from pwnedapi.models import Config
import re

# 8 or more characters
PASSWORD_REGEX = r'.{8,}'

def is_valid_command(cmd):
    pattern = r'[;&|]'
    if Config.get_value('OSCI_PROTECT'):
        pattern = r'[;&|<>`$(){}]'
    if re.search(pattern, cmd):
        return False
    return True

def is_valid_password(password):
    if not re.match(r'^{}$'.format(PASSWORD_REGEX), password):
        return False
    return True
