from flask import Blueprint, Response, request, session, g, abort, jsonify
from sqlalchemy import desc
from pwnedhub import db
from pwnedhub.models import Mail, Message, Tool, User
from pwnedhub.constants import ADMIN_RESPONSE
from pwnedhub.decorators import login_required
from pwnedhub.utils import unfurl_url
from pwnedhub.validators import is_valid_command
from datetime import datetime
from lxml import etree
import os
import subprocess

api = Blueprint('api', __name__, url_prefix='/api')

# RESTful API controllers

# get the current user
@api.route('/users/<string:uid>', methods=['GET'])
@login_required
def user_read(uid):
    if uid == 'me':
        return jsonify(**g.user.serialize())
    user = User.query.get(uid)
    if not user:
        abort(404)
    return jsonify(**user.serialize(public=True))

# get all users
@api.route('/users', methods=['GET'])
@login_required
def users_read():
    users = [u.serialize(public=True) for u in User.query.all()]
    return jsonify(users=users)

# create an artifact
@api.route('/artifacts', methods=['POST'])
@login_required
def artifact_create():
    xml = request.data
    parser = etree.XMLParser()
    doc = etree.fromstring(str(xml), parser)
    content = doc.find('content').text
    filename = doc.find('filename').text
    if all((content, filename)):
        filename += '-{}.txt'.format(datetime.now().strftime('%s'))
        msg = 'Artifact created \'{}\'.'.format(filename)
        path = os.path.join(session.get('upload_folder'), filename)
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

# get a tool
@api.route('/tools/<string:tid>', methods=['GET'])
@login_required
def tool_read(tid):
    query = "SELECT * FROM tools WHERE id={}"
    try:
        tool = db.session.execute(query.format(tid)).first() or {}
    except:
        tool = {}
    return jsonify(**dict(tool))

# get all mail
@api.route('/mail', methods=['GET'])
@login_required
def mailbox_read():
    mail = [m.serialize() for m in g.user.received_mail.order_by(Mail.created.desc()).all()]
    return jsonify(mail=mail)

# create a piece of mail
@api.route('/mail', methods=['POST'])
@login_required
def mail_create():
    content = request.json.get('content')
    receiver = User.query.get(request.json.get('receiver'))
    subject = request.json.get('subject')
    letter = Mail(content=content, subject=subject, sender=g.user, receiver=receiver)
    db.session.add(letter)
    db.session.commit()
    # generate automated Administrator response
    if receiver.role == 0:
        content = ADMIN_RESPONSE
        auto_letter = Mail(content=content, subject='RE:'+subject, sender=receiver, receiver=g.user)
        db.session.add(auto_letter)
        db.session.commit()
    return jsonify(**letter.serialize())

# get a piece of mail
@api.route('/mail/<string:mid>', methods=['GET'])
@login_required
def mail_read(mid):
    mail = Mail.query.get(mid)
    if mail:
        # mark mail as read
        if mail.read == 0:
            mail.read = 1
            db.session.add(mail)
            db.session.commit()
        # [vuln] no authz check
        mail = mail.serialize()
        resp = jsonify(**mail)
    else:
        abort(404)
    return resp

# delete a piece of mail
@api.route('/mail/<string:mid>', methods=['DELETE'])
@login_required
def mail_delete(mid):
    mail = Mail.query.get(mid)
    if mail:
        if mail.receiver == g.user:
            db.session.delete(mail)
            db.session.commit()
            mail = [m.serialize() for m in g.user.received_mail.order_by(Mail.created.desc()).all()]
            resp = jsonify(mail=mail)
        else:
            abort(403)
    else:
        abort(404)
    return resp

# get all messages
@api.route('/messages', methods=['GET'])
@login_required
def messages_read():
    messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
    resp = jsonify(messages=messages)
    # [vuln] responds with mismatched content type
    resp.mimetype = 'text/html'
    return resp

# create a message
@api.route('/messages', methods=['POST'])
@login_required
def message_create():
    # [vuln] accepts mismatched content type
    jsonobj = request.get_json(force=True)
    message = jsonobj.get('message')
    if message:
        msg = Message(comment=message, user=g.user)
        db.session.add(msg)
        db.session.commit()
    messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
    return jsonify(messages=messages)

# delete a message
@api.route('/messages/<string:mid>', methods=['DELETE'])
@login_required
def message_delete(mid):
    message = Message.query.get(mid)
    if message:
        if message.user == g.user or g.user.is_admin:
            db.session.delete(message)
            db.session.commit()
            messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
            resp = jsonify(messages=messages)
        else:
            abort(403)
    else:
        abort(404)
    return resp

# RESTless API controllers

# update the current user's notes
@api.route('/notes', methods=['PUT'])
@login_required
def note_update():
    g.user.notes = request.json.get('notes')
    db.session.add(g.user)
    db.session.commit()
    return jsonify(notes=g.user.notes)

# execute a tool
@api.route('/tools/<string:tid>/execute', methods=['POST'])
@login_required
def tool_execute(tid):
    tool = Tool.query.get(tid)
    path = tool.path
    args = request.json.get('args')
    cmd = '{} {}'.format(path, args)
    error = False
    if is_valid_command(cmd):
        env = os.environ.copy()
        env['PATH'] = os.pathsep.join(('/usr/bin', env["PATH"]))
        p = subprocess.Popen([cmd, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
        out, err = p.communicate()
        output = out + err
    else:
        output = 'Command contains invalid characters.'
        error = True
    return jsonify(cmd=cmd, output=output, error=error)

# get a remote resource
@api.route('/unfurl', methods=['POST'])
def unfurl():
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
    return jsonify(**data), status
