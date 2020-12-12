from flask import Blueprint, request, redirect, url_for, render_template, g
from flask_login import login_user, logout_user, login_required

from util.user import User, authenticate
from util.config import get_config

login = Blueprint('login', __name__, template_folder='templates')

@login.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        return render_template('login.html.j2')
    if request.method == 'POST':
        user = authenticate(request.form['username'], request.form['password'])
        if isinstance(user, User):
            login_user(user, remember=True)
            return redirect(url_for('index'))
    return redirect(url_for('login.login_view'))

@login.route('/logout', methods=['POST'])
@login_required
def logout_view():
    logout_user()
    return redirect(url_for('login.login_view'))
