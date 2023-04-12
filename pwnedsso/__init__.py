from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config='Development'):

    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedsso.config.{}'.format(config.title()))

    db.init_app(app)

    from pwnedsso.views.sso import sso
    app.register_blueprint(sso)

    return app
