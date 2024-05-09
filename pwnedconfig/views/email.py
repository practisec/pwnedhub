from flask import Blueprint, render_template
from pwnedconfig.models import Email

blp = Blueprint('email', __name__, url_prefix='/inbox')

@blp.route('/', methods=['GET', 'POST'])
def index():
    emails = Email.query.order_by(Email.created.desc()).all()
    return render_template('emails.html', emails=emails)
