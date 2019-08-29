from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_socketio import SocketIO
from common import db
from common.utils import generate_csrf_token
from datetime import datetime
from urllib.parse import unquote

sess = Session()
socketio = SocketIO()

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    # files from the web root, allowing for robots.txt
    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedhub.config.{}'.format(config.title()))

    db.init_app(app)
    sess.init_app(app)
    socketio.init_app(app)

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

    from pwnedhub.views import websockets

    return app, socketio
