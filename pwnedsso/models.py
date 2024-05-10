from flask import current_app
from pwnedsso import db
from pwnedsso.utils import get_current_utc_time, get_local_from_utc, xor_encrypt
from secrets import token_urlsafe


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

    @property
    def is_enabled(self):
        if self.status == 1:
            return True
        return False

    def check_password(self, password):
        if self.password_hash == xor_encrypt(password, current_app.config['SECRET_KEY']):
            return True
        return False

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)
