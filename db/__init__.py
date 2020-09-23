__author__ = 'mandar'

import os
from tinydb import TinyDB

from config.app_config import APP_CONFIG

os.makedirs(os.path.dirname(APP_CONFIG['db_path']), exist_ok=True)

DB = TinyDB(APP_CONFIG['db_path'])
