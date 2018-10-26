from flask import current_app
from pwnedhub import db
from constants import ROLES, QUESTIONS, STATUSES
from utils import xor_encrypt, xor_decrypt
import datetime

class Tool(db.Model):
    __tablename__ = 'tools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Tool '{}'>".format(self.name)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string, 
            'comment': self.comment,
            'author': {
                'id': self.user.id,
                'name': self.user.name,
                'username': self.user.username,
            },
        }

    def __repr__(self):
        return "<Message '{}'>".format(self.id)

class Mail(db.Model):
    __tablename__ = 'mail'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    subject = db.Column(db.Text)
    content = db.Column(db.Text)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read = db.Column(db.Integer, nullable=False, default=0)

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return "<Mail '{}'>".format(self.id)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    username = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255))
    question = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    sent_mail = db.relationship('Mail', foreign_keys='Mail.sender_id', backref='sender', lazy='dynamic')
    received_mail = db.relationship('Mail', foreign_keys='Mail.receiver_id', backref='receiver', lazy='dynamic')

    @property
    def role_as_string(self):
        return ROLES[self.role]

    @property
    def status_as_string(self):
        return STATUSES[self.status]

    @property
    def question_as_string(self):
        return QUESTIONS[self.question]

    @property
    def password_as_string(self):
        return xor_decrypt(self.password_hash, current_app.config['PW_ENC_KEY'])

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = xor_encrypt(password, current_app.config['PW_ENC_KEY'])

    @property
    def is_admin(self):
        if self.role == 0:
            return True
        return False

    @property
    def is_enabled(self):
        if self.status == 1:
            return True
        return False

    def check_password(self, password):
        if self.password_hash == xor_encrypt(password, current_app.config['PW_ENC_KEY']):
            return True
        return False

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'username': self.username,
            'name': self.name,
            'role': self.role_as_string,
        }

    def __repr__(self):
        return "<User '{}'>".format(self.username)
