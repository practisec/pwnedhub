from flask import Blueprint, render_template
from pwnedhub.decorators import login_required

spa = Blueprint('spa', __name__, url_prefix='/spa')

# no XSS to better support other demos
@spa.route('/messages')
@login_required
def messages():
    return render_template('spa/messages.html', spa=True)
