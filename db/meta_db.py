__author__ = 'mandar'

from tinydb import Query

from db import DB


class MetaDB(object):
    def __init__(self):
        self.drives_table = DB.table('drives', cache_size=0)
        self.config_table = DB.table('config', cache_size=0)

    def add_drive(self, name, path):
        return self.drives_table.upsert({'name': name, 'path': path}, Query().name == name)

    def remove_drive(self, name):
        return self.drives_table.remove(Query().name == name)

    def get_drives(self):
        return self.drives_table.all()

    def get_drive_path(self, name):
        drive_path = None
        drive_info = self.drives_table.search(Query().name == name)
        if len(drive_info) > 0:
            drive_path = drive_info[0]['path']
        return drive_path

    def set_config(self, key, value):
        self.config_table.upsert({'key': key, 'value': value}, Query().key == key)

    def get_config(self, key):
        return self.config_table.get(Query().key == key)

    def get_all_config(self):
        return self.config_table.all()
