from flask import current_app, url_for
from common import db
from common.constants import ROLES, QUESTIONS, USER_STATUSES
from common.utils import xor_encrypt, xor_decrypt, get_jaccard_sim
from secrets import token_urlsafe
from sqlalchemy import event
from sqlalchemy.orm import object_session
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

class Config(db.Model):
    __tablename__ = 'configs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Boolean, nullable=False)

    @staticmethod
    def get_by_name(name):
        return Config.query.filter_by(name=name).first()

    @staticmethod
    def get_value(name):
        return Config.query.filter_by(name=name).first().value

    def __repr__(self):
        return "<Config '{}'>".format(self.name)

class Scan(BaseModel):
    __tablename__ = 'scans'
    id = db.Column(db.String(36), primary_key=True)
    command = db.Column(db.String(255), nullable=False)
    results = db.Column(db.Text)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def serialize(self, include_results=False):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'modified': self.modified_as_string,
            'command': self.command,
            'complete': self.complete,
        }

    def __repr__(self):
        return "<Scan '{}'>".format(self.name)

class Membership(BaseModel):
    __tablename__ = 'memberships'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    level = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship("User", backref=db.backref('memberships', lazy='dynamic', cascade="all, delete-orphan"))
    room = db.relationship("Room", backref=db.backref('memberships', lazy='dynamic', cascade="all, delete-orphan"))
    __table_args__ = (db.UniqueConstraint('user_id', 'room_id', name='membership_id'),)

    def serialize(self, include_results=False):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'level': self.level,
        }

    def __repr__(self):
        return "<Membership '{}'>".format(self.id)

class Note(BaseModel):
    __tablename__ = 'notes'
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'created': self.created_as_string,
            'modified': self.modified_as_string,
        }

    def __repr__(self):
        return "<Note '{}'>".format(self.name)

class Tool(BaseModel):
    __tablename__ = 'tools'
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'description': self.description,
        }

    def __repr__(self):
        return "<Tool '{}'>".format(self.name)

class Room(BaseModel):
    __tablename__ = 'rooms'
    name = db.Column(db.String(255), nullable=False, unique=True)
    private = db.Column(db.Boolean, nullable=False)
    messages = db.relationship('Message', backref='room', lazy='dynamic')
    members = db.relationship("User", secondary="memberships", viewonly=True, lazy='dynamic')

    @property
    def is_private(self):
        return self.private

    @property
    def is_public(self):
        return not self.private

    @staticmethod
    def get_public_rooms():
        return Room.query.filter_by(private=False).all()

    @staticmethod
    def get_by_name(name):
        return Room.query.filter_by(name=name).first()

    def serialize_with_context(self, user):
        serialized_room = self.serialize()
        if self.is_private:
            peer = self.members.filter(User.id != user.id).first()
            serialized_room['display'] = f"@{peer.name}"
        else:
            serialized_room['display'] = f"#{self.name}"
        return serialized_room

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'name': self.name,
            'display': self.name,
            'private': self.private,
        }

    def __repr__(self):
        return "<Room '{}'>".format(self.name)

class Message(BaseModel):
    __tablename__ = 'messages'
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'comment': self.comment,
            'author': {
                'id': self.author.id,
                'name': self.author.name,
                'username': self.author.username,
                'avatar': self.author.avatar_or_default,
            },
            'room': {
                'id': self.room.id,
                'name': self.room.name,
            },
        }

    def __repr__(self):
        return "<Message '{}'>".format(self.id)

class Mail(BaseModel):
    __tablename__ = 'mail'
    subject = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
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
            'sender': self.sender.serialize(),
            'receiver': self.receiver.serialize(),
        }

    def __repr__(self):
        return "<Mail '{}'>".format(self.id)

class User(BaseModel):
    __tablename__ = 'users'
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.Text)
    signature = db.Column(db.Text)
    password_hash = db.Column(db.String(255))
    question = db.Column(db.Integer, nullable=False, default=0)
    answer = db.Column(db.String(255), nullable=False, default=token_urlsafe(10))
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    notes = db.relationship('Note', backref='owner', lazy='dynamic')
    scans = db.relationship('Scan', backref='owner', lazy='dynamic')
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    sent_mail = db.relationship('Mail', foreign_keys='Mail.sender_id', backref='sender', lazy='dynamic')
    received_mail = db.relationship('Mail', foreign_keys='Mail.receiver_id', backref='receiver', lazy='dynamic')
    rooms = db.relationship("Room", secondary="memberships", viewonly=True, lazy='dynamic')

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
        return xor_decrypt(self.password_hash, current_app.config['SECRET_KEY'])

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = xor_encrypt(password, current_app.config['SECRET_KEY'])

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

    @property
    def has_unread_mail(self):
        for letter in self.received_mail:
            if letter.read == 0:
                return True
        return False

    def create_membership(self, room, level=1):
        membership = Membership(user=self, room=room, level=level)
        self.rooms.append(membership)
        db.session.add(membership)
        db.session.commit()
        return membership

    def check_password(self, password):
        if self.password_hash == xor_encrypt(password, current_app.config['SECRET_KEY']):
            return True
        return False

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'name': self.name,
            'avatar': self.avatar_or_default,
            'signature': self.signature,
        }

    def serialize_admin(self):
        return {
            **self.serialize(),
            'username': self.username,
            'email': self.email,
            'role': self.role_as_string,
            'status': self.status_as_string,
        }

    def serialize_self(self):
        return {
            **self.serialize_admin(),
            'question': self.question,
            'answer': self.answer,
        }

    def __repr__(self):
        return "<User '{}'>".format(self.username)

@event.listens_for(User, "after_insert")
def create_default_memberships(mapper, connection, user):
    for room in Room.get_public_rooms():
        membership = Membership(user=user, room=room, level=1)
        user.rooms.append(membership)
        object_session(user).add(membership)

class Score(BaseModel):
    __tablename__ = 'scores'
    player = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    recid = db.Column(db.Integer)
    recording = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Score '{}:{}'>".format(self.player, self.score)
