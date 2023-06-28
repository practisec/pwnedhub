from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pwnedfast.auth import authenticate, encode_jwt
from pwnedfast.config import settings
from pwnedfast import deps
from pwnedfast import schemas
from pwnedfast import models
from pwnedfast import crud
from sqlalchemy.orm import Session

auth_router = APIRouter(
    prefix='/access-token',
)

@auth_router.post('', status_code=201)
def create_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session= Depends(deps.get_db)):
    '''
    Create an access token.
    '''
    user = authenticate(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=400,
            detail='Incorrect username or password'
        )
    token = encode_jwt(user.id, claims={})
    # send the JWT as a cookie when the feature is enabled
    if not True:#Config.get_value('BEARER_AUTH_ENABLE'):
        # return a CSRF token when using cookie authentication
        csrf_obj = CsrfToken(user.id)
        csrf_obj.sign(current_app.config['SECRET_KEY'])
        data['csrf_token'] = csrf_obj.serialize()
        # set the JWT as a HttpOnly cookie
        return data, 201, {'Set-Cookie': f"access_token={token}; HttpOnly"}
    # default to Bearer token authentication
    return  {
        'user': user,
        'access_token': token,
        #'token_type': 'bearer',
    }

users_router = APIRouter(
    prefix='/users',
)

@users_router.get('', response_model=list[schemas.User], response_model_by_alias=False)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    '''
    Fetch all users.
    '''
    users = crud.user.get_many(db, skip=skip, limit=limit)
    return users

@users_router.get("/me", response_model=schemas.User, response_model_by_alias=False)
def read_user_me(current_user: models.User = Depends(deps.get_current_user)):
    '''
    Fetch the current logged in user.
    '''
    user = current_user
    return user

@users_router.get('/{user_id}', response_model=schemas.User, response_model_by_alias=False)
def read_user(user_id: int, db: Session = Depends(deps.get_db)):
    '''
    Fetch a single user.
    '''
    user = crud.user.get(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f'User with ID {user_id} not found.'
        )
    return user

@users_router.post('', status_code=201, response_model=schemas.User, response_model_by_alias=False)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    '''
    Create a new user.
    '''
    if db.query(models.User).filter_by(username=user_in.username).first():
        raise HTTPException(
            status_code=400,
            detail='Username already exists.'
        )
    if db.query(models.User).filter_by(email=user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail='Email already exists.'
        )
    return crud.user.create(db=db, obj_in=user_in)
