from flask import Blueprint, render_template

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('spa.html')
