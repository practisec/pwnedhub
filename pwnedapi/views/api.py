from flask import Blueprint, g, current_app, request, jsonify, abort, Response
from flask_restful import Resource, Api
from pwnedapi import db
from pwnedapi.utils import PaginationHelper, validate_json
from common.constants import ROLES, QUESTIONS, DEFAULT_NOTE, ADMIN_RESPONSE
from common.models import Config, User, Note, Message, Mail, Tool, Scan
from common.utils import get_unverified_jwt_payload, unfurl_url, send_email
from common.validators import is_valid_password, is_valid_command
from datetime import datetime, timedelta
from functools import wraps
from hashlib import md5
from itsdangerous import want_bytes
from secrets import token_urlsafe
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

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if ROLES[g.user.role] not in roles:
                return abort(403)
            return func(*args, **kwargs)
        return wrapped
    return wrapper

# API RESOURCE CLASSES

class TokenList(Resource):

    def post(self):
        '''Returns a JWT for the user that owns the provided credentials.'''
        id_token = request.json.get('id_token')
        username = request.json.get('username')
        password = request.json.get('password')
        user = None
        # process OIDC credentials
        if id_token:
            payload = get_unverified_jwt_payload(id_token)
            email = payload['email']
            user = User.get_by_email(email)
            if not user:
                # register the user
                user = User(
                    username=email.split('@')[0],
                    email=email,
                    avatar=payload['picture'],
                    signature='',
                    name=payload['name'],
                    password=token_urlsafe(20),
                    question=0,
                    answer=token_urlsafe(10),
                )
                db.session.add(user)
                db.session.commit()
        # process username and password credentials
        elif username and password:
            user = User.get_by_username(username)
            if user and not user.check_password(password):
                user = None
        # handle authentication
        if user and user.is_enabled:
            data = {'user': user.serialize_self()}
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
        abort(400, 'Invalid username or password.')

    def delete(self):
        response = Response(None, 204)
        response.delete_cookie('access_token')
        return response

api.add_resource(TokenList, '/access-token')


class UserList(Resource):

    @token_auth_required
    def get(self):
        users = [u.serialize() for u in User.query.all()]
        return {'users': users}

    def post(self):
        '''Creates an account.'''
        username = request.json.get('username')
        if User.query.filter_by(username=username).first():
            abort(400, 'Username already exists.')
        email = request.json.get('email')
        if User.query.filter_by(email=email).first():
            abort(400, 'Email already exists.')
        password = request.json.get('password')
        if not is_valid_password(password):
            abort(400, 'Password does not meet complexity requirements.')
        user = User(**request.json)
        db.session.add(user)
        db.session.commit()
        return {'success': True}, 201

api.add_resource(UserList, '/users')


class UserInst(Resource):

    @token_auth_required
    def get(self, uid):
        if uid == 'me' or uid == str(g.user.id):
            return g.user.serialize_self()
        user = User.query.get_or_404(uid)
        return user.serialize()

    @token_auth_required
    def patch(self, uid):
        if uid != 'me' and uid != str(g.user.id):
            abort(403)
        user = g.user
        user.name = request.json.get('name', user.name)
        user.avatar = request.json.get('avatar', user.avatar)
        user.signature = request.json.get('signature', user.signature)
        user.question = request.json.get('question', user.question)
        user.answer = request.json.get('answer', user.answer)
        db.session.add(user)
        db.session.commit()
        return user.serialize_self()

api.add_resource(UserInst, '/users/<string:uid>')


class AdminUserList(Resource):

    @token_auth_required
    @roles_required('admin')
    def get(self):
        users = [u.serialize_admin() for u in User.query.all()]
        return {'users': users}

api.add_resource(AdminUserList, '/admin/users')


class AdminUserInst(Resource):

    @token_auth_required
    @roles_required('admin')
    def patch(self, uid):
        user = User.query.get_or_404(uid)
        if user == g.user:
            abort(400, 'Self-administration not permitted.')
        print(request.json)
        user.role = request.json.get('role', user.role)
        user.status = request.json.get('status', user.status)
        db.session.add(user)
        db.session.commit()
        return user.serialize_admin()

api.add_resource(AdminUserInst, '/admin/users/<string:uid>')


class QuestionList(Resource):

    def get(self):
        questions = [{'id': index, 'text': value} for (index, value) in QUESTIONS.items()]
        return {'questions': questions}

api.add_resource(QuestionList, '/questions')


class PasswordResetList(Resource):

    def post(self):
        '''Creates and sends a password reset link.'''
        credential = request.json.get('credential')
        user = None
        if credential:
            user = User.get_by_email(credential) or User.get_by_username(credential)
        if not user or not user.is_enabled:
            abort(400, 'Invalid email address or username.')
        # create a JWT
        token = encode_jwt(user.id)
        # "send an email" with a reset link using the token
        base_url = request.headers['origin']
        link = f"{base_url}/#/reset/{user.id}/{token}"
        send_email(
            sender = User.query.first().email,
            recipient = user.email,
            subject = 'PwnedHub Password Reset',
            body = f"Hi {user.name}!<br><br>You recently requested to reset your PwnedHub password. Visit the following link to set a new password for your account.<br><br><a href=\"{link}\">{link}</a><br><br>If you did not request this password reset, please respond to this email to reach an administrator. Thank you.",
        )
        return {'success': True}, 201

api.add_resource(PasswordResetList, '/password-reset')


class PasswordInst(Resource):

    def put(self, uid):
        '''Updates a user's password.'''
        current_password = request.json.get('current_password')
        token = request.json.get('token')
        user = User.query.get_or_404(uid)
        new_password = None
        # process current password
        if current_password:
            if not g.user:
                abort(401)
            if user.id != g.user.id:
                abort(403)
            if not user.check_password(current_password):
                abort(400, 'Invalid current password.')
            new_password = request.json.get('new_password')
        # process reset token
        elif token:
            payload = get_unverified_jwt_payload(token)
            if payload['sub'] != user.id:
                abort(400, 'Invalid token.')
            new_password = request.json.get('new_password')
        # handle password update
        if not new_password:
            abort(400, 'Invalid request.')
        if not is_valid_password(new_password):
            abort(400, 'Password does not meet complexity requirements.')
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return {'success': True}

api.add_resource(PasswordInst, '/users/<string:uid>/password')


class NoteInst(Resource):

    @token_auth_required
    def get(self):
        #note = Note.query.get_or_404(mid)
        #if note.owner != g.user:
        #    abort(403)
        note = g.user.notes.first()
        content = note.content if note else DEFAULT_NOTE
        return {'content': content}

    @token_auth_required
    def put(self):
        note = g.user.notes.first()
        if not note:
            note = Note(name='Notes', owner=g.user)
        note.content = request.json.get('content')
        db.session.add(note)
        db.session.commit()
        return {'success': True}

api.add_resource(NoteInst, '/notes')


class MessageList(Resource):

    @token_auth_required
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=Message.query.order_by(Message.created.desc()),
            resource_for_url='resources.messagelist',
            key_name='messages'
        )
        result = pagination_helper.paginate_query()
        result['messages'].reverse()
        resp = jsonify(result)
        resp.mimetype = 'text/html'
        return resp

    @token_auth_required
    def post(self):
        jsonobj = request.get_json(force=True)
        comment = jsonobj.get('message')
        if not comment:
            abort(400, 'Invalid request.')
        message = Message(comment=comment, author=g.user)
        db.session.add(message)
        db.session.commit()
        result = message.serialize()
        resp = jsonify(result)
        resp.mimetype = 'text/html'
        return resp

api.add_resource(MessageList, '/messages')


class MessageInst(Resource):

    @token_auth_required
    def delete(self, mid):
        message = Message.query.get_or_404(mid)
        if message.author != g.user and not g.user.is_admin:
            abort(403)
        db.session.delete(message)
        db.session.commit()
        return '', 204

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
        # [Todo] this shouldn't work because only BaseQuery has update method
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


class ToolList(Resource):

    @token_auth_required
    def get(self):
        tools = [t.serialize() for t in Tool.query.all()]
        return {'tools': tools}

    @token_auth_required
    @roles_required('admin')
    @validate_json(['name', 'path', 'description'])
    def post(self):
        tool = Tool(
            name=request.json.get('name'),
            path=request.json.get('path'),
            description=request.json.get('description'),
        )
        db.session.add(tool)
        db.session.commit()
        return tool.serialize(), 201

api.add_resource(ToolList, '/tools')


class ToolInst(Resource):

    @token_auth_required
    def get(self, tid):
        query = 'SELECT id, name, path, description FROM tools WHERE id='+tid
        try:
            tool = db.session.execute(query).first() or {}
        except:
            tool = {}
        return dict(tool)

    @token_auth_required
    @roles_required('admin')
    def delete(self, tid):
        tool = Tool.query.get_or_404(tid)
        db.session.delete(tool)
        db.session.commit()
        return '', 204

api.add_resource(ToolInst, '/tools/<string:tid>')


class ScanList(Resource):

    @token_auth_required
    def get(self):
        scans = [s.serialize() for s in g.user.scans.order_by(Scan.created.asc())]
        return {'scans': scans}

    @token_auth_required
    @validate_json(['tid', 'args'])
    def post(self):
        tool = Tool.query.get(request.json.get('tid') or -1)
        if not tool:
            abort(400, 'Invalid tool ID.')
        path = tool.path
        args = request.json.get('args')
        cmd = '{} {}'.format(path, args)
        error = False
        if not is_valid_command(cmd):
            abort(400, 'Command contains invalid characters.')
        job = current_app.task_queue.enqueue('pwnedapi.tasks.execute_tool', cmd)
        sid = job.get_id()
        scan = Scan(id=sid, command=cmd, owner=g.user)
        db.session.add(scan)
        db.session.commit()
        return scan.serialize(), 201

api.add_resource(ScanList, '/scans')


class ScanInst(Resource):

    @token_auth_required
    def delete(self, sid):
        scan = Scan.query.get_or_404(sid)
        if scan.owner != g.user:
            abort(403)
        db.session.delete(scan)
        db.session.commit()
        return '', 204

api.add_resource(ScanInst, '/scans/<string:sid>')


class ResultsInst(Resource):

    @token_auth_required
    def get(self, sid):
        scan = Scan.query.get_or_404(sid)
        if scan.owner != g.user:
            abort(403)
        return {'results': scan.results}

api.add_resource(ResultsInst, '/scans/<string:sid>/results')


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
