from flask import Blueprint, current_app, request, g, session, redirect, url_for, render_template, flash, abort
from pwnedhub import db
from pwnedhub.constants import QUESTIONS
from pwnedhub.decorators import validate
from pwnedhub.models import Config, Email, Mail, User, Token
from pwnedhub.oauth import OAuthSignIn, OAuthCallbackError
from pwnedhub.utils import xor_encrypt, generate_timestamp_token
from pwnedhub.validators import is_valid_password
from hashlib import md5
from secrets import token_urlsafe
from sqlalchemy import select, text
import jwt
import os

blp = Blueprint('auth', __name__)

@blp.before_app_request
def load_user():
    g.user = None
    if session.get('user_id'):
        g.user = User.query.get(session.get('user_id'))

def create_welcome_message(user):
    sender = User.query.get(1)
    receiver = user
    subject = 'Welcome to PwnedHub!'
    content = "We're glad you've chosen PwnedHub to help you take your next step in becoming a more efficient security consultant. We're here to help. If you have any questions or concerns, please don't hesitate to reach out to this account for assistance. Together, we can make security testing great again!"
    mail = Mail(content=content, subject=subject, sender=sender, receiver=receiver)
    db.session.add(mail)
    db.session.commit()

def init_session(user_id):
    session['user_id'] = user_id
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], md5(str(user_id).encode()).hexdigest())
    if not os.path.exists(path):
        os.makedirs(path)
    session['upload_folder'] = path
    current_app.session_interface.regenerate(session)

# authenticaton controllers

@blp.route('/register', methods=['GET', 'POST'])
@validate(['username', 'email', 'name', 'password', 'question', 'answer'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if not User.get_by_username(username):
            email = request.form['email']
            if not User.get_by_email(email):
                password = request.form['password']
                if is_valid_password(password):
                    user = User(**request.form.to_dict())
                    db.session.add(user)
                    db.session.commit()
                    create_welcome_message(user)
                    flash('Account created. Please log in.')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Password does not meet complexity requirements.')
            else:
                flash('Email already exists.')
        else:
            flash('Username already exists.')
    return render_template('register.html', questions=QUESTIONS)

@blp.route('/login', methods=['GET', 'POST'])
@validate(['username', 'password'])
def login():
    # redirect to home if already logged in
    if session.get('user_id'):
        return redirect(url_for('core.home'))
    if request.method == 'POST':
        username = request.form['username']
        # introduce an artificial delay to simulate multiple database queries if the username is valid
        if User.get_by_username(username):
            import time
            time.sleep(0.1)
        if Config.get_value('SQLI_PROTECT'):
            user = User.get_by_username(username)
            if user and not user.check_password(request.form['password']):
                user = None
        else:
            password_hash = xor_encrypt(request.form['password'], current_app.config['SECRET_KEY'])
            query = select(User).where(text("username='{}' AND password_hash='{}'".format(username, password_hash)))
            user = db.session.execute(query).scalars().first()
        if user and user.is_enabled:
            init_session(user.id)
            return redirect(request.args.get('next') or url_for('core.home'))
        return redirect(url_for('auth.login', error='Invalid username or password.', next=request.args.get('next')))
    return render_template('login.html', next=request.args.get('next'))

@blp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.clear()
    return redirect(url_for('core.index'))

@blp.route('/sso/login')
def sso_login():
    id_token = request.args.get('id_token')
    if not id_token:
        return redirect(url_for('auth.login', error='Missing ID token.', next=request.args.get('next')))
    try:
        payload = jwt.decode(id_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        return redirect(url_for('auth.login', error='Invalid ID token.', next=request.args.get('next')))
    user = User.get_by_username(payload.get('sub'))
    if user and user.is_enabled:
        init_session(user.id)
        return redirect(request.args.get('next') or url_for('core.home'))
    return redirect(url_for('auth.login', error='Invalid username or password.', next=request.args.get('next')))

@blp.route('/oauth/login/<string:provider>')
def oauth_login(provider):
    # redirect to home if logged in
    if session.get('user_id'):
        return redirect(url_for('core.home'))
    # validate the provider
    if provider not in current_app.config['OAUTH_PROVIDERS']:
        return redirect(url_for('auth.login'))
    # build an authorization url
    oauth = OAuthSignIn(provider)
    if not oauth.doc:
        return redirect(url_for('auth.login', error='OpenID Connect provider unreachable.'))
    url = oauth.authorize()
    return redirect(url)

@blp.route('/oauth/callback/<string:provider>')
def oauth_callback(provider):
    # validate the provider
    if provider not in current_app.config['OAUTH_PROVIDERS']:
        return redirect(url_for('auth.login'))
    oauth = OAuthSignIn(provider)
    try:
        resp = oauth.callback(request)
    except OAuthCallbackError as e:
        flash(e.__str__(), category='error')
    else:
        # process user information
        email = resp['email']
        user = User.get_by_email(email)
        if not user:
            # register the user
            user = User(
                username=email.split('@')[0],
                email=email,
                avatar=resp['picture'],
                signature='',
                name=resp['name'],
                password=token_urlsafe(20),
            )
            db.session.add(user)
            db.session.commit()
            create_welcome_message(user)
        if user and user.is_enabled:
            # authenticate the user
            init_session(user.id)
            return redirect(request.args.get('next') or url_for('core.home'))
        flash('User not found.', category='error')
    return redirect(url_for('auth.login'))

# password recovery flow controllers

def reset_flow(message):
    session.pop('reset_id', None)
    session.pop('reset_token', None)
    flash(message)
    return redirect(url_for('auth.reset_init'))

@blp.route('/reset', methods=['GET', 'POST'])
@validate(['username'])
def reset_init():
    if request.method == 'POST':
        username = request.form['username']
        query = select(User).where(text("username='{}'".format(username)))
        try:
            user = db.session.execute(query).scalars().first()
        except:
            user = None
        if user:
            if Config.get_value('OOB_RESET_ENABLE'):
                # initialize the out-of-band reset flow
                reset_token = Token(
                    value=generate_timestamp_token(),
                    owner=user
                )
                db.session.add(reset_token)
                db.session.commit()
                link = url_for('auth.reset_password_oob', token=reset_token.value, _external=True)
                email = Email(
                    sender = 'no-reply@pwnedhub.com',
                    receiver = user.email,
                    subject = 'PwnedHub Password Reset',
                    body = f"Hi {user.name}!<br><br>Visit the following link to reset your password.<br><br><a href=\"{link}\">{link}</a><br><br>See you soon!",
                )
                db.session.add(email)
                db.session.commit()
                flash('Check your email to reset your password.')
                return redirect(url_for('auth.reset_init'))
            # initialize the in-band reset flow
            session['reset_id'] = user.id
            return redirect(url_for('auth.reset_question'))
        else:
            flash('User not recognized.')
    return render_template('reset_init.html')

@blp.route('/reset/question', methods=['GET', 'POST'])
@validate(['answer'])
def reset_question():
    if Config.get_value('OOB_RESET_ENABLE'):
        abort(404)
    # validate flow control
    if not session.get('reset_id'):
        return reset_flow('Reset improperly initialized.')
    user = User.query.get(session.get('reset_id'))
    if request.method == 'POST':
        answer = request.form['answer']
        if user.answer == answer:
            return redirect(url_for('auth.reset_password'))
        return reset_flow('Incorrect answer.')
    return render_template('reset_question.html', question=user.question_as_string)

@blp.route('/reset/password', methods=['GET', 'POST'])
@validate(['password'])
def reset_password():
    if Config.get_value('OOB_RESET_ENABLE'):
        abort(404)
    # validate flow control
    if not session.get('reset_id'):
        return reset_flow('Reset improperly initialized.')
    user = User.query.get(session.get('reset_id'))
    if request.method == 'POST':
        password = request.form['password']
        if is_valid_password(password):
            session.pop('reset_id', None)
            user.password = password
            db.session.commit()
            flash('Password reset. Please log in.')
            return redirect(url_for('auth.login'))
        flash('Password does not meet complexity requirements.')
    return render_template('reset_password.html', user=user)

@blp.route('/reset/password/<string:token>', methods=['GET', 'POST'])
@validate(['password'])
def reset_password_oob(token):
    if not Config.get_value('OOB_RESET_ENABLE'):
        abort(404)
    # validate the reset token
    reset_token = Token.get_by_value(token)
    if not reset_token:
        return reset_flow('Invalid reset token.')
    if not reset_token.is_valid:
        Token.purge()
        return reset_flow('Invalid reset token.')
    if request.method == 'POST':
        password = request.form['password']
        if is_valid_password(password):
            reset_token.owner.password = password
            db.session.delete(reset_token)
            db.session.commit()
            flash('Password reset. Please log in.')
            return redirect(url_for('auth.login'))
        flash('Password does not meet complexity requirements.')
    return render_template('reset_password.html', token=reset_token.value, user=reset_token.owner)
