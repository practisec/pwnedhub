from flask import Blueprint, request, redirect
from pwnedsso.models import User
from pwnedsso.utils import encode_jwt
from urllib.parse import urlencode

blp = Blueprint('sso', __name__)

# sso controllers

@blp.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    user = None
    if username and password:
        untrusted_user = User.get_by_username(username)
        if untrusted_user and untrusted_user.check_password(password):
            user = untrusted_user
    params = {}
    params['id_token'] = encode_jwt(user.username if user else None)
    if 'next' in request.args:
        params['next'] = request.args.get('next')
    redirect_url = '?'.join(['http://www.pwnedhub.com/sso/login', urlencode(params)])
    return redirect(redirect_url)
