from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from util.config import get_config

settings = Blueprint('settings', __name__, template_folder='templates')


@settings.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_view():
    if request.method == 'GET':
        return render_template('settings.html.j2', config=get_config)
    if request.method == 'POST':
        # TODO: save form
        return redirect(url_for('settings.settings_view'))
