from typing import Union

import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from hashlib import pbkdf2_hmac
from configparser import ConfigParser

from flask_login import UserMixin
from flask_login.mixins import AnonymousUserMixin

from .config import get_config
from .save import save_config

PBKDF2_ITERATIONS = 50000
PBKDF2_ALGO = 'sha256'


class Anonymous(AnonymousUserMixin):
    pass


class User(UserMixin):

    def get_id(self) -> str:
        return self.username

    @property
    def username(self) -> str:
        config = get_config()
        return config['web']['username']

    @username.setter
    def username(self, value) -> None:
        config = get_config()
        config['web']['username'] = value

    def save(self):
        config = get_config()
        save_config(config)

    def update_password(self, new_password: str) -> None:
        salt = urlsafe_b64encode(os.urandom(16))
        new_hash = urlsafe_b64encode(
            pbkdf2_hmac(
                PBKDF2_ALGO,
                new_password.encode('utf-8'),
                salt,
                PBKDF2_ITERATIONS
            )
        ).decode('utf-8')

        config = get_config()
        config['web']['password'] = '{algo}:{iterations}:{salt}:{hash}'.format(
            algo=PBKDF2_ALGO,
            salt=salt.decode('utf-8'),
            iterations=PBKDF2_ITERATIONS,
            hash=new_hash
        )


def authenticate(username: str, password: str) -> Union[User, Anonymous]:
    """
    Authenticate a user with username and password

    :param config: loaded configuration from config file
    :param username: username to authenticate
    :param password: password to use for authentication
    :returns: ``User`` instance if username and password match, ``Anonymous`` instance if they don't
    """
    config = get_config()

    if config['web']['username'] == username:
        # check password
        algo, iterations, salt, stored_hash = config['web']['password'].split(':')
        password_hash = urlsafe_b64encode(
            pbkdf2_hmac(
                algo,
                password.encode('utf-8'),
                salt.encode('utf-8'),
                int(iterations)
            )
        ).decode('utf-8')

        # hashes match, return user object
        if stored_hash == password_hash:
            return User()

    return Anonymous()