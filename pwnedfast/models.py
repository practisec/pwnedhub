from pwnedfast.config import settings
from pwnedfast.constants import ROLES, USER_STATUSES
from pwnedfast.database import Base
from pwnedfast.security import xor_encrypt, xor_decrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
import datetime

#db = get_db()

'''
class Config(Model):
    __tablename__ = 'configs'
    __bind_key__ = 'config'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    value = Column(Boolean, nullable=False)

    @staticmethod
    def get_by_name(name):
        return Config.query.filter_by(name=name).first()

    @staticmethod
    def get_value(name):
        return Config.query.filter_by(name=name).first().value

    def __repr__(self):
        return "<Config '{}'>".format(self.name)
'''


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    modified = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    @property
    def _name(self):
        return self.__class__.__name__.lower()

    @property
    def created_as_string(self):
        return self.created.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def modified_as_string(self):
        return self.modified.strftime('%Y-%m-%d %H:%M:%S')


class Scan(BaseModel):
    __tablename__ = 'scans'
    id = Column(String(36), primary_key=True)
    command = Column(String(255), nullable=False)
    results = Column(Text)
    complete = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "<Scan '{}'>".format(self.name)


class Membership(BaseModel):
    __tablename__ = 'memberships'
    user_id = Column(Integer, ForeignKey('users.id'))
    room_id = Column(Integer, ForeignKey('rooms.id'))
    level = Column(Integer, nullable=False, default=1)
    user = relationship('User', backref=backref('memberships', lazy='dynamic', cascade='all, delete-orphan'))
    room = relationship('Room', backref=backref('memberships', lazy='dynamic', cascade='all, delete-orphan'))
    __table_args__ = (UniqueConstraint('user_id', 'room_id', name='membership_id'),)

    def __repr__(self):
        return "<Membership '{}'>".format(self.id)


class Note(BaseModel):
    __tablename__ = 'notes'
    name = Column(String(255), nullable=False)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "<Note '{}'>".format(self.name)


class Tool(BaseModel):
    __tablename__ = 'tools'
    name = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return "<Tool '{}'>".format(self.name)


class Room(BaseModel):
    __tablename__ = 'rooms'
    name = Column(String(255), nullable=False, unique=True)
    private = Column(Boolean, nullable=False)
    messages = relationship('Message', backref='room', lazy='dynamic')
    members = relationship('User', secondary='memberships', viewonly=True, lazy='dynamic')

    @property
    def is_private(self):
        return self.private

    @property
    def is_public(self):
        return not self.private

    '''
    @staticmethod
    def get_public_rooms():
        return Room.query.filter_by(private=False).all()

    @staticmethod
    def get_by_name(name):
        return Room.query.filter_by(name=name).first()
    '''

    def __repr__(self):
        return "<Room '{}'>".format(self.name)


class Message(BaseModel):
    __tablename__ = 'messages'
    comment = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    def __repr__(self):
        return "<Message '{}'>".format(self.id)


class User(BaseModel):
    __tablename__ = 'users'
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    avatar = Column(Text)
    signature = Column(Text)
    password_hash = Column(String(255))
    role = Column(Integer, nullable=False, default=1)
    status = Column(Integer, nullable=False, default=1)
    notes = relationship('Note', backref='owner', lazy='dynamic')
    scans = relationship('Scan', backref='owner', lazy='dynamic')
    messages = relationship('Message', backref='author', lazy='dynamic')
    rooms = relationship('Room', secondary='memberships', viewonly=True, lazy='dynamic')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        # create default memberships
        for room in Room.get_public_rooms():
            membership = Membership(user=self, room=room, level=1)
            self.rooms.append(membership)
        '''

    @property
    def role_as_string(self):
        return ROLES[self.role]

    @property
    def status_as_string(self):
        return USER_STATUSES[self.status]

    @property
    def password_as_string(self):
        return xor_decrypt(self.password_hash, settings.SECRET_KEY)

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = xor_encrypt(password, settings.SECRET_KEY)

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

    '''
    def create_membership(self, room, level=1):
        membership = Membership(user=self, room=room, level=level)
        self.rooms.append(membership)
        db.session.add(membership)
        db.session.commit()
        return membership
    '''

    def check_password(self, password):
        if self.password_hash == xor_encrypt(password, settings.SECRET_KEY):
            return True
        return False

    '''
    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()
    '''

    def __repr__(self):
        return "<User '{}'>".format(self.username)
