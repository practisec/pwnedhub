# -*- coding: utf-8 -*-

"""
Adds server-side session support to your application via SQLAlchemy interface.

Derived from the Flask-Session extension, but includes major changes and fixes
for several session management vulnerabilites, e.g. fixation, persistence, etc.
"""

from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle
from flask.sessions import SessionInterface
from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import Signer, BadSignature, want_bytes
import binascii
import os

# for python 2, otherwise str
text_type = unicode

def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds

class Session(object):
    """This class is used to add Server-side Session to one or more Flask applications."""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """This is used to set up session for your app object.

        :param app: the Flask app object with proper configuration.
        """
        app.session_interface = self._get_interface(app)

    def _get_interface(self, app):
        config = app.config.copy()
        config.setdefault('SESSION_TYPE', 'null')
        config.setdefault('SESSION_PERMANENT', True)
        config.setdefault('SESSION_USE_SIGNER', False)
        config.setdefault('SESSION_KEY_PREFIX', 'session:')
        config.setdefault('SESSION_SQLALCHEMY', None)
        config.setdefault('SESSION_SQLALCHEMY_TABLE', 'sessions')
        session_interface = SqlAlchemySessionInterface(
            app,
            config['SESSION_SQLALCHEMY'],
            config['SESSION_SQLALCHEMY_TABLE'],
            config['SESSION_KEY_PREFIX'],
            config['SESSION_USE_SIGNER'],
            config['SESSION_PERMANENT'],
        )
        return session_interface

class SqlAlchemySession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        if permanent:
            self.permanent = permanent
        self.modified = False
        self._rotate = False

    def rotate(self):
        self._rotate = True

class SqlAlchemySessionInterface(SessionInterface):
    """Uses the Flask-SQLAlchemy from a flask app as a session backend.

    :param app: A Flask app instance.
    :param db: A Flask-SQLAlchemy instance.
    :param table: The table name you want to use.
    :param key_prefix: A prefix that is added to all store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = SqlAlchemySession

    def __init__(self, app, db, table, key_prefix, use_signer=False, permanent=True):
        if db is None:
            from flask.ext.sqlalchemy import SQLAlchemy
            db = SQLAlchemy(app)
        self.db = db
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent

        class Session(self.db.Model):
            __tablename__ = table

            id = self.db.Column(self.db.Integer, primary_key=True)
            session_id = self.db.Column(self.db.String(256), unique=True)
            data = self.db.Column(self.db.Text)
            expiry = self.db.Column(self.db.DateTime)

            def __init__(self, session_id, data, expiry):
                self.session_id = session_id
                self.data = data
                self.expiry = expiry

            def __repr__(self):
                return '<Session data %s>' % self.data

        self.db.create_all()
        self.sql_session_model = Session

    def _generate_sid(self):
        return binascii.hexlify(os.urandom(16))

    def _get_signer(self, app):
        if not app.secret_key:
            return None
        return Signer(app.secret_key, salt='flask-session', key_derivation='hmac')

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)
        if self.use_signer:
            signer = self._get_signer(app)
            if signer is None:
                return None
            try:
                sid = signer.unsign(sid)
            except BadSignature:
                sid = self._generate_sid()
                return self.session_class(sid=sid, permanent=self.permanent)
        store_id = self.key_prefix + sid
        saved_session = self.sql_session_model.query.filter_by(session_id=store_id).first()
        if saved_session and saved_session.expiry <= datetime.utcnow():
            # purge expired session
            self.db.session.delete(saved_session)
            self.db.session.commit()
            saved_session = None
        if saved_session:
            try:
                val = saved_session.data
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        store_id = self.key_prefix + session.sid
        saved_session = self.sql_session_model.query.filter_by(session_id=store_id).first()
        if not session:
            if session.modified:
                if saved_session:
                    self.db.session.delete(saved_session)
                    self.db.session.commit()
                response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
            return
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        sid = session.sid
        session_changed = False
        if saved_session:
            if session._rotate:
                sid = self._generate_sid()
                new_store_sid = self.key_prefix + sid
                saved_session.session_id = new_store_sid
                session_changed = True
            saved_session.data = val
            saved_session.expiry = expires
            self.db.session.commit()
            session.sid = sid
        else:
            new_session = self.sql_session_model(store_id, val, expires)
            self.db.session.add(new_session)
            self.db.session.commit()
            session_changed = True
        if self.use_signer:
            session_id = self._get_signer(app).sign(want_bytes(session.sid))
        else:
            session_id = session.sid
        if session_changed:
            response.set_cookie(
                app.session_cookie_name,
                session_id,
                expires=expires,
                httponly=httponly,
                path=path,
                secure=secure
            )
