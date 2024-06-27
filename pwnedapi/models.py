from flask import url_for
from pwnedapi import db
from pwnedapi.constants import ROLES, USER_STATUSES
from pwnedapi.utils import get_current_utc_time, get_local_from_utc

memberships = db.Table('memberships',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id')),
)


class Config(db.Model):
    __tablename__ = 'configs'
    __bind_key__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Boolean, nullable=False)

    @staticmethod
    def get_by_name(name):
        return Config.query.filter_by(name=name).first()

    @staticmethod
    def get_value(name):
        return Config.query.filter_by(name=name).first().value

    def __repr__(self):
        return "<Config '{}'>".format(self.name)


class Email(db.Model):
    __tablename__ = 'emails'
    __bind_key__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=get_current_utc_time)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    @property
    def created_as_string(self):
        return get_local_from_utc(self.created).strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return "<Email '{}'>".format(self.id)


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=get_current_utc_time)
    modified = db.Column(db.DateTime, nullable=False, default=get_current_utc_time, onupdate=get_current_utc_time)

    @property
    def _name(self):
        return self.__class__.__name__.lower()

    @property
    def created_as_string(self):
        return get_local_from_utc(self.created).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def modified_as_string(self):
        return get_local_from_utc(self.modified).strftime("%Y-%m-%d %H:%M:%S")

    def serialize_for_export(self):
        return {c.name: getattr(self, c.name) for c in self.__mapper__.columns}


class Scan(BaseModel):
    __tablename__ = 'scans'
    id = db.Column(db.String(36), primary_key=True)
    command = db.Column(db.String(255), nullable=False)
    results = db.Column(db.Text)
    complete = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='scans')

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


class Note(BaseModel):
    __tablename__ = 'notes'
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='notes')

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
    messages = db.relationship('Message', back_populates='room', lazy='dynamic')
    members = db.relationship('User', secondary=memberships, back_populates='rooms', lazy='dynamic')


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

    def get_peer(self, user):
        if user and self.is_private:
            for member in self.members.all():
                if member.id != user.id:
                    return member
        return None

    def serialize(self, user=None):
        peer = self.get_peer(user)
        return {
            'id': self.id,
            'created': self.created_as_string,
            'name': self.name,
            'private': self.private,
            'peer': peer.serialize() if peer else None,
        }

    def __repr__(self):
        return "<Room '{}'>".format(self.name)


class Message(BaseModel):
    __tablename__ = 'messages'
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    author = db.relationship('User', back_populates='messages')
    room = db.relationship('Room', back_populates='messages')

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'comment': self.comment,
            'author': {
                'id': self.author.id,
                'name': self.author.name,
                'email': self.author.email,
                'avatar': self.author.avatar_or_default,
            },
            'room': {
                'id': self.room.id,
                'name': self.room.name,
            },
        }

    def __repr__(self):
        return "<Message '{}'>".format(self.id)


class User(BaseModel):
    __tablename__ = 'users'
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.Text)
    signature = db.Column(db.Text)
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    notes = db.relationship('Note', back_populates='owner', lazy='dynamic')
    scans = db.relationship('Scan', back_populates='owner', lazy='dynamic')
    messages = db.relationship('Message', back_populates='author', lazy='dynamic')
    rooms = db.relationship('Room', secondary=memberships, back_populates='members', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create default memberships
        for room in Room.get_public_rooms():
            self.create_membership(room)

    @property
    def role_as_string(self):
        return ROLES[self.role]

    @property
    def status_as_string(self):
        return USER_STATUSES[self.status]

    @property
    def avatar_or_default(self):
        return self.avatar or url_for('common.static', filename='images/avatars/default.png')

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

    def create_membership(self, room):
        self.rooms.append(room)
        db.session.commit()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def serialize(self):
        return {
            'id': self.id,
            'created': self.created_as_string,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar_or_default,
            'signature': self.signature,
            'role': self.role_as_string,
            'status': self.status_as_string,
        }

    def __repr__(self):
        return "<User '{}'>".format(self.email)
