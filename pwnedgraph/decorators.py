from graphql import GraphQLError
from common.constants import ROLES
from functools import wraps

def auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if args[1].context.user:
            return func(*args, **kwargs)
        raise GraphQLError('Unauthorized.')
    return wrapped

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if ROLES[args[1].context.user.role] not in roles:
                raise GraphQLError('Forbidden.')
            return func(*args, **kwargs)
        return wrapped
    return wrapper
