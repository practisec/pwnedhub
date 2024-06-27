from flask import Flask, request, render_template, g, Blueprint, __version__
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from pwnedhub.utils import get_current_utc_time, generate_nonce
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
    app.jinja_env.globals['date'] = get_current_utc_time()
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

    @app.before_request
    def render_mobile():
        if any(x in request.user_agent.string.lower() for x in ['android', 'iphone', 'ipad']):
            if not request.endpoint in ('static', 'common.static'):
                return render_template('mobile.html')

    @app.before_request
    def add_nonce():
        g.nonce = generate_nonce()

    @app.after_request
    def add_header(response):
        response.headers['X-Powered-By'] = 'Flask/{}'.format(__version__)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if Config.get_value('CSP_PROTECT'):
            response.headers['Content-Security-Policy'] = f"script-src 'unsafe-inline' 'nonce-{g.nonce}'; script-src-attr 'unsafe-inline'; object-src 'none'; base-uri 'none'"
        return response

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedhub.views.core import blp as CoreBlueprint
    from pwnedhub.views.auth import blp as AuthBlueprint
    from pwnedhub.views.errors import blp as ErrorsBlueprint
    app.register_blueprint(CoreBlueprint)
    app.register_blueprint(AuthBlueprint)
    app.register_blueprint(ErrorsBlueprint)

    @app.cli.command("init")
    def init_data():
        from pwnedhub import models
        db.create_all()
        print('Database initialized.')

    @app.cli.command("export")
    def export_data():
        from pwnedhub.models import Note, Tool, Message, Mail, User, Token
        import json
        for cls in [Note, Tool, Message, Mail, User, Token]:
            objs = [obj.serialize_for_export() for obj in cls.query.all()]
            if objs:
                print(f"\n***** {cls.__table__.name}.json *****\n")
                print(json.dumps(objs, indent=4, default=str))
        print('Database exported.')

    return app
