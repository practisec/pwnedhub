from fastapi.security import OAuth2PasswordBearer
from pwnedfast.config import settings
from pwnedfast.models import User
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional#, MutableMapping, List, Union
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='access-token')

def authenticate(*, username: str, password: str, db: Session,) -> Optional[User]:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if user and not user.check_password(password):
        return None
    if not user.is_enabled:
        return None
    return user

def encode_jwt(user_id, claims={}, expire_delta={'days': 1, 'seconds': 0}):
    payload = {
        'exp': datetime.utcnow() + timedelta(**expire_delta),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    for claim, value in claims.items():
        payload[claim] = value
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
