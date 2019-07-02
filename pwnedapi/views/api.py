from flask import Blueprint, g, current_app, session, request, jsonify, abort, Response
from flask_restful import Resource, Api
from pwnedapi import db
from common.constants import ADMIN_RESPONSE
from common.models import User, Message, Mail, Tool
from common.utils import unfurl_url
from common.validators import is_valid_command
from datetime import datetime, timedelta
from functools import wraps
from hashlib import md5
from itsdangerous import want_bytes
from lxml import etree
import jwt
import os
import subprocess
try:
    import cPickle as pickle
except ImportError:
    import pickle

endpoints = Blueprint('endpoints', __name__)
api = Api()
api.init_app(endpoints)

# UTILITY FUNCTIONS

def encode_jwt(user_id, claims={}):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    for claim, value in claims.iteritems():
        payload[claim] = value
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

# PRE-REQUEST FUNCTIONS

@endpoints.before_app_request
def parse_jwt():
    request.jwt = {}
    token = request.cookies.get('access_token')
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'])
    except:
        return
    request.jwt = payload

@endpoints.before_app_request
def load_user():
    g.user = None
    uid = request.jwt.get('sub')
    if uid:
        g.user = User.query.get(uid)

# DECORATOR FUNCTIONS

def auth_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        abort(401)
    return wrapped


# API RESOURCE CLASSES

class TokenList(Resource):

    def post(self):
        '''Returns a JWT for the user that owns the provided session.'''
        # customized for the configuration of pwnedhub sessions
        # if something changes there, it needs to change here
        session_token = request.json.get('session') or abort(400)
        # no Session model is available for stored sessions
        # so query safely using parameterized execute calls
        query = 'SELECT data, expiry FROM sessions WHERE session_id=:sid'
        rows = db.session.execute(query, {'sid': 'session:'+session_token}).first()
        if not rows:
            return {'message': 'Invalid session.'}, 401
        expired = rows[1] < datetime.now()
        if expired:
            return {'message': 'Session expired.'}, 401
        data = pickle.loads(want_bytes(rows[0]))
        user = User.query.get(data['user_id'])
        # build other claims
        claims = {}
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], md5(str(data['user_id'])).hexdigest())
        if not os.path.exists(path):
            os.makedirs(path)
        claims['upload_folder'] = path
        # create a JWT and set it as a HttpOnly cookie for the api
        token = encode_jwt(user.id, claims=claims)
        return user.serialize(), 200, {'Set-Cookie': 'access_token='+token+'; HttpOnly'}

api.add_resource(TokenList, '/access-token')


class UserList(Resource):

    @auth_required
    def get(self):
        users = [u.serialize(public=True) for u in User.query.all()]
        return {'users': users}

api.add_resource(UserList, '/users')


class UserInst(Resource):

    @auth_required
    def get(self, uid):
        if uid == 'me' or uid == str(g.user.id):
            return g.user.serialize()
        user = User.query.get_or_404(uid)
        return user.serialize(public=True)

    @auth_required
    def patch(self, uid):
        #[vuln] mass assignment here now too!
        User.query.filter_by(id=g.user.id).update(request.json)
        db.session.commit()
        return g.user.serialize()

api.add_resource(UserInst, '/users/<string:uid>')


class MessageList(Resource):

    @auth_required
    def get(self):
        messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
        resp = jsonify(messages=messages)
        resp.mimetype = 'text/html'
        return resp

    @auth_required
    def post(self):
        jsonobj = request.get_json(force=True)
        message = jsonobj.get('message')
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
        messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
        return {'messages': messages}

api.add_resource(MessageList, '/messages')


class MessageInst(Resource):

    @auth_required
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

    @auth_required
    def get(self):
        mail = [m.serialize() for m in g.user.received_mail.order_by(Mail.created.desc()).all()]
        return {'mail': mail}

    @auth_required
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

    @auth_required
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

    @auth_required
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

    @auth_required
    def get(self, tid):
        query = 'SELECT id, name, path, description FROM tools WHERE id='+tid
        try:
            tool = db.session.execute(query).first() or {}
        except:
            tool = {}
        return dict(tool)

api.add_resource(ToolInst, '/tools/<string:tid>')


class ExecuteList(Resource):

    @auth_required
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
            output = out + err
        else:
            output = 'Command contains invalid characters.'
            error = True
        return {'cmd': cmd, 'output': output, 'error': error}

api.add_resource(ExecuteList, '/execute')


class ArtifactsList(Resource):

    @auth_required
    def post(self):
        xml = request.data
        parser = etree.XMLParser(no_network=False)
        doc = etree.fromstring(str(xml), parser)
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
