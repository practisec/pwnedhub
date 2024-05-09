from flask import Blueprint, request, render_template, abort
from pwnedconfig.models import Config
from pwnedconfig import db

blp = Blueprint('config', __name__, url_prefix='/config')

@blp.route('/', methods=['GET', 'POST'])
def index():
    if Config.get_value('CTF_MODE'):
        abort(404)
    if request.method == 'POST':
        options = [
            'CSRF_PROTECT',
            'BEARER_AUTH_ENABLE',
            'CORS_RESTRICT',
            'OIDC_ENABLE',
            'OSCI_PROTECT',
            'SQLI_PROTECT',
            'CTF_MODE',
            'SSO_ENABLE',
            'JWT_VERIFY',
            'JWT_ENCRYPT',
            'OOB_RESET_ENABLE',
        ]
        for option in options:
            Config.get_by_name(option.upper()).value = request.form.get(option.lower()) == 'on'
        db.session.commit()
    return render_template('config.html')
