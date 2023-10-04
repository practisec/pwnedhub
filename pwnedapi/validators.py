from pwnedapi.models import Config
import re

def is_valid_command(cmd):
    pattern = r'[;&|]'
    if Config.get_value('OSCI_PROTECT'):
        pattern = r'[;&|<>`$(){}]'
    if re.search(pattern, cmd):
        return False
    return True
