from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from util.config import get_config

camera = Blueprint('camera', __name__, template_folder='templates')


@camera.route('/camera', methods=['GET', 'POST'])
@login_required
def camera_view():
    if request.method == 'GET':
        return render_template('camera.html.j2', config=get_config)
    if request.method == 'POST':
        # TODO: save form
        return redirect(url_for('camera.camera_view'))
