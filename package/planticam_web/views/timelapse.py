import os
from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from util.config import get_config
from util.save import save_config

timelapse = Blueprint('timelapse', __name__, template_folder='templates')


@timelapse.route('/timelapse', methods=['GET', 'POST'])
@login_required
def timelapse_view():
    settings = get_config()['timelapse']
    if request.method == 'GET':
        return render_template(
            'timelapse.html.j2',
            settings=settings,
            weekday_enable=settings['weekday_enable'].split(','),
            weekday_from=settings['weekday_from'].split(','),
            weekday_to=settings['weekday_to'].split(',')
        )
    if request.method == 'POST':
        # generic form
        if 'enable_timelapse' in request.form:
            settings['enable'] = request.form['enable_timelapse']
            settings['delay'] = request.form['delay']

            save_config(get_config())

        # destination form
        if 'upload_mode' in request.form:
            settings['upload_mode'] = request.form['upload_mode']
            settings['upload_server'] = request.form['upload_server']
            settings['upload_path'] = request.form['upload_path']

            settings['upload_auth_user'] = request.form['upload_username']
            settings['upload_auth_password'] = request.form['upload_password']
            settings['upload_form_field'] = request.form['upload_form_field']

            if settings['upload_mode'] == 'sftp':
                settings['upload_cmd'] = 'SSHPASS={password} sftp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -q -i /boot/id_ed25519 {{input_file}} {user}@{host}:{path}/{{output_file}}'.format(
                    user=request.form['upload_username'],
                    host=request.form['upload_server'],
                    path=request.form['upload_path'],
                    password=request.form['upload_password']
                )
            if settings['upload_mode'] == 'scp':
                settings['upload_cmd'] = 'SSHPASS={password} scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -q -i /boot/id_ed25519 {{input_file}} {user}@{host}:{path}/{{output_file}}'.format(
                    user=request.form['upload_username'],
                    host=request.form['upload_server'],
                    path=request.form['upload_path'],
                    password=request.form['upload_password']
                )
            if settings['upload_mode'] in ['post', 'form']:
                settings['upload_url'] = "{server}{path}".format(
                    server=request.form['upload_server'],
                    path=request.form['upload_path'],
                )
            if settings['upload_mode'] == 'local':
                # check if we have a data partition on the sd card
                os.system('/usr/bin/umount /data')
                ret = os.system('/usr/bin/mount /data')
                if ret != 0:
                    # partition does not exist, try to create one
                    # /dev/mmcblk0p3
                    ret = os.system('/usr/bin/make_data_partition.sh')
                    ret = os.system('/usr/bin/mount /data')

            save_config(get_config())

        # schedule form
        if 'weekday_1_from' in request.form:
            if 'weekday_enable' not in settings:
                settings['weekday_enable'] = 'off,off,off,off,off,off,off'
            if 'weekday_from' not in settings:
                settings['weekday_from'] = '00:00,00:00,00:00,00:00,00:00,00:00,00:00,'
            if 'weekday_to' not in settings:
                settings['weekday_to'] = '23:59,23:59,23:59,23:59,23:59,23:59,23:59,'

            weekday_enable = settings['weekday_enable'].split(',')
            weekday_from = settings['weekday_from'].split(',')
            weekday_to = settings['weekday_to'].split(',')
            for i in range(1, 8):
                setting = 'weekday_{}_enable'.format(i)
                if setting not in request.form:
                    weekday_enable[i-1] = 'off'
                else:
                    weekday_enable[i-1] = request.form[setting]
                setting = 'weekday_{}_from'.format(i)
                weekday_from[i-1] = request.form[setting]
                setting = 'weekday_{}_to'.format(i)
                weekday_to[i-1] = request.form[setting]

            settings['weekday_enable'] = ",".join(weekday_enable)
            settings['weekday_from'] = ",".join(weekday_from)
            settings['weekday_to'] = ",".join(weekday_to)
            save_config(get_config())

        return redirect(url_for('timelapse.timelapse_view'))
