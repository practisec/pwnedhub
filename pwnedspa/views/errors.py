from flask import Blueprint, request, render_template
import traceback
import uuid

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def not_found(e):
    return render_template('404.html', message=request.url), 404

@errors.app_errorhandler(500)
def internal_server_error(e):
    message = traceback.format_exc()
    return render_template('500.html', reference_id=str(uuid.uuid4())), 500
