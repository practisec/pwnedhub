from flask import Blueprint, current_app, request, session, g, redirect, url_for, render_template, flash, jsonify, Response, send_file, abort, __version__
from pwnedhub import db
from pwnedhub.decorators import login_required, roles_required, validate, csrf_protect
from common.models import Note, Mail, Message, Tool, User, Room
from common.constants import ROLES, QUESTIONS, DEFAULT_NOTE, ADMIN_RESPONSE
from common.utils.unfurl import unfurl_url
from common.validators import is_valid_password, is_valid_command, is_valid_filename, is_valid_mimetype
from datetime import datetime
from lxml import etree
import os
import platform
import subprocess

core = Blueprint('core', __name__)

@core.before_app_request
def render_mobile():
    if any(x in request.user_agent.string.lower() for x in ['android', 'iphone', 'ipad']):
        if not request.endpoint.startswith('static'):
            return render_template('mobile.html')

@core.before_app_request
def load_user():
    g.user = None
    if session.get('user_id'):
        g.user = User.query.get(session.get('user_id'))

@core.after_app_request
def add_header(response):
    response.headers['X-Powered-By'] = 'Flask/{}'.format(__version__)
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@core.after_app_request
def restrict_flashes(response):
    flashes = session.get('_flashes')
    if flashes and len(flashes) > 5:
        del session['_flashes'][0]
    return response

# general controllers

@core.route('/')
def index():
    return render_template('index.html')

@core.route('/home')
def home():
    if g.user:
        if g.user.is_admin:
            return redirect(url_for('core.admin_users'))
        return redirect(url_for('core.notes'))
    return redirect(url_for('core.index'))

@core.route('/about')
def about():
    return render_template('about.html')

# admin controllers

@core.route('/admin/tools')
@login_required
@roles_required('admin')
def admin_tools():
    tools = Tool.query.order_by(Tool.name.asc()).all()
    return render_template('admin_tools.html', tools=tools)

@core.route('/admin/tools/add', methods=['POST'])
@login_required
@roles_required('admin')
@validate(['name', 'path', 'description'])
def admin_tools_add():
    tool = Tool(
        name=request.form['name'],
        path=request.form['path'],
        description=request.form['description'],
    )
    db.session.add(tool)
    db.session.commit()
    flash('Tool added.')
    return redirect(url_for('core.admin_tools'))

@core.route('/admin/tools/remove/<int:tid>')
@login_required
@roles_required('admin')
def admin_tools_remove(tid):
    tool = Tool.query.get_or_404(tid)
    db.session.delete(tool)
    db.session.commit()
    flash('Tool removed.')
    return redirect(url_for('core.admin_tools'))

@core.route('/admin/users')
@login_required
@roles_required('admin')
def admin_users():
    users = User.query.filter(User.id != g.user.id).order_by(User.username.asc()).all()
    return render_template('admin_users.html', users=users)

@core.route('/admin/users/<string:action>/<int:uid>')
@login_required
def admin_users_modify(action, uid):
    user = User.query.get_or_404(uid)
    if user != g.user:
        if action == 'promote':
            user.role = 0
            db.session.add(user)
            db.session.commit()
            flash('User promoted.')
        elif action == 'demote':
            user.role = 1
            db.session.add(user)
            db.session.commit()
            flash('User demoted.')
        elif action == 'enable':
            user.status = 1
            db.session.add(user)
            db.session.commit()
            flash('User enabled.')
        elif action == 'disable':
            user.status = 0
            db.session.add(user)
            db.session.commit()
            flash('User disabled.')
        else:
            flash('Invalid user action.')
    else:
        flash('Self-modification denied.')
    return redirect(url_for('core.admin_users'))

# user controllers

@core.route('/profile', methods=['GET', 'POST'])
@login_required
@validate(['name', 'question', 'answer'])
@csrf_protect
def profile():
    user = g.user
    if request.values:
        password = request.values['password']
        if password:
            if is_valid_password(password):
                user.password = password
            else:
                flash('Password does not meet complexity requirements.')
        user.avatar = request.values['avatar']
        user.signature = request.values['signature']
        user.name = request.values['name']
        user.question = request.values['question']
        user.answer = request.values['answer']
        db.session.add(user)
        db.session.commit()
        flash('Account information changed.')
    return render_template('profile.html', user=user, questions=QUESTIONS)

@core.route('/profile/view/<int:uid>')
@login_required
def profile_view(uid):
    user = User.query.get_or_404(uid)
    return render_template('profile_view.html', user=user)

@core.route('/mail')
@login_required
def mail():
    mail = g.user.received_mail.order_by(Mail.created.desc()).all()
    return render_template('mail_inbox.html', mail=mail)

@core.route('/mail/compose', methods=['GET', 'POST'])
@login_required
@validate(['receiver', 'subject', 'content'])
def mail_compose():
    if request.method == 'POST':
        receiver = User.query.get(request.form['receiver'])
        if not receiver:
            abort(400, 'Invalid receiver.')
        content = request.form['content']
        subject = request.form['subject']
        letter = Mail(content=content, subject=subject, sender=g.user, receiver=receiver)
        db.session.add(letter)
        db.session.commit()
        # generate automated Administrator response
        if receiver.role == 0:
            content = ADMIN_RESPONSE
            letter = Mail(content=content, subject='RE: '+subject, sender=receiver, receiver=g.user)
            db.session.add(letter)
            db.session.commit()
        flash('Mail sent.')
        return redirect(url_for('core.mail'))
    users = User.query.filter(User.id != g.user.id).order_by(User.username.asc()).all()
    return render_template('mail_compose.html', users=users)

@core.route('/mail/reply/<int:mid>')
@login_required
def mail_reply(mid=0):
    letter = Mail.query.get_or_404(mid)
    return render_template('mail_reply.html', letter=letter)

@core.route('/mail/view/<int:mid>')
@login_required
def mail_view(mid):
    letter = Mail.query.get_or_404(mid)
    if letter.read == 0:
        letter.read = 1
        db.session.add(letter)
        db.session.commit()
    return render_template('mail_view.html', letter=letter)

@core.route('/mail/delete/<int:mid>')
@login_required
def mail_delete(mid):
    letter = Mail.query.get_or_404(mid)
    db.session.delete(letter)
    db.session.commit()
    flash('Mail deleted.')
    return redirect(url_for('core.mail'))

@core.route('/messages')
@core.route('/messages/page/<int:page>')
@login_required
def messages(page=1):
    messages = Room.query.first().messages.order_by(Message.created.desc()).paginate(page=page, per_page=5)
    return render_template('messages.html', messages=messages)

@core.route('/messages/create', methods=['POST'])
@login_required
@validate(['message'])
def messages_create():
    message = request.form['message']
    msg = Message(comment=message, author=g.user, room=Room.query.first())
    db.session.add(msg)
    db.session.commit()
    return redirect(url_for('core.messages'))

@core.route('/messages/delete/<int:mid>')
@login_required
def messages_delete(mid):
    message = Room.query.first().messages.filter_by(id=mid).first()
    if not message:
        abort(404)
    if message.author == g.user or g.user.is_admin:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted.')
    else:
        abort(403)
    return redirect(url_for('core.messages'))

@core.route('/messages/unfurl', methods=['POST'])
def unfurl():
    url = request.json.get('url')
    headers = {}
    data = {'error': 'RequestError', 'message': 'Invalid request.'}
    status = 400
    if url:
        try:
            data = unfurl_url(url, headers)
            status = 200
        except Exception as e:
            data = {'error': 'UnfurlError', 'message': str(e)}
            status = 500
    return jsonify(**data), status

@core.route('/notes')
@login_required
@roles_required('user')
def notes():
    note = g.user.notes.first()
    notes = note.content if note else DEFAULT_NOTE
    return render_template('notes.html', notes=notes)

@core.route('/notes', methods=['PUT'])
@login_required
@roles_required('user')
def notes_update():
    notes = g.user.notes.first()
    if not notes:
        notes = Note(name='Notes', owner=g.user)
    notes.content = request.json.get('notes')
    db.session.add(notes)
    db.session.commit()
    return jsonify(notes=notes.content)

@core.route('/artifacts')
@login_required
@roles_required('user')
def artifacts():
    artifacts = []
    for (dirpath, dirnames, filenames) in os.walk(session.get('upload_folder')):
        valid_filenames = [f for f in filenames if is_valid_filename(f)]
        for filename in valid_filenames:
            modified_ts = os.path.getmtime(os.path.join(dirpath, filename))
            modified = datetime.fromtimestamp(modified_ts).strftime('%Y-%m-%d %H:%M:%S')
            artifacts.append({'filename': filename, 'modified': modified})
        break
    return render_template('artifacts.html', artifacts=artifacts)

@core.route('/artifacts/save', methods=['POST'])
@login_required
@roles_required('user')
@validate(['file'])
def artifacts_save():
    file = request.files['file']
    if is_valid_filename(file.filename):
        if is_valid_mimetype(file.mimetype):
            path = os.path.join(session.get('upload_folder'), file.filename)
            if not os.path.isfile(path):
                try:
                    file.save(path)
                except IOError:
                    flash('Unable to save the artifact.')
            else:
                flash('An artifact with that name already exists.')
        else:
            flash('Invalid file type. Only {} types allowed.'.format(', '.join(current_app.config['ALLOWED_MIMETYPES'])))
    else:
        flash('Invalid file extension. Only {} extensions allowed.'.format(', '.join(current_app.config['ALLOWED_EXTENSIONS'])))
    return redirect(url_for('core.artifacts'))

@core.route('/artifacts/create', methods=['POST'])
@login_required
@roles_required('user')
def artifacts_create():
    xml = request.data
    parser = etree.XMLParser(no_network=False)
    doc = etree.fromstring(xml, parser)
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

@core.route('/artifacts/delete', methods=['POST'])
@login_required
@roles_required('user')
@validate(['filename'])
def artifacts_delete():
    filename = request.form['filename']
    try:
        os.remove(os.path.join(session.get('upload_folder'), filename))
        flash('Artifact deleted.')
    except IOError:
        flash('Unable to remove the artifact.')
    return redirect(url_for('core.artifacts'))

@core.route('/artifacts/view', methods=['POST'])
@login_required
@roles_required('user')
@validate(['filename'])
def artifacts_view():
    filename = request.form['filename']
    try:
        return send_file(os.path.join(session.get('upload_folder'), filename))
    except IOError:
        flash('Unable to load the artifact.')
    return redirect(url_for('core.artifacts'))

@core.route('/tools')
@login_required
@roles_required('user')
def tools():
    tools = Tool.query.all()
    return render_template('tools.html', tools=tools)

@core.route('/tools/info/<string:tid>', methods=['GET'])
@login_required
@roles_required('user')
def tools_info(tid):
    query = 'SELECT * FROM tools WHERE id='+tid
    try:
        tool = db.session.execute(query).first() or {}
    except:
        tool = {}
    return jsonify(**dict(tool))

@core.route('/tools/execute/<string:tid>', methods=['POST'])
@login_required
@roles_required('user')
def tools_execute(tid):
    tool = Tool.query.get_or_404(tid)
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
    return jsonify(cmd=cmd, output=output, error=error)

@core.route('/status')
def server_status():
    # borrowed from https://github.com/balarsen/FlaskStatus
    platform_stats = {
        'architecture': platform.architecture(),
        'machine': platform.machine(),
        'node': platform.node(),
        'platform': platform.platform(),
        'processor': platform.processor(),
        'python_branch': platform.python_branch(),
        'python_build': platform.python_build(),
        'python_compiler': platform.python_compiler(),
        'python_implementation': platform.python_implementation(),
        'python_revision': platform.python_revision(),
        'python_version': platform.python_version(),
        'python_version_tuple': platform.python_version_tuple(),
        'release': platform.release(),
        'system': platform.system(),
        'uname': platform.uname(),
        'version': platform.version(),
        'java_ver': platform.java_ver(),
        'win32_ver': platform.win32_ver(),
        'mac_ver': platform.mac_ver(),
        'libc_ver': platform.libc_ver(),
        'load_average': os.getloadavg()
    }
    log_stats = []
    log_files = [
        '/tmp/gunicorn-pwnedapi.log',
        '/tmp/gunicorn-pwnedconfig.log',
        '/tmp/gunicorn-pwnedhub.log',
        '/tmp/gunicorn-pwnedspa.log',
        '/tmp/gunicorn-pwnedgraph.log',
        '/var/log/nginx/access.log',
    ]
    for log_file in log_files:
        if os.path.exists(log_file):
            data = {
                'name': log_file,
                'size': os.path.getsize(log_file),
                'mtime': os.path.getmtime(log_file),
                'ctime': os.path.getctime(log_file),
                'tail': []
            }
            with open(log_file) as fp:
                data['tail'] = ''.join(fp.readlines()[-20:])
            log_stats.append(data)

    return render_template('status.html', platform_stats=platform_stats, log_stats=log_stats)
