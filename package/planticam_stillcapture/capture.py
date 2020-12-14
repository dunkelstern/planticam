import os
import signal
import configparser
from socket import gethostname
from datetime import datetime
from time import sleep

import requests
import exifread
from picamera import PiCamera

reload_service = False


def handler(signum, frame):
	global reload_service

	if signum == signal.SIGUSR1:
		print('Reload signal received!')
		reload_service = True


def upload_file(config, date):
	filename = "{host}-{date:%Y-%m-%d_%H-%M-%S}.jpg".format(
		host=gethostname(),
		date=date
	)

	if 'upload_cmd' in config['timelapse']:
		cmd = config['timelapse']['upload_cmd']
		cmd = cmd.format(
			input_file='/tmp/capture.jpg',
			output_file=filename
		)
		os.system(cmd)

	if 'post_url' in config['timelapse']:
		url = config['timelapse']['post_url']
		with open('/tmp/capture.jpg', 'rb') as fp:
			data=fp.read()
		requests.post(
			url=url,
			data=data,
			headers={'Content-Type': 'image/jpeg'}
		)


def capture_image(cam, settings):
	cam.resolution = (int(settings['resolution_x']), int(settings['resolution_y']))
	cam.rotation = int(settings.get('rotation', '0'))
	aspect_ratio = cam.resolution[1] / cam.resolution[0]
	cam.exposure_mode = settings.get('exposure_mode', 'auto')
	cam.exposure_compensation = int(settings.get('exposure_compensation', '0'))
	cam.awb_mode = settings.get('awb_mode', 'auto')
	iso = settings.get('iso', 'auto')
	if iso == 'auto':
		iso = '0'
	cam.iso = int(iso)
	cam.metering_mode = settings.get('metering_mode', 'average')
	cam.drc_strength = settings.get('drc', 'off')
	if cam.awb_mode == 'off':
		cam.awb_gains = (float(settings.get('awb_gain_red', '0.9')), float(settings.get('awb_gain_blue', '0.9')))
	cam.brightness = int(settings.get('brightness', '50'))
	cam.contrast = int(settings.get('contrast', '0'))
	cam.saturation = int(settings.get('saturation', '0'))
	cam.image_denoise = settings.get('denoise', 'on') in ['1', 'yes', 'on', 'true']
	cam.sharpness = int(settings.get('sharpness', '0'))

	cam.framerate = 1
	try:
		os.unlink('/tmp/capture.jpg')
	except FileNotFoundError:
		pass
	cam.capture('/tmp/capture.jpg', thumbnail=(300, int(300 * aspect_ratio), 60))
	cam.stop_preview()

	# now extract the thumbnail into it's own file
	with open('/tmp/capture.jpg', 'rb') as fp:
		tags = exifread.process_file(fp, stop_tag='JPEGThumbnail')
		if 'JPEGThumbnail' in tags:
			with open('/tmp/capture_thumb.jpg', 'wb') as o:
				o.write(tags['JPEGThumbnail'])


def main():
	global reload_service

	config = configparser.ConfigParser()

	cam = None

	while True:
		config.read('/boot/planticam.conf')
		if config['timelapse']['enable'] not in ['1', 'yes', 'on', 'true'] and not reload_service is True:
			if cam is not None:
				cam.close()
				cam = None
			for i in range(0, 60):
				sleep(1)
				if reload_service is True:
					break
			continue

		if cam is None:
			cam = PiCamera()

		reload_service = False

		start = datetime.now()

		capture_image(cam, config['image_settings'])
		upload_file(config, start)

		# calculate the time we took to process and upload
		end = datetime.now()
		delta = end - start

		sleep_time = float(config['timelapse']['delay']) - delta.total_seconds()
		while sleep_time > 1:
			sleep(1)
			sleep_time -= 1
			if reload_service is True:
				sleep_time = 0
		if sleep_time > 0:
			sleep(sleep_time)

if __name__ == '__main__':
	signal.signal(signal.SIGUSR1, handler)
	main()
