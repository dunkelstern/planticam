from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from util.config import get_config

timelapse = Blueprint('timelapse', __name__, template_folder='templates')


@timelapse.route('/timelapse', methods=['GET', 'POST'])
@login_required
def timelapse_view():
    if request.method == 'GET':
        return render_template('timelapse.html.j2', config=get_config)
    if request.method == 'POST':
        # TODO: save form
        return redirect(url_for('timelapse.timelapse_view'))
