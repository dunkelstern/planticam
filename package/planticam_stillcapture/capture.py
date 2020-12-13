import os
import configparser
from socket import gethostname
from datetime import datetime
from time import sleep

import requests
import exifread
from picamera import PiCamera


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
	aspect_ratio = cam.resolution[1] / cam.resolution[0]
	cam.exposure_mode = settings['exposure_mode'] if 'exposure_mode' in settings else 'auto'
	cam.awb_mode = settings['awb_mode'] if 'awb_mode' in settings else 'auto'
	# TODO: other camera settings

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
		if 'JPEGthumbnail' in tags:
			with open('/tmp/capture_thumb.jpg', 'wb') as o:
				o.write(tags['JPEGThumbnail'])


def main():
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

		capture_image(cam, config['image_settings'])
		upload_file(config, start)

		# calculate the time we took to process and upload
		end = datetime.now()
		delta = end - start

		sleep_time = float(config['timelapse']['delay']) - delta.total_seconds()
		if sleep_time > 0:
			sleep(sleep_time)

if __name__ == '__main__':
	main()