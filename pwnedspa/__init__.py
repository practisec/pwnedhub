from flask import Flask, Blueprint
import os

def create_app():

    # create the Flask application
    app = Flask(__name__, static_url_path='/static')

    # configure the Flask application
    config_class = os.getenv('CONFIG', default='Development')
    app.config.from_object('pwnedspa.config.{}'.format(config_class.title()))

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedspa.routes.core import blp as CoreBlueprint
    app.register_blueprint(CoreBlueprint)

    return app
