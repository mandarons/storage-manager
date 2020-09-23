__author__ = 'mandar'

import os

APP_CONFIG = {
    'db_path': os.environ.get('DB_PATH', os.path.join(os.path.expanduser('~'), '.storage-manager/db.json')),
}
