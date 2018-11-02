from flask import Blueprint, Response, request, session, g, abort, jsonify
from sqlalchemy import desc
from pwnedhub import db
from pwnedhub.models import Mail, Message, Tool, User
from pwnedhub.decorators import login_required
from pwnedhub.utils import unfurl_url
from pwnedhub.validators import is_valid_command
from datetime import datetime
from lxml import etree
import os
import subprocess

api = Blueprint('api', __name__, url_prefix='/api')

# RESTful API controllers

# fetch user
@api.route('/users/me', methods=['GET'], endpoint='users-get')
@login_required
def users():
    return jsonify(**g.user.serialize())

# update note
@api.route('/notes', methods=['PUT'], endpoint='notes-put')
@login_required
def notes():
    if request.method == 'PUT':
        g.user.notes = request.json.get('notes')
        db.session.add(g.user)
        db.session.commit()
        return jsonify(notes=g.user.notes)

# create artifact
@api.route('/artifacts', methods=['POST'], endpoint='artifacts-post')
@login_required
def artifacts():
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

# fetch tool
@api.route('/tools/<string:tid>', methods=['GET'], endpoint='tools-get')
@login_required
def tools(tid):
    query = "SELECT * FROM tools WHERE id={}"
    try:
        tool = db.session.execute(query.format(tid)).first() or {}
    except:
        tool = {}
    return jsonify(**dict(tool))

# fetch mail
@api.route('/mail', methods=['GET'], endpoint='mail-get')
# fetch letter
@api.route('/mail/<string:mid>', methods=['GET'], endpoint='letter-get')
@login_required
def mail(mid=None):
    if mid and request.method == 'GET':
        letter = Mail.query.get(mid)
        if not letter:
            abort(404)
        # mark letter as read
        if letter.read == 0:
            letter.read = 1
            db.session.add(letter)
            db.session.commit()
        letter = letter.serialize()
        resp = jsonify(**letter)
        return resp
    # catch all and default response
    mail = [m.serialize() for m in g.user.received_mail.order_by(Mail.created.desc()).all()]
    resp = jsonify(mail=mail)
    return resp

# fetch messages
@api.route('/messages', methods=['GET'], endpoint='messages-get')
# create message
@api.route('/messages', methods=['POST'], endpoint='messages-post')
# delete message
@api.route('/messages/<string:mid>', methods=['DELETE'], endpoint='messages-delete')
@login_required
def messages(mid=None):
    if request.method == 'POST':
        jsonobj = request.get_json(force=True)
        message = jsonobj.get('message')
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
    if mid and request.method == 'DELETE':
        message = Message.query.get(mid)
        if message and (message.user == g.user or g.user.is_admin):
            db.session.delete(message)
            db.session.commit()
    # catch all and default response
    messages = [m.serialize() for m in Message.query.order_by(Message.created.desc()).all()]
    resp = jsonify(messages=messages)
    resp.mimetype = 'text/html'
    return resp

# RESTless API controllers

# execute tool
@api.route('/tools/<string:tid>/execute', methods=['POST'])
@login_required
def tools_execute(tid):
    tool = Tool.query.get(tid)
    path = tool.path
    args = request.json.get('args')
    cmd = '{} {}'.format(path, args)
    if is_valid_command(cmd):
        env = os.environ.copy()
        env['PATH'] = os.pathsep.join(('/usr/bin', env["PATH"]))
        p = subprocess.Popen([cmd, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
        out, err = p.communicate()
        output = out + err
    else:
        output = 'Command contains invalid characters.'
    return jsonify(cmd=cmd, output=output)

# fetch remote resource
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
