__author__ = 'mandar'

from tinydb import TinyDB

from config.app_config import APP_CONFIG

DB = TinyDB(APP_CONFIG['db_path'])
