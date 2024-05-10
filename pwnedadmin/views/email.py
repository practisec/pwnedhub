from flask import Blueprint, request, render_template, redirect, url_for
from pwnedadmin import db
from pwnedadmin.models import Email

blp = Blueprint('email', __name__, url_prefix='/inbox')

@blp.route('/', methods=['GET', 'POST'])
def index():
    if user := request.args.get('user'):
        emails = Email.get_by_receiver(user)
    else:
        emails = Email.get_unrestricted()
    return render_template('emails.html', emails=emails.order_by(Email.created.desc()).all())

@blp.route('/empty')
def empty():
    emails = Email.query.delete()
    db.session.commit()
    return redirect(url_for('email.index'))
