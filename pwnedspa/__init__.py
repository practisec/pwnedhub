from flask import Flask
from common.models import Config

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    # files from the web root, allowing for robots.txt
    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedspa.config.{}'.format(config.title()))

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    from pwnedspa.views.core import core
    from pwnedspa.views.errors import errors
    app.register_blueprint(core)
    app.register_blueprint(errors)

    return app
