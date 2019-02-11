from flask import current_app, url_for
from pwnedhub import db
from constants import ROLES, QUESTIONS, USER_STATUSES, BUG_STATUSES, VULNERABILITIES, SEVERITY
from utils import xor_encrypt, xor_decrypt
import datetime

class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    modified = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @property
    def _name(self):
        return self.__class__.__name__.lower()

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def modified_as_string(self):
        return self.modified.strftime("%Y-%m-%d %H:%M:%S")

class Tool(BaseModel):
    __tablename__ = 'tools'
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Tool '{}'>".format(self.name)

class Message(BaseModel):
    __tablename__ = 'messages'
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

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

class Mail(BaseModel):
    __tablename__ = 'mail'
    subject = db.Column(db.Text)
    content = db.Column(db.Text)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read = db.Column(db.Integer, nullable=False, default=0)

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'subject': self.subject,
            'content': self.content,
            'read': self.read,
            'sender': self.sender.serialize(public=True),
            'receiver': self.receiver.serialize(public=True),
        }

    def __repr__(self):
        return "<Mail '{}'>".format(self.id)

class Bug(BaseModel):
    __tablename__ = 'bugs'
    title = db.Column(db.String(255))
    vuln_id = db.Column(db.Integer, nullable=False, default=0)
    severity = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=False)
    impact = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    submitter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @property
    def vulnerability_as_string(self):
        return VULNERABILITIES[self.vuln_id][0]

    @property
    def severity_as_string(self):
        return SEVERITY[self.severity]

    @property
    def status_as_string(self):
        return BUG_STATUSES[self.status]

    @property
    def bounty(self):
        return VULNERABILITIES[self.vuln_id][1] * self.severity

    @property
    def is_validated(self):
        # includes any validation result
        # rejected, confirmed, and fixed
        if self.status > 0:
            return True
        return False

    @property
    def is_accepted(self):
        # includes confirmed and fixed
        if self.status > 1:
            return True
        return False

    def __repr__(self):
        return "<Bug '{}'>".format(self.title)

class User(BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.Text)
    signature = db.Column(db.Text)
    password_hash = db.Column(db.String(255))
    question = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    sent_mail = db.relationship('Mail', foreign_keys='Mail.sender_id', backref='sender', lazy='dynamic')
    received_mail = db.relationship('Mail', foreign_keys='Mail.receiver_id', backref='receiver', lazy='dynamic')
    bugs = db.relationship('Bug', foreign_keys='Bug.submitter_id', backref='submitter', lazy='dynamic')
    validations = db.relationship('Bug', foreign_keys='Bug.reviewer_id', backref='reviewer', lazy='dynamic')

    @property
    def reputation(self):
        rep = 0
        for bug in self.accepted_bugs:
            rep += bug.bounty
        for val in self.accepted_validations:
            rep += val.bounty/4
        return rep

    @property
    def accepted_bugs(self):
        return [b for b in self.bugs if b.is_accepted]

    @property
    def accepted_validations(self):
        return [v for v in self.validations if v.is_accepted]

    @property
    def completed_validations(self):
        return [v for v in self.validations if v.is_validated]

    @property
    def role_as_string(self):
        return ROLES[self.role]

    @property
    def status_as_string(self):
        return USER_STATUSES[self.status]

    @property
    def question_as_string(self):
        return QUESTIONS[self.question]

    @property
    def password_as_string(self):
        return xor_decrypt(self.password_hash, current_app.config['PW_ENC_KEY'])

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = xor_encrypt(password, current_app.config['PW_ENC_KEY'])

    @property
    def avatar_or_default(self):
        return self.avatar or url_for('static', filename='images/avatars/default.png')

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

    def serialize(self, public=False):
        if public:
            return {
                'id': self.id,
                'name': self.name,
            }
        return {
            'id': self.id,
            'created': self.created_as_string,
            'username': self.username,
            'name': self.name,
            'role': self.role_as_string,
        }

    def __repr__(self):
        return "<User '{}'>".format(self.username)

class Score(BaseModel):
    __tablename__ = 'scores'
    player = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    recid = db.Column(db.Integer)
    recording = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Score '{}:{}'>".format(self.player, self.score)
