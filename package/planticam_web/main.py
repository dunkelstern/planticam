from datetime import datetime

from flask import Flask, redirect, url_for, request
from flask_login import LoginManager, login_required

from util.user import User
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
    return User(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login.login_view'))

@app.context_processor
def inject_navigation():
    return dict(nav=request.path)

@app.context_processor
def inject_last_capture():
    return dict(
        last_capture_date=datetime.now()
    )

@app.route('/')
@login_required
def index():
    return redirect(url_for('settings.settings_view'))


if __name__ == '__main__':
    app.run(debug=True)

