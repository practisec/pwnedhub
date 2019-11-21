from flask import Blueprint, g, current_app, request, jsonify, abort, Response
from flask_restful import Resource, Api
from pwnedapi import db
from common.constants import ADMIN_RESPONSE
from common.models import Config, User, Message, Mail, Tool
from common.utils import get_unverified_jwt_payload, unfurl_url
from common.validators import is_valid_command
from datetime import datetime, timedelta
from functools import wraps
from hashlib import md5
from itsdangerous import want_bytes
from lxml import etree
import jwt
import os
import pickle
import subprocess

resources = Blueprint('resources', __name__)
api = Api()
api.init_app(resources)

# UTILITY FUNCTIONS

def encode_jwt(user_id, claims={}):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    for claim, value in claims.items():
        payload[claim] = value
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    ).decode()

def get_bearer_token(headers):
    auth_header = headers.get('Authorization')
    if auth_header:
        return auth_header.split()[1]
    return None

# PRE-REQUEST FUNCTIONS

@resources.before_app_request
def parse_jwt():
    request.jwt = {}
    token = request.cookies.get('access_token')
    if Config.get_value('BEARER_AUTH_ENABLE'):
        token = get_bearer_token(request.headers)
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'])
    except:
        return
    request.jwt = payload

@resources.before_app_request
def load_user():
    g.user = None
    uid = request.jwt.get('sub')
    if uid:
        g.user = User.query.get(uid)

# DECORATOR FUNCTIONS

def token_auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        abort(401)
    return wrapped

def key_auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        key = request.headers.get(current_app.config['API_CONFIG_KEY_NAME'])
        if key == current_app.config['API_CONFIG_KEY_VALUE']:
            return func(*args, **kwargs)
        abort(401)
    return wrapped

# API RESOURCE CLASSES


class TokenList(Resource):

    def post(self):
        '''Returns a JWT for the user that owns the provided credentials.'''
        id_token = request.json.get('id_token')
        username = request.json.get('username')
        password = request.json.get('password')
        user = None
        if id_token:
            payload = get_unverified_jwt_payload(id_token)
            user = User.get_by_email(payload['email'])
        elif username and password:
            user = User.get_by_username(username)
            if user and not user.check_password(password):
                user = None
        if user and user.is_enabled:
            data = {'user': user.serialize()}
            # build other claims
            claims = {}
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], md5(str(user.id).encode()).hexdigest())
            if not os.path.exists(path):
                os.makedirs(path)
            claims['upload_folder'] = path
            # create a JWT
            token = encode_jwt(user.id, claims=claims)
            # send the JWT as a Bearer token when the feature is enabled
            if Config.get_value('BEARER_AUTH_ENABLE'):
                data['token'] = token
                # remove any existing access token cookie
                return data, 200, {'Set-Cookie': 'access_token=; Expires=Thu, 01-Jan-1970 00:00:00 GMT'}
            # set the JWT as a HttpOnly cookie by default
            return data, 200, {'Set-Cookie': 'access_token='+token+'; HttpOnly'}
        return {'message': 'Invalid username or password.'}

    def delete(self):
        response = Response(None, 204)
        response.delete_cookie('access_token')
        return response

api.add_resource(TokenList, '/access-token')


class UserList(Resource):

    @token_auth_required
    def get(self):
        users = [u.serialize(public=True) for u in User.query.all()]
        return {'users': users}

api.add_resource(UserList, '/users')


class UserInst(Resource):

    @token_auth_required
    def get(self, uid):
        if uid == 'me' or uid == str(g.user.id):
            return g.user.serialize()
        user = User.query.get_or_404(uid)
        return user.serialize(public=True)

    @token_auth_required
    def patch(self, uid):
        User.query.filter_by(id=g.user.id).update(request.json)
        db.session.commit()
        return g.user.serialize()

api.add_resource(UserInst, '/users/<string:uid>')


class MessageList(Resource):

    @token_auth_required
    def get(self):
        messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
        resp = jsonify(messages=messages)
        resp.mimetype = 'text/html'
        return resp

    @token_auth_required
    def post(self):
        jsonobj = request.get_json(force=True)
        message = jsonobj.get('message')
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
        messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
        resp = jsonify(messages=messages)
        resp.mimetype = 'text/html'
        return resp

api.add_resource(MessageList, '/messages')


class MessageInst(Resource):

    @token_auth_required
    def delete(self, mid):
        message = Message.query.get_or_404(mid)
        if message.user != g.user and not g.user.is_admin:
            abort(403)
        db.session.delete(message)
        db.session.commit()
        messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
        return {'messages': messages}

api.add_resource(MessageInst, '/messages/<string:mid>')


class MailList(Resource):

    @token_auth_required
    def get(self):
        mail = [m.serialize() for m in g.user.received_mail.order_by(Mail.created.desc()).all()]
        return {'mail': mail}

    @token_auth_required
    def post(self):
        receiver = User.query.get(request.json.get('receiver'))
        if not receiver:
            abort(400, 'Invalid receiver.')
        subject = request.json.get('subject')
        content = request.json.get('content')
        letter = Mail(
            content=content,
            subject=subject,
            sender=g.user,
            receiver=receiver,
        )
        db.session.add(letter)
        db.session.commit()
        # generate automated Administrator response
        if receiver.role == 0:
            content = ADMIN_RESPONSE
            auto_letter = Mail(
                content=content,
                subject='RE:'+subject,
                sender=receiver,
                receiver=g.user,
            )
            db.session.add(auto_letter)
            db.session.commit()
        return letter.serialize()

api.add_resource(MailList, '/mail')


class MailInst(Resource):

    @token_auth_required
    def get(self, mid):
        mail = Mail.query.get_or_404(mid)
        if mail.receiver != g.user:
            abort(403)
        # mark mail as read
        if mail.read == 0:
            mail.read = 1
            db.session.add(mail)
            db.session.commit()
        return mail.serialize()

    @token_auth_required
    def patch(self, mid):
        mail = Mail.query.get_or_404(mid)
        if mail.receiver != g.user:
            abort(403)
        mail.update(request.json)
        db.session.commit()
        return mail.serialize()

    @token_auth_required
    def delete(self, mid):
        mail = Mail.query.get_or_404(mid)
        if mail.receiver != g.user:
            abort(403)
        db.session.delete(mail)
        db.session.commit()
        mail = [m.serialize() for m in g.user.received_mail.order_by(Mail.created.desc()).all()]
        return {'mail': mail}

api.add_resource(MailInst, '/mail/<string:mid>')


class UnfurlList(Resource):

    def post(self):
        url = request.json.get('url')
        headers = {'User-Agent': request.headers.get('User-Agent')}
        if url:
            try:
                data = unfurl_url(url, headers)
                status = 200
            except Exception as e:
                data = {'error': 'UnfurlError', 'message': str(e)}
                status = 500
        else:
            data = {'error': 'RequestError', 'message': 'Invalid request.'}
            status = 400
        return data, status

api.add_resource(UnfurlList, '/unfurl')


class ToolInst(Resource):

    @token_auth_required
    def get(self, tid):
        query = 'SELECT id, name, path, description FROM tools WHERE id='+tid
        try:
            tool = db.session.execute(query).first() or {}
        except:
            tool = {}
        return dict(tool)

api.add_resource(ToolInst, '/tools/<string:tid>')


class ExecuteList(Resource):

    @token_auth_required
    def post(self):
        tool = Tool.query.get(request.json.get('tid') or -1)
        if not tool:
            abort(400, 'Invalid tool ID.')
        path = tool.path
        args = request.json.get('args')
        cmd = '{} {}'.format(path, args)
        error = False
        if is_valid_command(cmd):
            env = os.environ.copy()
            env['PATH'] = os.pathsep.join(('/usr/bin', env['PATH']))
            p = subprocess.Popen([cmd, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            out, err = p.communicate()
            output = (out + err).decode()
        else:
            output = 'Command contains invalid characters.'
            error = True
        return {'cmd': cmd, 'output': output, 'error': error}

api.add_resource(ExecuteList, '/execute')


class ArtifactsList(Resource):

    @token_auth_required
    def post(self):
        xml = request.data
        parser = etree.XMLParser(no_network=False)
        doc = etree.fromstring(xml, parser)
        content = doc.find('content').text
        filename = doc.find('filename').text
        if all((content, filename)):
            filename += '-{}.txt'.format(datetime.now().strftime('%s'))
            msg = 'Artifact created \'{}\'.'.format(filename)
            path = os.path.join(request.jwt.get('upload_folder'), filename)
            if not os.path.isfile(path):
                try:
                    with open(path, 'w') as fp:
                        fp.write(content)
                except IOError:
                    msg = 'Unable to save as an artifact.'
            else:
                msg = 'An artifact with that name already exists.'
        else:
            msg = 'Invalid request.'
        xml = '<xml><message>{}</message></xml>'.format(msg)
        return Response(xml, mimetype='application/xml')

api.add_resource(ArtifactsList, '/artifacts')
