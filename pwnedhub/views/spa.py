from flask import Blueprint, render_template
from pwnedhub.decorators import login_required

spa = Blueprint('spa', __name__, url_prefix='/spa')

# no XSS to better support other demos
@spa.route('/<string:component>')
@login_required
def messages(component):
    return render_template('spa/component.html', component=component)
