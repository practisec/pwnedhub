from pwnedhub import app, db
from constants import ROLES, QUESTIONS, STATUSES
from utils import xor_encrypt, xor_decrypt
import datetime

class Tool(db.Model):
    __tablename__ = 'tools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "<Tool '{}'>".format(self.name)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    comment = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return "<Message '{}'>".format(self.id)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    username = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String)
    question = db.Column(db.Integer, nullable=False)
    answer = db.Column(db.String, nullable=False)
    notes = db.Column(db.String)
    role = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.Integer, nullable=False, default=1)
    messages = db.relationship('Message', backref='user', lazy='dynamic')

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
        return xor_decrypt(self.password_hash, app.config['PW_ENC_KEY'])

    @property
    def created_as_string(self):
        return self.created.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = xor_encrypt(password, app.config['PW_ENC_KEY'])

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
        if self.password_hash == xor_encrypt(password, app.config['PW_ENC_KEY']):
            return True
        return False

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    player = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    recid = db.Column(db.Integer)
    recording = db.Column(db.String, nullable=False)

def __repr__(self):
        return "<Score '{}:{}'>".format(self.player, self.score)
