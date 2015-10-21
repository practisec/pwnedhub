from flask import request, session, g, redirect, url_for, render_template, jsonify, flash, abort, send_file
from sqlalchemy import asc, desc
from pwnedhub import app, db
from models import User, Message, Score
from constants import QUESTIONS, TOOLS, DEFAULT_NOTE
from decorators import login_required, roles_required
from utils import xor_encrypt
from validators import is_valid_quantity, is_valid_password, is_valid_file
from urllib import urlencode
import math
import os
import re
import subprocess

@app.before_request
def load_user():
    g.user = None
    if session.get('user_id'):
        g.user = User.query.get(session["user_id"])

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
    notes = g.user.notes or DEFAULT_NOTE
    return render_template('notes.html', notes=notes)

'''
@app.route('/admin')
@login_required
@roles_required('admin')
def admin():
    vouchers = Voucher.query.order_by(Voucher.created.desc())
    users = User.query.order_by(User.username.asc())
    return render_template('admin.html', vouchers=vouchers, users=users)
'''

# ;;no re-authentication for state changing operations
# ;;passwords stored in a plain or reversable form
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        password = request.form['password']
        if is_valid_password(password):
            question = request.form['question']
            answer = request.form['answer']
            g.user.password = password
            g.user.question = question
            g.user.answer = answer
            db.session.add(g.user)
            db.session.commit()
            flash('Account information successfully changed.')
        else:
            flash('Password does not meet complexity requirements.')
    return render_template('profile.html', questions=QUESTIONS)

# ;;stored XSS
@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    if request.method == 'POST':
        message = request.form['message']
        if message:
            msg = Message(comment=message, user=g.user)
            db.session.add(msg)
            db.session.commit()
    messages = Message.query.order_by(Message.created.desc())
    return render_template('messages.html', messages=messages)

# ;;insecure direct object reference
@app.route('/messages/delete/<int:id>')
@login_required
def messages_delete(id):
    message = Message.query.get(id)
    if message:
        db.session.delete(message)
        db.session.commit()
        flash('Message deleted.')
    else:
        flash('Invalid message ID.')
    return redirect(url_for('messages'))

@app.route('/artifacts', methods=['GET', 'POST'])
@login_required
def artifacts():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            if is_valid_file(file.filename):
                path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                if not os.path.isfile(path):
                    try:
                        file.save(path)
                    except IOError:
                        flash('Unable to save the artifact.')
                else:
                    flash('An artifact with that name already exists.')
            else:
                flash('Invalid file type. Only {} filetypes allowed.'.format(', '.join(app.config['ALLOWED_EXTENSIONS'])))
    for (dirpath, dirnames, filenames) in os.walk(app.config['UPLOAD_FOLDER']):
        artifacts = [f for f in filenames if is_valid_file(f)]
        break
    return render_template('artifacts.html', artifacts=artifacts)

# ;;path traversal
@app.route('/artifacts/delete/<path:filename>')
@login_required
def artifacts_delete(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Artifact deleted.')
    except IOError:
        flash('Unable to remove the artifact.')
    return redirect(url_for('artifacts'))

# ;;path traversal
@app.route('/artifacts/view/<path:filename>')
@login_required
def artifacts_view(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except IOError:
        flash('Unable to load the artifact.')
    return redirect(url_for('artifacts'))

@app.route('/tools')
@login_required
def tools():
    return render_template('tools.html', tools=TOOLS)

# ;;OSCI using command substitution
@app.route('/tools/execute', methods=['POST'])
@login_required
def tools_execute():
    tool = TOOLS[int(request.form['tool'])][1]
    args = request.form['args']
    cmd = '{} {}'.format(tool, args)
    # filter out MOST characters that lead to OSCI
    cmd = re.sub('[;&|]', '', cmd)
    p = subprocess.Popen([cmd, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    output = out + err
    return jsonify(cmd=cmd, output=output)

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
            playerName = request.form['playerName']#re.sub('[&=#<>]', '', request.form['playerName'])
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

# authenticaton views

# ;;user enumeration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if not User.query.filter_by(username=username).first():
            password = request.form['password']
            if password == request.form['confirm_password']:
                if is_valid_password(password):
                    # ;;mass assignment
                    user_dict = {}
                    for k in request.form:
                        if k not in ('confirm_password',):
                            user_dict[k] = request.form[k]
                    print user_dict
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

# ;; SQLi for auth bypass
@app.route('/login', methods=['GET', 'POST'])
def login():
    # redirect to home if already logged in
    if session.get('user_id'):
        return redirect(url_for('home'))
    username = ''
    if request.method == 'POST':
        #user = User.get_by_username(request.form['username'])
        query = "SELECT * FROM users WHERE username='{}' AND password_hash='{}'"
        username = request.form['username']
        password_hash = xor_encrypt(request.form['password'], app.config['PW_ENC_KEY'])
        user = db.session.execute(query.format(username, password_hash)).first()
        if user:
            #if user.check_password(request.form['password']):
            session['user_id'] = user.id
            #flash('You have successfully logged in.')
            #if user.is_admin():
            #    return redirect(url_for('admin'))
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html', username=username)

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    #flash('You have been logged out')
    return redirect(url_for('index'))

# password recovery flow views

# ;;logic flaw
# once an attacker submits a valid username, they can directly request
# the reset password endpoint to bypass the security questions
# ;;user enumeration
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
