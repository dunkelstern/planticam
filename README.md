## Planticam, open source timelapse and streaming camera for Raspberry Pi Zero W

This firmware transforms your Raspberry Pi Zero W to a timelapse or RTMP streaming camera
using one of the many Raspberry Pi CSI compatible cameras.

The idea is to have a stable maintenance free appliance that will not crash and burn if
it looses power (for example because it is turned on and off by a timer switch)

## Features

- Simple setup via config file on boot partition or Webinterface on USB Gadget Ethernet
- Automatic image capture in timelapse mode
- Image upload to storage server, no local storage
- RTMP video streaming (WIP)
- Audio recording (WIP, only if hardware is available)
- 3D printed case AMF and FreeCAD files

## Todo

- Most image settings (brightness, contrast, exposure_compensation, iso, meter_mode, rotation)
- RTMP video streaming
- Make video and timelapse modes cooperate
- Audio recording
- Web-interface
- Add sensor readouts on GPIO header to be added as overlay onto the image or stored in exif metadata
- Add sensor plugin interface to allow the user to add sensor readout plugins to the boot partition
- Screenshots and photo of the finished device

## What you need

- Raspberry Pi 0 W.
- Pi 0 Camera Ribbon (for "normal" sized Raspberry Pi cameras like the HQ camera)
- Raspberry Pi Camera or Raspberry Pi High-Quality Camera (or one on a flex cable directly meant for the Pi Zero)
- A compatible lens if you use the HQ Camera sensor.
- Micro SD card
- Some sort of a case for the electronics (either a Raspi Zero case with camera hole or use the
  3D printer ready AMF files in the `case` subdir)
- The camera firmware image from the release page

## How to use

1. Connect the camera to the Pi Zero W
2. Put the electronics into the case (store bought or 3D Printed)
3. Flash the image from the release page onto the SD card (I recommend [Etcher](https://www.balena.io/etcher/) for this)
4. Connect your Pi to a Computer using the `OTG` (middle) Port, not the power port
5. Wait for it to boot, a new network connection will become available once it has booted
6. Open a browser and navigate to http://10.0.77.1/
7. Follow the setup instructions on the website

## How it works

When connected to power the Pi boots the image from the SD-Card, this image is special as it is not
the usual Raspberry Pi OS or even Ubuntu. This image has been build with [Buildroot](https://buildroot.org/) and
compressed into a read-only `squashfs` file system.

On boot the USB Ethernet Gadget mode is activated and an instance of `dnsmasq` is providing DHCP services
on that interface. When a computer connects to it, it sees a USB network card and usually runs a DHCP client
on that interface. It will get an IP address in the Range `10.0.77.50-150` while the Pi has `10.0.77.1`.

On the Pi we have the following running services:

- Ethernet Gadget (which just sets some `configfs` settings to activate Ethernet mode)
- `dnsmasq` to provide DHCP to the connected computer (if one is connected)
- `ntpd` to synchronize the clock over the network as the Pi has no realtime clock
- `sshd` to be able to connect, debug and monitor the device
- `getty` on the Pi's UART on the GPIO header which provides a serial console at 115200 baud
- `wpa_supplicant` to connect to Wifi (for more info read on)
- `planticam_web` which is the `flask` based webinterface for setting up the device
- `planticam_still` which is a relatively simple python script that captures still images for timelapses

## How to configure (the UI way)

1. Connect the Pi with the data port (not the power one) to a computer
2. Wait a minute for it to boot
3. Open a browser and navigate to http://10.0.77.1

The default username is `admin` and the password is `en3Eyied0mae`

## How to configure (the manual way)

1. Insert the flashed SD-card into a card reader/your computer
2. Open the SD-card (on Windows it will show up as a drive, on OSX it should show
  up in finder and on Linux it depends on your environment, if it does not show up
  automatically, mount the first partition, the `vfat` one)
3. Open `wpa_supplicant.conf` and enter your WiFi name and password instead of `default` and `password`.
  Make sure to save with linux/unix line endings (LF only, nor CR LF which is default on Windows)
4. Open `planticam.conf` in your editor and see below for a description of the options (if the names are not
  enough)

## How to configure (the cryptographically secure way)

See "The manual way" above first.

### SSH Keys

The ssh host keys of this image are embedded and will not be re-generated as the filesystem is strictly
read-only, however you can replace them as they are stored on the `vfat` partition of the SD-card in
the folder `ssh-keys`. It is strongly recommended to either build the complete image with `buildroot` yourself
or at least change the keys if it is remotely possible the device will be accessed over the internet.

To re-generate the keys run the following commands and replace the files on the SD-card with the newly generated
ones:

```bash
ssh-keygen -t rsa -f ssh_host_rsa_key -C '' -N ''
ssh-keygen -t dsa -f ssh_host_dsa_key -C '' -N ''
ssh-keygen -t ecdsa -f ssh_host_ecdsa_key -C '' -N ''
ssh-keygen -t ed25519 -f ssh_host_ed25519_key -C '' -N ''
```

On the boot partition you will find another SSH key, the client key, directly in the root folder.
To re-generate this one run the following command and replace the files on the card (`id_ed25519` and `id_ed25519.pub`):

```bash
ssh-keygen -t ed25519 -f id_ed25519 -C 'planticam' -N ''
```

### Random seed

As this is an embedded system with absolutely no external hardware attached to gather entropy from, we have
to help the Pi (else every cryptographic algorithm that uses random numbers will hang on boot until enough
entropy has been gathered.)

At build time the scripts generate a random seed. It is not strictly necessary to exchange that seed but if
you want to be sure nobody can guess the internal state of your device you may exchange the seed if you want.

The seed is stored as a kernel-boot-parameter in `cmdline.txt` in the parameter `systemd.random_seed`.
To generate a `base64` string to use as a seed run the following:

```bash
head -c 250 /dev/urandom |base64 -w0 -
```

This takes 250 bytes of random data from `/dev/urandom`, `base64` encodes it and prints it to the terminal.

## Debugging

also known as: "It does not work, what's wrong!"

There are 3 methods of accessing the device, ordered from "it mostly works" to "wtf is wrong":

1. If it seems to connect to Wifi, try SSH as root to `planticam.local` if you have zeroconf
  (also known as bonjour) running.
2. If you get something like `ssh: Could not resolve hostname planticam.local: Name or service not known`
  either zeroconf is not working correctly or the device did not connect to Wifi, consult your router to
  find the appropriate IP address to use with SSH.
3. If Wifi absolutely won't connect, see if your router advertises its SSID on a channel that is probably not
  supported by the firmware (for example: You can use 2.4GHz channel 13 in Germany, but the firmware has no
  region set so it will not scan on that channel as it is forbidden to use in other parts of the world)
4. If your router is fine, but it will not connect, try connecting the Pi to a computer via the USB data port and try
  SSH to `10.0.77.1` as root user.
5. If even the internal USB gadget ethernet won't work try using a serial console on the GPIO header. You will need
  a USB to serial converter (or something similar) that can be used on 3.3V. **Warning:** The Pi UART is not 5V
  compliant, you will destroy the PI if you're using a 5V device here! The Baud-rate is 115200,
  8 bits, no parity, 1 stop bit (also known as 115200 8N1)

For console login use the `root` user and the password `Tu1boo4bee5i`

You will not have any writable filesystem by default. You can re-mount the `vfat` partition that is mounted as `/boot`
if you just want to correct a setting though (only `vi` available on the Pi though, `i` to switch to edit mode,
ESC `:wq` to exit ;) ):

```bash
mount -o remount,rw /boot
```

Be sure to re-mount read only before disconnecting power to avoid crashed SD-cards.

To debug what went wrong, usually you can look at the following commands:

- Kernel log: `dmesg`, shows any hardware failures
- Journal: `journalctl -xe`, shows any output `systemd` or any of the running services generate, including
  python stacktraces of any service

## Building

1. Create a working directory: `mkdir planticam`
2. Checkout this repository: `git clone https://github.com/dunkelstern/planticam.git`
3. Download a copy of buildroot: `wget https://buildroot.org/downloads/buildroot-2020.11.tar.gz`
4. Unpack buildroot: `tar xvzf buildroot-2020.11.tar.gz`
5. Link the buildroot directory to `buildroot` (without version number): `ln -sf buildroot-2020.11 buildroot`
6. Switch to the build directory: `cd planticam`
7. Run the build script: `./build-planticam.sh`
8. Go grab a coffee, this takes some time as the complete crosscompiling toolchain is downloaded and
  build before re-building the complete system in the image from source. (Takes about an hour on my Lenovo Yoga Slim)
9. Go grab the image from `output/planticam/images/sdcard.img`

If you want to make changes to the planticam sources you can re-run the build process with the `clean` parameter
to clean out the build packages before re-building: `./build-planticam.sh clean`, this will only clean out neccessary
files, a rebuild should be done in about a minute usually.

While building, the scripts generate SSH keys for the ssh daemon as well as a client ssh key, those will only be rebuilt
if you remove the `output/planticam/images` folder, so you may experiment with new images without constantly removing
the keys from your `known_hosts` or replacing the public key on your image destination server.

To put the image on an SD-card you can either use etcher or any other image writer. I prefer to do it with `dd`:

```bash
dd if=output/planticam/images/sdcard.img of=/dev/sdX bs=1M oflag=sync status=progress
```

Replace `/dev/sdX` with the appropriate device name of your SD-card, make sure you may access the device file (either
put yourself in the appropriate group for your Linux Distro or run the command as root). The `oflag=sync` skips the
write cache of the SD-card so you can remove it immediately after the command finishes, the `status=progress` displays
write progress, which is good as the `dd` command may appear to hang while the system is copying data.

## planticam.conf

Example:

```ini
[timelapse]
enabled=1
delay=10
upload_cmd=scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -q -i /boot/id_ed25519 {input_file} user@host:/path/to/{output_file}
resolution_x=2592
resolution_y=1944
exposure_mode=auto
awb_mode=auto

[stream]
enabled=0
bitrate_kbps=3000
framerate=30
resolution_x=1920
resolution_y=1080
exposure_mode=auto
awb_mode=auto
destination=rtmp://example.com/live/planticam
```

### \[timelapse\]

- `enabled`: boolean value, enable the timelapse mode
- `delay`: delay in seconds between photos
- `upload_cmd`: (optional) command to run to upload the image somewhere, the example command uploads to a SSH server
  which has the `id_ed25519.pub` key in their `authorized_keys`-file. Has 2 placeholders: `{input_file}` the source
  file and `{output_file}` the output filename (usually `planticam-YYYY-MM-DD_HH-MM-SS.jpg`)
- `post_url`: (optional) URL to upload the image to, it will send a `HTTP POST`-request with `Content-Type: image/jpeg`
  and the JPEG binary as is in the body

### \[stream\]

- `enabled`: boolean value, enable the video mode. Be aware that video streaming mode overrides the image resolution of
  timelapse mode if both are enabled
- `bitrate_kbps`: Video bitrate
- `framerate`: Video framerate, see [picamera documentation](https://picamera.readthedocs.io/en/release-1.12/fov.html)
  for hardware limitations
- `destination`: RTMP server URL to stream the video to
- `include_audio`: boolean value, if you have a sound device on the Pi you can enable the audio track with this setting

### \[image_settings\]

- `resolution_x` and `resolution_y`: Image resolution, see
  [picamera documentation](https://picamera.readthedocs.io/en/release-1.12/fov.html) for explanation what the cameras
  can do
- `rotation`: (optional) Rotates the image in 90 degree increments
- `iso`: (optional) ISO to use, defaults to `auto` (one of `auto`, 100, 200, 320, 400, 500, 640, 800)
- `exposure_mode`: (optional) Exposure mode to use (one of `off`, `auto`, `night`, `nightpreview`, `backlight`,
  `spotlight`, `sports`, `snow`, `beach`, `verylong`, `fixedfps`, `antishake` or `fireworks`)
- `exposure_compensation`: (optional) Adjusts the camera’s exposure compensation level. Each increment represents
  1/6th of a stop. Range is -25 to 25, defaults to 0
- `meter_mode`: (optional) Exposure metering mode, defaults to `average` (one of `average`, `spot`, `backlit` or
  `matrix`)
- `awb_mode`: (optional) White-balance mode to use (one of `off`, `auto`, `sunlight`, `cloudy`, `shade`, `tungsten`,
  `fluorescent`, `incandescent`, `flash` or `horizon`)
- `brightness`: (optional) Brightness from 0-100, defaults to 50
- `contrast`: (optional) Contrast from -100-100, defaults to 0


## Credits

- [Buildroot](https://buildroot.org/) the build system
- [ShowMeWebcam](https://github.com/showmewebcam/showmewebcam), converts the Raspi Zero into a USB webcam,
  they gave me the idea
