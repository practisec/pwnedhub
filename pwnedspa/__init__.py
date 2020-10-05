from flask import Flask

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    app = Flask(__name__, static_url_path='')
    app.config.from_object('pwnedspa.config.{}'.format(config.title()))

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    from pwnedspa.views.core import core
    app.register_blueprint(core)

    return app
