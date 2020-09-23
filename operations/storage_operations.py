__author__ = 'mandar'

import random
import shutil


def calculate_storage_usage(config, path):
    usage = {}
    total, used, free = shutil.disk_usage(path=path)
    usage[path] = {
        'total': total,
        'used': used,
        'free': free
    }
    return usage


def determine_destination_drive(config, space_required):
    algorithm = config.meta_db.get_config(key='strategy')
    drives = config.meta_db.get_drives()
    eligible_drives = []
    for drive in drives:
        usage = calculate_storage_usage(config=config, path=drive['path'])
        usage = usage[drive['path']]
        if space_required < usage['free']:
            eligible_drives.append({'name': drive['name'], 'free': usage['free'], 'path': drive['path']})
    if algorithm == 'balanced':
        destination_drive = max([e['free'] for e in eligible_drives])
    else:
        destination_drive = random.choice(eligible_drives)
    return destination_drive
