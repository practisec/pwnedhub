from flask import Blueprint, render_template
from pwnedhub.decorators import login_required

spa = Blueprint('spa', __name__, url_prefix='/spa')

# no XSS to better support other demos
@spa.route('/')
@login_required
def default():
    return render_template('spa.html')
