import os
import sys
from os.path import abspath, join, dirname, expanduser
import logging.config

PROJECT_ROOT = abspath(dirname(__file__))

from tenyks.module_loader import make_module_from_file


class ConfigError(Exception):
    pass


class NotConfigured(Exception):
    pass


# taken from legit (https://github.com/kennethreitz/legit)
class Settings(object):
    _singleton = {}

    # attributes with defaults
    __attrs__ = tuple()

    def __init__(self, **kwargs):
        super(Settings, self).__init__()

        self.__dict__ = self._singleton

    def __call__(self, *args, **kwargs):
        # new instance of class to call
        r = self.__class__()

        # cache previous settings for __exit__
        r.__cache = self.__dict__.copy()
        map(self.__cache.setdefault, self.__attrs__)

        # set new settings
        self.__dict__.update(*args, **kwargs)

        return r

    def __enter__(self):
        pass

    def __exit__(self, *args):

        # restore cached copy
        self.__dict__.update(self.__cache.copy())
        del self.__cache

    def __getattribute__(self, key):
        if key in object.__getattribute__(self, '__attrs__'):
            try:
                return object.__getattribute__(self, key)
            except AttributeError:
                return None
        return object.__getattribute__(self, key)


settings = Settings()


def collect_settings(settings_path=None):
    intrl_settings = None
    if not settings_path:
        if len(sys.argv) > 1:
            intrl_settings = make_module_from_file('settings', sys.argv[1])
        else:
            path = join(expanduser('~'), '.config', 'tenyks', 'settings.py')
            if os.path.exists(path):
                intrl_settings = make_module_from_file('settings', path)
            else:
                path = join('etc', 'tenyks', 'settings.py')
                if os.path.exists(path):
                    intrl_settings = make_module_from_file('settings', path)
    else:
        if os.path.exists(settings_path):
            intrl_settings = make_module_from_file('settings', settings_path)

    if not intrl_settings:
        raise NotConfigured('You need to provide a settings.py')

    for sett in filter(lambda x: not x.startswith('__'), dir(intrl_settings)):
        setattr(settings, sett, getattr(intrl_settings, sett))

    if not hasattr(intrl_settings, 'WORKING_DIR'):
        WORKING_DIR = getattr(settings, 'WORKING_DIRECTORY_PATH',
                join(os.environ['HOME'], '.config', 'tenyks'))
        DATA_WORKING_DIR = join(WORKING_DIR, 'data')

        setattr(settings, 'WORKING_DIR', WORKING_DIR)
        setattr(settings, 'DATA_WORKING_DIR', DATA_WORKING_DIR)


    #BROADCAST_TO_SERVICES_CHANNEL = getattr(settings,
    #    'BROADCAST_TO_SERVICES_CHANNEL', 'tenyks.services.broadcast_to')

    #BROADCAST_TO_ROBOT_CHANNEL = getattr(settings,
    #    'BROADCAST_TO_ROBOT_CHANNEL', 'tenyks.robot.broadcast_to')

    #if hasattr(settings, 'MIDDLEWARE'):
    #    MIDDLEWARE = settings.MIDDLEWARE

logging.config.fileConfig(join(PROJECT_ROOT, 'logging_config.ini'))
