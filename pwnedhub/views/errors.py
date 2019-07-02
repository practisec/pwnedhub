from flask import Blueprint, request, render_template, render_template_string
import traceback

errors = Blueprint('errors', __name__)

# error handling controllers

@errors.app_errorhandler(404)
def not_found(e):
    template = '''{% extends "layout.html" %}
{% block body %}
<div class="flex-grow error center-content">
    <h1>Oops! That page doesn't exist.</h1>
    <h3>'''+request.url+'''</h3>
</div>
{% endblock %}'''
    return render_template_string(template), 404

@errors.app_errorhandler(500)
def internal_server_error(e):
    message = traceback.format_exc()
    return render_template('500.html', message=message), 500
