from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config='Development'):

    # setting the static_url_path to blank serves static
    app = Flask(__name__, static_url_path='/static')
    app.config.from_object('pwnedadmin.config.{}'.format(config.title()))

    db.init_app(app)

    # custom jinja global for accessing dynamic configuration values
    from pwnedadmin.models import Config
    app.jinja_env.globals['app_config'] = Config.get_value

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedadmin.views.config import blp as ConfigBlurprint
    from pwnedadmin.views.email import blp as EmailBlurprint
    app.register_blueprint(ConfigBlurprint)
    app.register_blueprint(EmailBlurprint)

    @app.cli.command("init")
    def init_data():
        from pwnedadmin import models
        db.create_all()
        print('Database initialized.')

    @app.cli.command("export")
    def export_data():
        from pwnedadmin.models import Config, Email
        import json
        for cls in [Config, Email]:
            objs = [obj.serialize_for_export() for obj in cls.query.all()]
            if objs:
                print(f"\n***** {cls.__table__.name}.json *****\n")
                print(json.dumps(objs, indent=4, default=str))
        print('Database exported.')

    return app
