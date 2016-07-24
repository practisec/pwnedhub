# -*- coding: utf-8 -*-

"""
Implements server-side session with sliding timeout for Flask applications via a
SQLAlchemy interface. Derived from the Flask-Session extension, but includes major
changes and fixes for several session management vulnerabilities, e.g. fixation,
persistence, etc.
"""

from datetime import datetime, timedelta
try:
    import cPickle as pickle
except ImportError:
    import pickle
from flask.sessions import SessionInterface
from flask.sessions import SessionMixin
from itsdangerous import want_bytes
from werkzeug.datastructures import CallbackDict
import binascii
import os

class Session(object):
    """This class is used to add server-side session to one or more Flask applications."""

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
        config.setdefault('SESSION_SQLALCHEMY', None)
        config.setdefault('SESSION_SQLALCHEMY_TABLE', 'sessions')
        config.setdefault('SESSION_KEY_PREFIX', 'session:')
        session_interface = SqlAlchemySessionInterface(
            app,
            config['SESSION_SQLALCHEMY'],
            config['SESSION_SQLALCHEMY_TABLE'],
            config['SESSION_KEY_PREFIX'],
        )
        return session_interface

class SqlAlchemySession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.modified = False
        self._rotate = False

    def rotate(self):
        self._rotate = True

class SqlAlchemySessionInterface(SessionInterface):
    """Uses the Flask-SQLAlchemy from a Flask app as a session backend.

    :param app: A Flask app instance.
    :param db: A Flask-SQLAlchemy instance.
    :param table: The table name you want to use.
    :param key_prefix: A prefix that is added to all store keys.
    """

    serializer = pickle
    session_class = SqlAlchemySession

    def __init__(self, app, db, table, key_prefix):
        if db is None:
            from flask_sqlalchemy import SQLAlchemy
            db = SQLAlchemy(app)
        self.db = db
        self.key_prefix = key_prefix

        class Session(self.db.Model):
            __tablename__ = table

            id = self.db.Column(self.db.Integer, primary_key=True)
            session_id = self.db.Column(self.db.String(256), unique=True)
            data = self.db.Column(self.db.LargeBinary)
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

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        # create a new session if the request does not include a token
        if not sid:
            return self.session_class(sid=self._generate_sid())
        # attempt to retrieve the session associated with the given token
        store_id = self.key_prefix + sid
        saved_session = self.sql_session_model.query.filter_by(session_id=store_id).first()
        # create a new session if the token doesn't represent a valid session
        if not saved_session:
            return self.session_class(sid=self._generate_sid())
        # create a new session if the session has expired
        elif saved_session.expiry <= datetime.utcnow():
            # purge the expired session
            self.db.session.delete(saved_session)
            self.db.session.commit()
            return self.session_class(sid=self._generate_sid())
        # handle valid sessions
        else:
            try:
                val = saved_session.data
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        store_id = self.key_prefix + session.sid
        saved_session = self.sql_session_model.query.filter_by(session_id=store_id).first()
        # destroy the session and token for logged out sessions
        if not session:
            if session.modified:
                if saved_session:
                    self.db.session.delete(saved_session)
                    self.db.session.commit()
                response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
                return
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = datetime.utcnow() + app.permanent_session_lifetime
        val = self.serializer.dumps(dict(session))
        sid = session.sid
        session_id_changed = False
        # handle existing sessions
        if saved_session:
            # rotate sessions to prevent fixation
            if session._rotate:
                sid = self._generate_sid()
                new_store_sid = self.key_prefix + sid
                # update the session id
                saved_session.session_id = new_store_sid
                session_id_changed = True
            # update the session data
            saved_session.data = val
            # update the session expiry
            saved_session.expiry = expires
            self.db.session.commit()
            session.sid = sid
        # handle new sessions
        else:
            # sids for new sessions are created in the open_session method
            new_session = self.sql_session_model(store_id, val, expires)
            self.db.session.add(new_session)
            self.db.session.commit()
            session_id_changed = True
        # handle session tokens
        if session_id_changed:
            # create a permanent cookie by expiring in 10 years
            expires = datetime.utcnow() + timedelta(0, 315360000)
            response.set_cookie(
                app.session_cookie_name,
                session.sid,
                expires=expires,
                httponly=httponly,
                path=path,
                secure=secure
            )
