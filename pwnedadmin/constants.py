RESTRICTED_USERS = [
    'admin@pwnedhub.com',
    'cooper@pwnedhub.com',
    'taylor@pwnedhub.com',
    'tanner@pwnedhub.com',
    'emilee@pwnedhub.com',
]

class ConfigTypes:
    CONTROL = 'security control'
    FEATURE = 'feature'

    def __init__(self):
        pass

    @property
    def serialized(self):
        return [self.CONTROL, self.FEATURE]
