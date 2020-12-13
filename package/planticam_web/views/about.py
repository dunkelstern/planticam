from flask import Blueprint, render_template

about = Blueprint('about', __name__, template_folder='templates')


@about.route('/about', methods=['GET'])
def about_view():
    with open('static/about.html', 'rb') as fp:
        licenses = fp.read().decode('utf-8', errors='replace')
    return render_template('about.html.j2', license_html=licenses)
