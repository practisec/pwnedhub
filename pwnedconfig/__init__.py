from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object('pwnedconfig.config.{}'.format(config.title()))

    db.init_app(app)

    # custom jinja global for accessing dynamic configuration values
    from pwnedconfig.models import Config
    app.jinja_env.globals['app_config'] = Config.get_value

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedconfig.views.config import blp as ConfigBlurprint
    from pwnedconfig.views.email import blp as EmailBlurprint
    app.register_blueprint(ConfigBlurprint)
    app.register_blueprint(EmailBlurprint)

    return app

def init_db():
    app = create_app('Production')
    with app.app_context():
        db.create_all()
    print('Database initialized.')
