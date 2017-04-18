from configparser import ConfigParser
import os

DJANGO_PROPERTY_MODE = 'production'
if os.environ.get('DJANGO_PROPERTY_MODE'):
    DJANGO_PROPERTY_MODE = os.environ.get('DJANGO_PROPERTY_MODE')

DJANGO_PROPERTY_FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/properties/properties-' + DJANGO_PROPERTY_MODE + '.ini'
module_config = ConfigParser()
module_config.read(DJANGO_PROPERTY_FILE_PATH)


def get_db(name):
    return module_config.get('DATABASE', name)


def get(name):
    return module_config.get('DEFAULT', name)


def need_cache():
    return module_config.get('DEFAULT', 'NEED_CACHE') == 'True'

