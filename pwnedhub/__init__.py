from flask import Flask, request, render_template, g, Blueprint, __version__
from pwnedhub.extensions import db, sess
from pwnedhub.utils import get_current_utc_time, generate_nonce
from urllib.parse import unquote
from redis import Redis
import click
import rq

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

    from pwnedhub.routes.core import blp as CoreBlueprint
    from pwnedhub.routes.auth import blp as AuthBlueprint
    from pwnedhub.routes.errors import blp as ErrorsBlueprint
    app.register_blueprint(CoreBlueprint)
    app.register_blueprint(AuthBlueprint)
    app.register_blueprint(ErrorsBlueprint)

    @app.cli.command('init')
    @click.argument('dataset')
    def init_data(dataset):
        from flask import current_app
        from pwnedhub import models
        import json
        import os
        db.create_all(bind_key=None)
        for cls in models.BaseModel.__subclasses__():
            fixture_path = os.path.join(current_app.root_path, 'fixtures', dataset, f"{cls.__table__.name}.json")
            if os.path.exists(fixture_path):
                print(f"Processing {fixture_path}.")
                with open(fixture_path) as fp:
                    for row in json.load(fp):
                        db.session.add(cls(**row))
        db.session.commit()
        print('Database initialized.')

    @app.cli.command('export')
    def export_data():
        from pwnedhub.models import BaseModel
        import json
        for cls in BaseModel.__subclasses__():
            objs = [obj.serialize_for_export() for obj in cls.query.all()]
            if objs:
                print(f"\n***** {cls.__table__.name}.json *****\n")
                print(json.dumps(objs, indent=4, default=str))
        print('Database exported.')

    @app.cli.command('purge')
    def purge_data():
        db.drop_all(bind_key=None)
        db.session.commit()
        print('Database purged.')

    return app
