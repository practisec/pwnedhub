from flask import Blueprint, render_template, Response

static = Blueprint('static', __name__)

@static.route('/constants.js')
def constants_js():
    return Response(render_template('constants.js'), mimetype='text/javascript')
