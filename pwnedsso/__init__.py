from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config='Development'):

    app = Flask(__name__, static_url_path='/static')
    app.config.from_object('pwnedsso.config.{}'.format(config.title()))

    db.init_app(app)

    from pwnedsso.views.sso import blp as SsoBlueprint
    app.register_blueprint(SsoBlueprint)

    return app
