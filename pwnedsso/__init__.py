from flask import Flask
from pwnedsso.extensions import db
import os

def create_app():

    # create the Flask application
    app = Flask(__name__, static_url_path='/static')

    # configure the Flask application
    config_class = os.getenv('CONFIG', default='Development')
    app.config.from_object('pwnedsso.config.{}'.format(config_class.title()))

    db.init_app(app)

    from pwnedsso.routes.sso import blp as SsoBlueprint
    app.register_blueprint(SsoBlueprint)

    return app
