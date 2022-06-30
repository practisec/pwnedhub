from flask import Flask
from flask_session import Session
from common import db
from common.models import Config
from common.utils import generate_csrf_token
from datetime import datetime
from urllib.parse import unquote

sess = Session()

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    # files from the web root, allowing for robots.txt, etc.
    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedhub.config.{}'.format(config.title()))

    db.init_app(app)
    sess.init_app(app)

    # custom jinja global for accessing dynamic configuration values
    app.jinja_env.globals['app_config'] = Config.get_value
    # custom jinja global for the current date
    # used in the layout to keep the current year
    app.jinja_env.globals['date'] = datetime.now()
    # custom jinja global for setting CSRF tokens
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    # custom jinja filter to decode urls
    app.jinja_env.filters['urldecode'] = lambda s: unquote(s)
    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    @app.template_filter('markdown')
    def markdown_filter(data):
        '''
        Use: {{ comment.content|markdown }}
        '''
        from flask import Markup
        from markdown import markdown
        return Markup(markdown(data or '', extensions=app.config['MARKDOWN_EXTENSIONS']))

    from pwnedhub.views.core import core
    from pwnedhub.views.auth import auth
    from pwnedhub.views.errors import errors
    app.register_blueprint(core)
    app.register_blueprint(auth)
    app.register_blueprint(errors)

    return app

def init_db(config='Development'):
    app = create_app(config)
    with app.app_context():
        db.create_all()
    print('Database initialized.')

def drop_db(config='Development'):
    app = create_app(config)
    with app.app_context():
        db.drop_all()
    print('Database dropped.')

def interact(config='Development'):
    app = create_app(config)
    with app.app_context():
        import pdb; pdb.set_trace()
