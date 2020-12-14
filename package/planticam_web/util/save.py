import os
from contextlib import contextmanager
from configparser import ConfigParser

CONFIG_FILE = '/boot/planticam.conf'

@contextmanager
def writeable_config():
    os.system('/usr/bin/mount -o remount,rw /boot')
    try:
        yield
    finally:
        os.system('/usr/bin/mount -o remount,ro /boot')


def save_config(config: ConfigParser):
    with writeable_config():
        with open(CONFIG_FILE + '.new', 'w') as fp:
            config.write(fp)
        os.unlink(CONFIG_FILE)
        os.rename(CONFIG_FILE + '.new', CONFIG_FILE)