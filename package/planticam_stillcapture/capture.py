import os
import configparser
from socket import gethostname
from datetime import datetime
from time import sleep

import requests
from picamera import PiCamera

config = configparser.ConfigParser()

cam = None

while True:
	config.read('/boot/planticam.conf')
	if config['timelapse']['enabled'] not in ['1', 'yes', 'on', 'true']:
		if cam is not None:
			cam.close()
			cam = None
		sleep(60)
		continue

	if cam is None:
		cam = PiCamera()

	start = datetime.now()

	cam.resolution = (int(config['timelapse']['resolution_x']), int(config['timelapse']['resolution_y']))
	cam.exposure_mode = config['timelapse']['exposure_mode']
	cam.awb_mode = config['timelapse']['awb_mode']
	cam.framerate = 1
	try:
		os.unlink('/tmp/capture.jpg')
	except FileNotFoundError:
		pass
	cam.capture('/tmp/capture.jpg')
	cam.stop_preview()

	filename = "{host}-{date:%Y-%m-%d_%H-%M-%S}.jpg".format(
		host=gethostname(),
		date=start
	)

	if 'upload_cmd' in config['timelapse']:
		cmd = config['timelapse']['upload_cmd']
		cmd = cmd.format(
			input_file='/tmp/capture.jpg',
			output_file=filename
		)
		os.system(cmd)
	end = datetime.now()
	delta = end - start

	if 'post_url' in config['timelapse']:
		url = config['timelapse']['post_url']
		with open('/tmp/capture.jpg', 'rb') as fp:
			data=fp.read()
		requests.post(
			url=url,
			data=data,
			headers={'Content-Type': 'image/jpeg'}
		)

	sleep_time = float(config['timelapse']['delay']) - delta.total_seconds()
	if sleep_time > 0:
		sleep(sleep_time)

