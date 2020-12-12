from flask import Blueprint, render_template

about = Blueprint('about', __name__, template_folder='templates')


@about.route('/about', methods=['GET'])
def about_view():
    return render_template('about.html.j2')
