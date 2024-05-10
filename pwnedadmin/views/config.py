from flask import Blueprint, request, render_template, abort, redirect, url_for
from pwnedadmin import db
from pwnedadmin.constants import ConfigTypes
from pwnedadmin.models import Config

blp = Blueprint('config', __name__, url_prefix='/config')

@blp.route('/', methods=['GET', 'POST'])
def index():
    if Config.get_value('CTF_MODE'):
        abort(404)
    configs = Config.query.all()
    if request.method == 'POST':
        for config in configs:
            config.value = request.form.get(config.name.lower()) == 'on'
        db.session.commit()
        return redirect(url_for('config.index'))
    return render_template('config.html', configs=configs, config_types=ConfigTypes().serialized)
