from datetime import datetime
from pydantic import BaseModel, validator, Field
from typing import Optional
import re


class CustomValidationException(ValueError):
    pass


class TokenData(BaseModel):
    user_id: Optional[int] = None


class BaseSchema(BaseModel):

    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class BaseDBSchema(BaseSchema):
    id: int
    #created: datetime
    #modified: datetime


class User(BaseDBSchema):
    username: str
    email: str
    name: str
    avatar: Optional[str] = None
    signature: Optional[str] = None
    role: str = Field(alias='role_as_string')
    status: str = Field(alias='status_as_string')
    class Config:
        orm_mode = True


class UserCreate(BaseSchema):
    username: str
    email: str
    name: str
    avatar: Optional[str] = None
    signature: Optional[str] = None
    password: str

    @validator('password')
    def password_strength(cls, password):
        PASSWORD_REGEX = r'.{8,}'
        if not re.match(r'^{}$'.format(PASSWORD_REGEX), password):
            raise CustomValidationException('Password does not meet complexity requirements.')
        return password


class UserUpdate(BaseSchema):
    username: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    signature: Optional[str] = None
    password: Optional[str] = None
