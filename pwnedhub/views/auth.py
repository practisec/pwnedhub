from flask import Blueprint, current_app, request, session, redirect, url_for, render_template, flash
from pwnedhub import db
from pwnedhub.models import Mail, User
from pwnedhub.constants import QUESTIONS
from pwnedhub.decorators import login_required, validate
from pwnedhub.utils import xor_encrypt
from pwnedhub.validators import is_valid_password
from hashlib import md5
import os

auth = Blueprint('auth', __name__)

# authenticaton controllers

@auth.route('/register', methods=['GET', 'POST'])
@validate(['username', 'name', 'password', 'confirm_password', 'question', 'answer'])
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
                    # create default welcome message
                    sender = User.query.get(1)
                    receiver = user
                    subject = 'Welcome to PwnedHub!'
                    content = "We're glad you've chosen PwnedHub to help you take your next step in becoming a more efficient security consultant. We're here to help. If you have any questions or concerns, please don't hesitate to reach out to this account for assistance. Together, we can make security testing great again!"
                    mail = Mail(content=content, subject=subject, sender=sender, receiver=receiver)
                    db.session.add(mail)
                    db.session.commit()
                    flash('Account created. Please log in.')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Password does not meet complexity requirements.')
            else:
                flash('Passwords do not match.')
        else:
            flash('Username already exists.')
    return render_template('register.html', questions=QUESTIONS)

@auth.route('/login', methods=['GET', 'POST'])
@validate(['username', 'password'])
def login():
    # redirect to home if already logged in
    if session.get('user_id'):
        return redirect(url_for('core.home'))
    if request.method == 'POST':
        username = request.form['username']
        password_hash = xor_encrypt(request.form['password'], current_app.config['PW_ENC_KEY'])
        query = "SELECT * FROM users WHERE username='"+username+"' AND password_hash='"+password_hash+"'"
        user = db.session.execute(query).first()
        if user and user['status'] == 1:
            session['user_id'] = user.id
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], md5(str(user.id)).hexdigest())
            if not os.path.exists(path):
                os.makedirs(path)
            session['upload_folder'] = path
            session.rotate()
            return redirect(request.args.get('next') or url_for('core.home'))
        return redirect(url_for('auth.login', error='Invalid username or password.'))
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.clear()
    return redirect(url_for('core.index'))

# password recovery flow controllers

@auth.route('/reset', methods=['GET', 'POST'])
@validate(['username'])
def reset_init():
    if request.method == 'POST':
        query = "SELECT * FROM users WHERE username='{}'"
        username = request.form['username']
        try:
            user = db.session.execute(query.format(username)).first()
        except:
            user = None
        if user:
            # add to session to begin the reset flow
            session['reset_id'] = user.id
            return redirect(url_for('auth.reset_question'))
        else:
            flash('User not recognized.')
    return render_template('reset_init.html')

@auth.route('/reset/question', methods=['GET', 'POST'])
@validate(['answer'])
def reset_question():
    # enforce flow control
    if not session.get('reset_id'):
        flash('Reset improperly initialized.')
        return redirect(url_for('auth.reset_init'))
    user = User.query.get(session.get('reset_id'))
    if request.method == 'POST':
        answer = request.form['answer']
        if user.answer == answer:
            return redirect(url_for('auth.reset_password'))
        else:
            flash('Incorrect answer.')
    return render_template('reset_question.html', question=user.question_as_string)

@auth.route('/reset/password', methods=['GET', 'POST'])
@validate(['password', 'confirm_password'])
def reset_password():
    # enforce flow control
    if not session.get('reset_id'):
        flash('Reset improperly initialized.')
        return redirect(url_for('auth.reset_init'))
    if request.method == 'POST':
        password = request.form['password']
        if password == request.form['confirm_password']:
            if is_valid_password(password):
                user = User.query.get(session.pop('reset_id'))
                user.password = password
                db.session.add(user)
                db.session.commit()
                flash('Password reset. Please log in.')
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid password.')
        else:
            flash('Passwords do not match.')
    return render_template('reset_password.html')
