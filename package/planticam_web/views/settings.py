import re
from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required, current_user

from util.config import get_config
from util.save import writeable_config

settings = Blueprint('settings', __name__, template_folder='templates')

ssid_regex = re.compile(r'^\s*ssid\s*=\s*"(.*)"$')
psk_regex = re.compile(r'^\s*psk\s*=\s*"(.*)"$')


def parse_wpa_supplicant_conf(filename):
    wifi_name = None
    wifi_password = None
    with open(filename, 'r') as fp:
        for line in fp:
            match = ssid_regex.match(line)
            if match:
                wifi_name = match.groups()[0].replace('\"', '"')
                continue
            match = psk_regex.match(line)
            if match:
                wifi_password = match.groups()[0].replace('\"', '"')
                continue
    return wifi_name, wifi_password


@settings.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_view():
    if request.method == 'GET':
        wifi_name, wifi_password = parse_wpa_supplicant_conf('/boot/wpa_supplicant.conf')
        with open('/boot/id_ed25519.pub', 'r') as fp:
            ssh_key = fp.read()
        return render_template(
            'settings.html.j2',
            config=get_config(),
            wifi_name=wifi_name,
            wifi_password=wifi_password,
            username=current_user.username,
            ssh_pub_key=ssh_key
        )
    if request.method == 'POST':
        # save wifi form
        if 'wifi_name' in request.form:
            wpa_config = render_template(
                'wpa_supplicant.conf.j2',
                wifi_name=request.form['wifi_name'].replace('"', '\\"'),
                wifi_password=request.form['wifi_password'].replace('"', '\\"')
            )
            with writeable_config():
                with open('/boot/wpa_supplicant.conf', 'w') as fp:
                    fp.write(wpa_config)
        # save username/password form
        if 'username' in request.form:
            current_user.username = request.form['username']
            current_user.update_password(request.form['password'])
            current_user.save()
        return redirect(url_for('settings.settings_view'))
