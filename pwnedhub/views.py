from flask import request, session, g, redirect, url_for, render_template, render_template_string, jsonify, flash, abort, send_file, __version__
from sqlalchemy import asc, desc, exc
from pwnedhub import app, db, spyne
from models import Mail, Message, Score, Tool, User
from constants import QUESTIONS, DEFAULT_NOTE
from decorators import login_required, roles_required
from utils import xor_encrypt, detect_user_agent, get_token
from validators import is_valid_quantity, is_valid_password, is_valid_file
from datetime import datetime
from hashlib import md5
from urllib import urlencode
import math
import os
import re
import subprocess
import traceback

# register new jinja global for the current date
# used in the layout to keep the current year
app.jinja_env.globals['date'] = datetime.now()

# monkey patch flask.render_template()
_render_template = render_template
def _my_render_template(*args, **kwargs):
    message = detect_user_agent(request.user_agent.string)
    if message:
        args = ('alternate.html',)
        kwargs = {'message': message}
    return _render_template(*args, **kwargs)
render_template = _my_render_template

@app.before_request
def load_user():
    g.user = None
    if session.get('user_id'):
        g.user = User.query.get(session.get('user_id'))

@app.after_request
def add_header(response):
    response.headers['X-Powered-By'] = 'Flask/{}'.format(__version__)
    # disable browser XSS protections
    response.headers['X-XSS-Protection'] = '0'
    return response

# general views

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return redirect(url_for('notes'))

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        g.user.notes = request.form['notes']
        db.session.add(g.user)
        db.session.commit()
        return jsonify(message='Notes saved.')
    notes = g.user.notes or DEFAULT_NOTE
    return render_template('notes.html', notes=notes)

@app.route('/admin')
@login_required
@roles_required('admin')
def admin():
    tools = Tool.query.order_by(Tool.name.asc()).all()
    users = User.query.filter(User.id != g.user.id).order_by(User.username.asc()).all()
    return render_template('admin.html', tools=tools, users=users)

@app.route('/admin/tools/add', methods=['POST'])
@login_required
@roles_required('admin')
def admin_tools_add():
    tool = Tool(
        name=request.form['name'],
        path=request.form['path'],
        description=request.form['description'],
    )
    db.session.add(tool)
    db.session.commit()
    flash('Tool added.')
    return redirect(url_for('admin'))

@app.route('/admin/tools/remove/<int:id>')
@login_required
@roles_required('admin')
def admin_tools_remove(id):
    tool = Tool.query.get(id)
    if tool:
        db.session.delete(tool)
        db.session.commit()
        flash('Tool removed.')
    else:
        flash('Invalid tool ID.')
    return redirect(url_for('admin'))

@app.route('/admin/users/<string:action>/<int:id>')
@login_required
def admin_users(action, id):
    user = User.query.get(id)
    if user:
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
    else:
        flash('Invalid user ID.')
    return redirect(url_for('admin'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=g.user, questions=QUESTIONS)

@app.route('/profile/change', methods=['GET', 'POST'])
@login_required
def profile_change():
    user = g.user
    if set(['password', 'question', 'answer']).issubset(request.values):
        password = request.values['password']
        if is_valid_password(password):
            name = request.values['name']
            question = request.values['question']
            answer = request.values['answer']
            user.name = name
            user.password = password
            user.question = question
            user.answer = answer
            db.session.add(user)
            db.session.commit()
            flash('Account information successfully changed.')
        else:
            flash('Password does not meet complexity requirements.')
    return redirect(url_for('profile'))

@app.route('/mail')
@login_required
def mail():
    mail = g.user.received_mail.order_by(Mail.created.desc()).all()
    return render_template('mail_inbox.html', mail=mail)

@app.route('/mail/compose', methods=['GET', 'POST'])
@app.route('/mail/compose/<int:id>')
@login_required
def mail_compose(id=0):
    if request.method == 'POST':
        content = request.form['content']
        if content:
            receiver = User.query.get(request.form['receiver'])
            subject = request.form['subject']
            mail = Mail(content=content, subject=subject, sender=g.user, receiver=receiver)
            db.session.add(mail)
            db.session.commit()
            flash('Mail sent.')
            return redirect(url_for('mail'))
    users = User.query.filter(User.id == id).all() or User.query.filter(User.id != g.user.id).order_by(User.username.asc()).all()
    return render_template('mail_compose.html', users=users)

@app.route('/mail/view/<int:id>')
@login_required
def mail_view(id):
    mail = Mail.query.get(id)
    if mail:
        if mail.read == 0:
            mail.read = 1
            db.session.add(mail)
            db.session.commit()
    else:
        flash('Invalid mail ID.')
        return redirect(url_for('mail'))
    return render_template('mail_view.html', mail=mail)

@app.route('/mail/delete/<int:id>')
@login_required
def mail_delete(id):
    mail = Mail.query.get(id)
    if mail:
        db.session.delete(mail)
        db.session.commit()
        flash('Mail deleted.')
    else:
        flash('Invalid mail ID.')
    return redirect(url_for('mail'))

@app.route('/messages.react')
@login_required
def messages_react():
    return render_template('messages.html', react=True)

@app.route('/api/messages', methods=['GET', 'POST'])
@app.route('/api/messages/<int:id>', methods=['DELETE'])
@login_required
def api_messages(id=None):
    if request.method == 'POST':
        message = request.json['message']
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
    if request.method == 'DELETE':
        message = Message.query.get(id)
        if message and message.user == g.user:
            db.session.delete(message)
            db.session.commit()
    messages = []
    # add is_owner field to each message
    for message in Message.query.order_by(Message.created.desc()).all():
        is_owner = False
        if message.user == g.user:
            is_owner = True
        message = message.serialize()
        message['is_owner'] = is_owner
        messages.append(message)
    return jsonify(messages=messages)

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    if request.method == 'POST':
        message = request.form['message']
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
    messages = Message.query.order_by(Message.created.desc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/messages/delete/<int:id>')
@login_required
def messages_delete(id):
    message = Message.query.get(id)
    if message and message.user == g.user:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted.')
    else:
        flash('Invalid message ID.')
    return redirect(url_for('messages'))

@app.route('/artifacts')
@login_required
def artifacts():
    for (dirpath, dirnames, filenames) in os.walk(session.get('upload_folder')):
        artifacts = [f for f in filenames if is_valid_file(f)]
        break
    return render_template('artifacts.html', artifacts=artifacts)

@app.route('/artifacts/save/<string:method>', methods=['POST'])
@login_required
def artifacts_save(method):
    if method == 'file':
        file = request.files['file']
        if file:
            if is_valid_file(file.filename):
                path = os.path.join(session.get('upload_folder'), file.filename)
                if not os.path.isfile(path):
                    try:
                        file.save(path)
                    except IOError:
                        flash('Unable to save the artifact.')
                else:
                    flash('An artifact with that name already exists.')
            else:
                flash('Invalid file type. Only {} filetypes allowed.'.format(', '.join(app.config['ALLOWED_EXTENSIONS'])))
    elif method == 'text':
        content = request.form['content']
        filename = request.form['filename']
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
            return jsonify(message=msg)
    return redirect(url_for('artifacts'))

@app.route('/artifacts/delete', methods=['POST'])
@login_required
def artifacts_delete():
    filename = request.form['filename']
    try:
        os.remove(os.path.join(session.get('upload_folder'), filename))
        flash('Artifact deleted.')
    except IOError:
        flash('Unable to remove the artifact.')
    return redirect(url_for('artifacts'))

@app.route('/artifacts/view', methods=['POST'])
@login_required
def artifacts_view():
    filename = request.form['filename']
    try:
        return send_file(os.path.join(session.get('upload_folder'), filename))
    except IOError:
        flash('Unable to load the artifact.')
    return redirect(url_for('artifacts'))

@app.route('/tools')
@login_required
def tools():
    tools = Tool.query.all()
    return render_template('tools.html', tools=tools)

@app.route('/tools/execute', methods=['POST'])
@login_required
def tools_execute():
    tool = Tool.query.get(request.form['tool'])
    path = tool.path
    args = request.form['args']
    cmd = '{} {}'.format(path, args)
    cmd = re.sub('[;&|]', '', cmd)
    p = subprocess.Popen([cmd, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    output = out + err
    return jsonify(cmd=cmd, output=output)

@app.route('/tools/info', methods=['POST'])
@login_required
def tools_info():
    query = "SELECT * FROM tools WHERE id='{}'"
    tid = request.form['tid']
    try:
        tools = db.session.execute(query.format(tid))
    except exc.OperationalError:
        tools = ()
    return jsonify(tools=[dict(t) for t in tools])

@app.route('/games/')
@login_required
def games():
    return render_template('games.html')

@app.route('/snake/<path:filename>')
@login_required
def snake_files(filename):
    rec_regex = r'rec(\d+)\.txt'
    if filename == 'highscores.txt':
        scores = Score.query.filter(Score.recid != None).order_by(Score.recid).all()
        scoreboard = []
        for i in range(0, len(scores)):
            scoreboard.append(('name'+str(i), scores[i].player))
            scoreboard.append(('score'+str(i), scores[i].score))
            scoreboard.append(('recFile'+str(i), scores[i].recid))
        return urlencode(scoreboard)
    elif re.search(rec_regex, filename):
        recid = re.search(rec_regex, filename).group(1)
        score = Score.query.filter_by(recid=recid).first()
        if not score:
            abort(404)
        return score.recording
    abort(404)

@app.route('/snake/enterHighscore.php', methods=['POST'])
@login_required
def snake_enter_score():
    status = 'no response'
    # make sure scorehash is correct for the given score
    score = int(request.form['score'])
    scorehash = int(request.form['scorehash'])
    if math.sqrt(scorehash - 1337) == score:
        if request.form['SNAKE_BLOCK'] == '1':
            # create recording string
            recTurn = request.form['recTurn']
            recFrame = request.form['recFrame']
            recFood = request.form['recFood']
            recData = urlencode({ 'recTurn':recTurn, 'recFrame':recFrame, 'recFood':recFood })
            # add the new score
            playerName = g.user.username#request.form['playerName']#re.sub('[&=#<>]', '', request.form['playerName'])
            score = Score(player=playerName, score=score, recording=recData)
            db.session.add(score)
            db.session.commit()
            # reset the high scores. the game requests rec#.txt files 0-9 by
            # default, so the recid field must be updated for the high scores
            # clear out current high scores
            for score in Score.query.all():
                score.recid = None
                db.session.add(score)
            db.session.commit()
            # update the recid field to set the new high scores
            scores = Score.query.order_by(Score.score.desc()).limit(10).all()
            for i in range(0, len(scores)):
                scores[i].recid = i
                db.session.add(scores[i])
            db.session.commit()
            status = 'ok'
        else:
            status = 'snake block not present'
    else:
        status = 'invalid scorehash'
    return urlencode({'status':status})

@app.route('/about')
def about():
    return render_template('about.html')

# authenticaton views

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if not User.query.filter_by(username=username).first():
            password = request.form['password']
            if password == request.form['confirm_password']:
                if is_valid_password(password):
                    user_dict = {}
                    for k in request.form:
                        if k not in ('confirm_password',):
                            user_dict[k] = request.form[k]
                    user = User(**user_dict)
                    db.session.add(user)
                    db.session.commit()
                    flash('Account created. Please log in.')
                    return redirect(url_for('login'))
                else:
                    flash('Password does not meet complexity requirements.')
            else:
                flash('Passwords do not match.')
        else:
            flash('Username already exists.')
    return render_template('register.html', questions=QUESTIONS)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # redirect to home if already logged in
    if session.get('user_id'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        token = request.form['token']
        if md5(session.get('seed')).hexdigest() == token:
            query = "SELECT * FROM users WHERE username='{}' AND password_hash='{}'"
            username = request.form['username']
            password_hash = xor_encrypt(request.form['password'], app.config['PW_ENC_KEY'])
            user = db.session.execute(query.format(username, password_hash)).first()
            if user and user['status'] == 1:
                session['user_id'] = user.id
                path = os.path.join(app.config['UPLOAD_FOLDER'], md5(str(user.id)).hexdigest())
                if not os.path.exists(path):
                    os.makedirs(path)
                session['upload_folder'] = path
                session.rotate()
                return redirect(request.args.get('next') or url_for('home'))
            return redirect(url_for('login', error='Invalid username or password.'))
        return redirect(url_for('login', error='Bot detected.'))
    session['seed'] = get_token(5)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.clear()
    return redirect(url_for('index'))

# password recovery flow views

@app.route('/reset', methods=['GET', 'POST'])
def reset_init():
    if request.method == 'POST':
        user = User.get_by_username(request.form['username'])
        if user:
            # add to session to begin the reset flow
            session['reset_id'] = user.id
            return redirect(url_for('reset_question'))
        else:
            flash('User not recognized.')
    return render_template('reset_init.html')

@app.route('/reset/question', methods=['GET', 'POST'])
def reset_question():
    # enforce flow control
    if not session.get('reset_id'):
        flash('Reset improperly initialized.')
        return redirect(url_for('reset_init'))
    user = User.query.get(session.get('reset_id'))
    if request.method == 'POST':
        answer = request.form['answer']
        if user.answer == answer:
            return redirect(url_for('reset_password'))
        else:
            flash('Incorrect answer.')
    return render_template('reset_question.html', question=user.question_as_string)

@app.route('/reset/password', methods=['GET', 'POST'])
def reset_password():
    # enforce flow control
    if not session.get('reset_id'):
        flash('Reset improperly initialized.')
        return redirect(url_for('reset_init'))
    if request.method == 'POST':
        password = request.form['password']
        if password == request.form['confirm_password']:
            if is_valid_password(password):
                user = User.query.get(session.pop('reset_id'))
                user.password = password
                db.session.add(user)
                db.session.commit()
                flash('Password reset. Please log in.')
                return redirect(url_for('login'))
            else:
                flash('Invalid password.')
        else:
            flash('Passwords do not match.')
    return render_template('reset_password.html')

@app.errorhandler(404)
def page_not_found(e):
    template = '''{%% extends "layout.html" %%}
{%% block body %%}
    <div class="center-content error">
        <h1>Oops! That page doesn't exist.</h1>
        <h3>%s</h3>
    </div>
{%% endblock %%}
''' % (request.url)
    return render_template_string(template), 404

@app.errorhandler(500)
def internal_error(e):
    message = traceback.format_exc()
    return render_template('500.html', message=message), 500

# SOAP web service view

from spyne.protocol.soap import Soap11
from spyne.model.primitive import AnyDict, Unicode, Integer
from spyne.model.complex import Iterable

class Tools(spyne.Service):
    __service_url_path__ = '/service'
    __in_protocol__ = Soap11(validator='lxml')
    __out_protocol__ = Soap11()

    @spyne.srpc(Unicode, _returns=Iterable(AnyDict))
    def info(tid):
        query = "SELECT * FROM tools WHERE id='{}'"
        try:
            tools = db.session.execute(query.format(tid))
        except Exception as e:
            tools = [dict(error=e.__str__())]
        for tool in tools:
            yield dict(tool)
