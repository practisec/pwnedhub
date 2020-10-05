from flask import Flask
from common import db
from common.models import Config

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedconfig.config.{}'.format(config.title()))

    db.init_app(app)

    # custom jinja global for accessing dynamic configuration values
    app.jinja_env.globals['app_config'] = Config.get_value

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    from pwnedconfig.views.core import core
    app.register_blueprint(core)

    return app
