import os
from datetime import datetime

from flask import Flask, redirect, url_for, request, send_file, render_template
from flask_login import LoginManager, login_required, current_user

from util.user import User, Anonymous
from util.config import get_config, reload_config
from views import login, settings, about, camera, timelapse, video


login_manager = LoginManager()
app = Flask(__name__)

app.register_blueprint(login)
app.register_blueprint(settings)
app.register_blueprint(about)
app.register_blueprint(camera)
app.register_blueprint(timelapse)
app.register_blueprint(video)
login_manager.init_app(app)

with app.app_context():
    app.secret_key = get_config()['web']['secret_key']


@login_manager.user_loader
def load_user(user_id):
    # reload config in case the user info changed
    reload_config()
    return User()


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login.login_view'))


@app.context_processor
def inject_systime():
    return dict(systime=datetime.now())


@app.context_processor
def inject_navigation():
    return dict(nav=request.path)


@app.context_processor
def inject_last_capture():
    if os.path.exists('/tmp/capture_thumb.jpg'):
        mtime = datetime.fromtimestamp(os.path.getmtime('/tmp/capture_thumb.jpg'))
    else:
        mtime = None

    return dict(
        last_capture_date=mtime
    )

@app.route('/')
@login_required
def index():
    return render_template('index.html.j2')


@app.route('/current_image.jpg')
def current_image():
    if isinstance(current_user, Anonymous):
        img = open('static/img/placeholder.jpg', 'rb')
    else:
        if os.path.exists('/tmp/capture_thumb.jpg'):
            img = open('/tmp/capture_thumb.jpg', 'rb')
        else:
            img = open('static/img/placeholder.jpg', 'rb')
    return send_file(img, mimetype='image/jpeg')


@app.route('/last-capture-time')
def last_capture_time():
    if os.path.exists('/tmp/capture_thumb.jpg'):
        return str(os.path.getmtime('/tmp/capture_thumb.jpg'))
    return '0'


@app.route('/capture-now', methods=["POST"])
def capture_now():
    os.system('systemctl reload planticam_still')
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

