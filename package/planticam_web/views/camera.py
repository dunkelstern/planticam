from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from util.config import get_config
from util.save import save_config

camera = Blueprint('camera', __name__, template_folder='templates')


@camera.route('/camera', methods=['GET', 'POST'])
@login_required
def camera_view():
    settings = get_config()['image_settings']
    if request.method == 'GET':
        return render_template(
            'camera.html.j2',
            settings=settings
        )
    if request.method == 'POST':
        # resolution/rotation form
        if 'rotation' in request.form:
            settings['resolution_x'] = request.form['resolution_x']
            settings['resolution_y'] = request.form['resolution_y']
            settings['rotation'] = request.form['rotation']

            save_config(get_config())

        # exposure form
        if 'iso' in request.form:
            settings['iso'] = request.form['iso']
            settings['exposure_mode'] = request.form['exposure_mode']
            settings['exposure_compensation'] = request.form['exposure_compensation']
            settings['metering_mode'] = request.form['metering_mode']
            settings['drc'] = request.form['drc']

            save_config(get_config())

        # color form
        if 'awb_mode' in request.form:
            settings['awb_mode'] = request.form['awb_mode']
            settings['awb_gain_red'] = request.form['awb_gain_red']
            settings['awb_gain_blue'] = request.form['awb_gain_blue']
            settings['brightness'] = request.form['brightness']
            settings['contrast'] = request.form['contrast']
            settings['saturation'] = request.form['saturation']

            save_config(get_config())

        # postprocessing form
        if 'sharpness' in request.form:
            settings['sharpness'] = request.form['sharpness']
            settings['denoise'] = request.form['denoise']

            save_config(get_config())

        return redirect(url_for('camera.camera_view'))
