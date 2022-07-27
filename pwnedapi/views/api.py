from flask import Blueprint, g, current_app, request, jsonify, abort, Response, url_for
from flask_restful import Resource, Api
from pwnedapi import db
from pwnedapi.decorators import token_auth_required, roles_required, validate_json, csrf_protect
from pwnedapi.utils import CsrfToken, send_email
from common.constants import DEFAULT_NOTE_V2
from common.models import Config, User, Note, Message, Tool, Scan, Room
from common.utils import get_bearer_token, get_unverified_jwt_payload
from common.utils.unfurl import unfurl_url
from common.utils.jwt import encode_jwt
from common.validators import is_valid_password, is_valid_command
from datetime import datetime
from hashlib import md5
from secrets import token_urlsafe
import jwt
import os

resources = Blueprint('resources', __name__)
api = Api()
api.init_app(resources)

# PRE-REQUEST FUNCTIONS

@resources.before_app_request
def parse_jwt():
    request.jwt = {}
    token = request.cookies.get('access_token')
    if Config.get_value('BEARER_AUTH_ENABLE'):
        token = get_bearer_token(request.headers)
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        return
    request.jwt = payload

@resources.before_app_request
def load_user():
    g.user = None
    uid = request.jwt.get('sub')
    if uid:
        g.user = User.query.get(uid)

# API RESOURCE CLASSES

class TokenList(Resource):

    def post(self):
        '''Returns a JWT for the user that owns the provided credentials.'''
        json_data = request.get_json(force=True)
        id_token = json_data.get('id_token')
        username = json_data.get('username')
        password = json_data.get('password')
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
                data['access_token'] = token
                # remove any existing access token cookie
                return data, 201, {'Set-Cookie': 'access_token=; Expires=Thu, 01-Jan-1970 00:00:00 GMT'}
            # default to cookie authentication
            # return a CSRF token when using cookie authentication
            csrf_obj = CsrfToken(user.id)
            csrf_obj.sign(current_app.config['SECRET_KEY'])
            data['csrf_token'] = csrf_obj.serialize()
            # set the JWT as a HttpOnly cookie
            return data, 201, {'Set-Cookie': f"access_token={token}; HttpOnly"}
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

    @validate_json(['username', 'email', 'name', 'password'])
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
    @csrf_protect
    @validate_json(['username', 'email', 'name'])
    def patch(self, uid):
        if uid != 'me' and uid != str(g.user.id):
            abort(403)
        user = g.user
        # validate that the provided username doesn't belong to another user
        username = request.json.get('username', user.username)
        untrusted_user = User.query.filter_by(username=username).first()
        if untrusted_user and untrusted_user != g.user:
            abort(400, 'Username already exists.')
        # validate that the provided email doesn't belong to another user
        email = request.json.get('email', user.email)
        untrusted_user = User.query.filter_by(email=email).first()
        if untrusted_user and untrusted_user != g.user:
            abort(400, 'Email already exists.')
        # update the user object
        user.username = username
        user.email = email
        user.name = request.json.get('name', user.name)
        user.avatar = request.json.get('avatar', user.avatar)
        user.signature = request.json.get('signature', user.signature)
        db.session.add(user)
        db.session.commit()
        return user.serialize_self()

api.add_resource(UserInst, '/users/<string:uid>')


class AdminUserInst(Resource):

    @token_auth_required
    @roles_required('admin')
    def patch(self, uid):
        user = User.query.get_or_404(uid)
        if user == g.user:
            abort(400, 'Self-administration not permitted.')
        user.role = request.json.get('role', user.role)
        user.status = request.json.get('status', user.status)
        db.session.add(user)
        db.session.commit()
        return user.serialize()

api.add_resource(AdminUserInst, '/admin/users/<string:uid>')


class PasswordResetList(Resource):

    @validate_json(['credential'])
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
        note = g.user.notes.first()
        content = note.content if note else DEFAULT_NOTE_V2
        return {'content': content}

    @token_auth_required
    @validate_json(['content'])
    def put(self):
        note = g.user.notes.first()
        if not note:
            note = Note(name='Notes', owner=g.user)
        note.content = request.json.get('content')
        db.session.add(note)
        db.session.commit()
        return {'success': True}

api.add_resource(NoteInst, '/notes')


class RoomList(Resource):

    @token_auth_required
    def get(self):
        rooms = [r.serialize_with_context(g.user) for r in g.user.rooms]
        return {'rooms': rooms}

    @token_auth_required
    @validate_json(['name', 'private', 'members'])
    def post(self):
        name = request.json.get('name')
        private = request.json.get('private')
        members = request.json.get('members')
        room = Room.get_by_name(name)
        code = 200
        if not room:
            # create the room
            room = Room(
                name=name,
                private=private,
            )
            db.session.add(room)
            db.session.commit()
            # initialize memberships
            for member in members:
                user = User.query.get(member)
                user.create_membership(room)
            code = 201
            # TODO: if private, emit socket message for all users to update rooms
        return room.serialize_with_context(g.user), code

api.add_resource(RoomList, '/rooms')


class RoomMessageList(Resource):

    @token_auth_required
    def get(self, rid):
        room = Room.query.get_or_404(rid)
        if room not in g.user.rooms:
            abort(403)
        result = {
            'messages': [],
            'cursor': None,
            'next': None,
        }
        cursor = float(request.args.get('cursor', datetime.now().timestamp()))
        size = request.args.get('size', 8)
        messages = room.messages.filter(Message.created < datetime.fromtimestamp(cursor)).order_by(Message.created.desc()).all()
        if messages:
            paged_messages = messages[:size]
            next_cursor = str(paged_messages[-1].created.timestamp())
            next_url = None
            if messages[-1].created < paged_messages[-1].created:
                next_url = url_for('resources.roommessagelist', rid=room.id, cursor=next_cursor, _external=True)
            paged_messages.reverse()
            result = {
                'messages': [m.serialize() for m in paged_messages],
                'cursor': next_cursor,
                'next': next_url,
            }
        resp = jsonify(result)
        resp.mimetype = 'text/html'
        return resp

api.add_resource(RoomMessageList, '/rooms/<string:rid>/messages')


class UnfurlList(Resource):

    def post(self):
        url = request.json.get('url')
        headers = {}
        if url:
            try:
                data = unfurl_url(url, headers)
                status = 201
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
