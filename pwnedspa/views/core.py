from flask import Blueprint, render_template

blp = Blueprint('core', __name__)

@blp.route('/')
def index():
    return render_template('spa.html')
