from flask import Flask, Blueprint
from pwnedadmin.extensions import db
import click
import os

def create_app():

    # create the Flask application
    app = Flask(__name__, static_url_path='/static')

    # configure the Flask application
    config_class = os.getenv('CONFIG', default='Development')
    app.config.from_object('pwnedadmin.config.{}'.format(config_class.title()))

    db.init_app(app)

    # custom jinja global for accessing dynamic configuration values
    from pwnedadmin.models import Config
    app.jinja_env.globals['app_config'] = Config.get_value

    # misc jinja configuration variables
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    StaticBlueprint = Blueprint('common', __name__, static_url_path='/static/common', static_folder='../common/static')
    app.register_blueprint(StaticBlueprint)

    from pwnedadmin.routes.config import blp as ConfigBlurprint
    from pwnedadmin.routes.email import blp as EmailBlurprint
    app.register_blueprint(ConfigBlurprint)
    app.register_blueprint(EmailBlurprint)

    @app.cli.command('init')
    @click.argument('dataset')
    def init_data(dataset):
        from flask import current_app
        from pwnedadmin import models
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
        from pwnedadmin.models import BaseModel
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
