from flask import Blueprint, Response, request, session, g, jsonify
from sqlalchemy import desc
from pwnedhub import db
from pwnedhub.models import Message, Tool
from pwnedhub.decorators import login_required
from pwnedhub.utils import unfurl_uri
from pwnedhub.validators import is_valid_command
from datetime import datetime
from lxml import etree
import os
import subprocess

api = Blueprint('api', __name__, url_prefix='/api')

# create artifact
@api.route('/artifacts', methods=['POST'])
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
@api.route('/tools/<string:tid>')
@login_required
def tools(tid):
    query = "SELECT * FROM tools WHERE id={}"
    try:
        tool = db.session.execute(query.format(tid)).first() or {}
    except:
        tool = {}
    return jsonify(**dict(tool))

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

# fetch messages
@api.route('/messages', methods=['GET', 'POST'])
# create or delete message
@api.route('/messages/<int:mid>', methods=['DELETE'])
@login_required
def messages(mid=None):
    if request.method == 'POST':
        jsonobj = request.get_json(force=True)
        message = jsonobj.get('message')
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
    if request.method == 'DELETE':
        message = Message.query.get(mid)
        if message and (message.user == g.user or g.user.is_admin):
            db.session.delete(message)
            db.session.commit()
    messages = []
    # add is_owner field to each message
    for message in Message.query.order_by(Message.created.desc()).all():
        can_delete = False
        if message.user == g.user or g.user.is_admin:
            can_delete = True
        message = message.serialize()
        message['is_owner'] = can_delete
        messages.append(message)
    resp = jsonify(messages=messages)
    resp.mimetype = 'text/html'
    return resp

# fetch and parse remote resource
@api.route('/unfurl', methods=['POST'])
def unfurl():
    uri = request.json.get('uri')
    headers = {'User-Agent': request.headers.get('User-Agent')}
    if uri:
        try:
            data = unfurl_uri(uri, headers)
            status = 200
        except Exception as e:
            data = {'error': 'UnfurlError', 'message': str(e)}
            status = 500
    else:
        data = {'error': 'RequestError', 'message': 'Invalid request.'}
        status = 400
    return jsonify(unfurl=data), status
