from pwnedadmin import db
from pwnedadmin.constants import RESTRICTED_USERS
from pwnedadmin.utils import get_current_utc_time, get_local_from_utc


class Config(db.Model):
    __tablename__ = 'configs'
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
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=get_current_utc_time)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    @property
    def created_as_string(self):
        return get_local_from_utc(self.created).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_unrestricted():
        return Email.query.filter(Email.receiver.notin_(RESTRICTED_USERS))

    @staticmethod
    def get_by_receiver(receiver):
        return Email.query.filter_by(receiver=receiver)

    def __repr__(self):
        return "<Email '{}'>".format(self.id)
