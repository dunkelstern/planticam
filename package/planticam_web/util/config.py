from flask import g
from configparser import ConfigParser

CONFIG_FILES = [
    'planticam.conf',
    '/boot/planticam.conf'
]


def get_config():
    if 'config' not in g:
        g.config = ConfigParser()
        for config_file in CONFIG_FILES:
            g.config.read(config_file)

    return g.config


def reload_config():
    if 'config' not in g:
        g.config = ConfigParser()

    for config_file in CONFIG_FILES:
        g.config.read(config_file)

    return g.config
