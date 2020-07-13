from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_socketio import SocketIO
from common import db
from common.models import Config
from redis import Redis
import rq

cors = CORS()
socketio = SocketIO()

def create_app(config='Development'):

    # setting the static_url_path to blank serves static files from the web root
    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedapi.config.{}'.format(config.title()))

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = rq.Queue('pwnedhub-tasks', connection=app.redis)

    def is_allowed_origin(response):
        for k, v in response.headers:
            if k == 'Access-Control-Allow-Origin':
                return v in app.config['ALLOWED_ORIGINS']
        return False

    def remove_cors_headers(response):
        to_remove = []
        for k, v in response.headers:
            if any(k.startswith(s) for s in ['Access-Control-', 'Vary']):
                to_remove.append(k)
        for name in to_remove:
            del response.headers[name]
        return response

    # must be set before initializing the CORS extension to modify
    # headers created by the extension's `after_request` methods
    @app.after_request
    def config_cors(response):
        if Config.get_value('CORS_RESTRICT'):
            # apply the CORS whitelist from the config
            if not is_allowed_origin(response):
                response = remove_cors_headers(response)
        return response

    db.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config['ALLOWED_ORIGINS'])

    from pwnedapi.views.api import resources
    app.register_blueprint(resources)

    from pwnedapi.views import websockets

    return app, socketio
