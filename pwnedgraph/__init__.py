from flask import Flask, request, current_app
from flask_graphql import GraphQLView
from flask_sqlalchemy import SQLAlchemy
from pwnedgraph.constants import VOYAGER_HTML
import jwt

db = SQLAlchemy()

def create_app(config='Development'):

    app = Flask(__name__)
    app.config.from_object('pwnedgraph.config.{}'.format(config.title()))

    db.init_app(app)

    @app.before_request
    def parse_jwt():
        '''Adds the `jwt` object to the current request for later access.'''
        request.jwt = {}
        from pwnedgraph.utils import get_bearer_token
        token = get_bearer_token(request.headers)
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return
        request.jwt = payload

    @app.before_request
    def load_user():
        '''Adds the `user` object to the current request based on the JWT `sub` claim.'''
        request.user = None
        uid = request.jwt.get('sub')
        if uid:
            from pwnedgraph.models import User
            request.user = User.query.get(uid)

    from pwnedgraph.schema import schema
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True
        )
    )

    @app.route('/voyager', methods=['GET'])
    def graphql_voyager():
        return VOYAGER_HTML, 200

    return app
