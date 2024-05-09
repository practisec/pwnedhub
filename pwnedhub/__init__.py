from flask import Flask, Blueprint
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import unquote
from redis import Redis
import rq

db = SQLAlchemy()
sess = Session()

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    # files from the web root, allowing for robots.txt, etc.
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object('pwnedhub.config.{}'.format(config.title()))

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.bot_task_queue = rq.Queue('adminbot-tasks', connection=app.redis)

    db.init_app(app)
    sess.init_app(app)

    # custom jinja global for accessing dynamic configuration values
    from pwnedhub.models import Config
    app.jinja_env.globals['app_config'] = Config.get_value
    # custom jinja global for the current date
    # used in the layout to keep the current year
    app.jinja_env.globals['date'] = datetime.now()
    # custom jinja global for setting CSRF tokens
    from pwnedhub.utils import generate_csrf_token
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

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedhub.views.core import blp as CoreBlueprint
    from pwnedhub.views.auth import blp as AuthBlueprint
    from pwnedhub.views.errors import blp as ErrorsBlueprint
    app.register_blueprint(CoreBlueprint)
    app.register_blueprint(AuthBlueprint)
    app.register_blueprint(ErrorsBlueprint)

    return app

def init_db():
    app = create_app('Production')
    with app.app_context():
        db.create_all()
    print('Database initialized.')
