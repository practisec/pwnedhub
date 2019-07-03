from flask import Blueprint, request, render_template, render_template_string, jsonify
import traceback

errors = Blueprint('errors', __name__)

CONTENT_TYPE = 'application/json'

# error handling controllers

@errors.app_errorhandler(400)
def bad_request(e):
    if request.content_type == CONTENT_TYPE:
        response = jsonify(status=400, message=e.description), 400
    else:
        return e

@errors.app_errorhandler(403)
def forbidden(e):
    if request.content_type == CONTENT_TYPE:
        return jsonify(status=403, message="Resource forbidden."), 403
    else:
        return e

@errors.app_errorhandler(404)
def not_found(e):
    if request.content_type == CONTENT_TYPE:
        return jsonify(status=404, message="Resource not found."), 404
    else:
        template = '''{% extends "layout.html" %}
{% block body %}
<div class="flex-grow error center-content">
    <h1>Oops! That page doesn't exist.</h1>
    <h3>'''+request.url+'''</h3>
</div>
{% endblock %}'''
        return render_template_string(template), 404

@errors.app_errorhandler(405)
def method_not_allowed(e):
    if request.content_type == CONTENT_TYPE:
        return jsonify(status=405, message="Method not allowed."), 405
    else:
        return e

@errors.app_errorhandler(500)
def internal_server_error(e):
    message = traceback.format_exc()
    if request.content_type == CONTENT_TYPE:
        return jsonify(status=500, message=message), 500
    else:
        return render_template('500.html', message=message), 500
