from flask import Flask, Blueprint

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object('pwnedspa.config.{}'.format(config.title()))

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedspa.views.core import blp as CoreBlueprint
    app.register_blueprint(CoreBlueprint)

    return app
