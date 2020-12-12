from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from util.config import get_config

video = Blueprint('video', __name__, template_folder='templates')


@video.route('/video', methods=['GET', 'POST'])
@login_required
def video_view():
    if request.method == 'GET':
        return render_template('video.html.j2', config=get_config)
    if request.method == 'POST':
        # TODO: save form
        return redirect(url_for('video.video_view'))
