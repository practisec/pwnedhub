from flask import current_app, url_for
from pwnedhub import db
from pwnedhub.constants import ROLES, QUESTIONS, USER_STATUSES
from pwnedhub.utils import get_current_utc_time, get_local_from_utc, xor_encrypt, xor_decrypt
from secrets import token_urlsafe


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


class Note(BaseModel):
    __tablename__ = 'notes'
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='notes')

    def __repr__(self):
        return "<Note '{}'>".format(self.name)


class Tool(BaseModel):
    __tablename__ = 'tools'
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Tool '{}'>".format(self.name)


class Message(BaseModel):
    __tablename__ = 'messages'
    comment = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', back_populates='messages')

    def __repr__(self):
        return "<Message '{}'>".format(self.id)


class Mail(BaseModel):
    __tablename__ = 'mail'
    subject = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    read = db.Column(db.Integer, nullable=False, default=0)
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_mail')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_mail')

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
    notes = db.relationship('Note', back_populates='owner', lazy='dynamic')
    messages = db.relationship('Message', back_populates='author', lazy='dynamic')
    tokens = db.relationship('Token', back_populates='owner', lazy='dynamic')
    sent_mail = db.relationship('Mail', foreign_keys=[Mail.sender_id], back_populates='sender', lazy='dynamic')
    received_mail = db.relationship('Mail', foreign_keys=[Mail.receiver_id], back_populates='receiver', lazy='dynamic')

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

    @property
    def has_unread_mail(self):
        for letter in self.received_mail:
            if letter.read == 0:
                return True
        return False

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

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class Token(BaseModel):
    __tablename__ = 'tokens'
    value = db.Column(db.String(255), nullable=False)
    ttl = db.Column(db.Integer, nullable=False, default=600)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', back_populates='tokens')

    @property
    def is_valid(self):
        current = get_current_utc_time().replace(tzinfo=None)
        diff = current - self.created
        if diff.total_seconds() > self.ttl:
            return False
        return True

    @staticmethod
    def get_by_value(value):
        return Token.query.filter_by(value=value).first()

    @staticmethod
    def purge():
        invalid_tokens = [t for t in Token.query.all() if not t.is_valid]
        for invalid_token in invalid_tokens:
            db.session.delete(invalid_token)
        db.session.commit()

    def __repr__(self):
        return "<Token '{}'>".format(self.value)
