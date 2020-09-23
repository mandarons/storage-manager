__author__ = 'mandar'

from tinydb import Query

from db import DB


class StatsDB(object):
    def __init__(self):
        self.stats_table = DB.table('stats', cache_size=0)
        self.DB = DB

    def upsert(self, folder_path, stats):
        return self.stats_table.upsert({'path': folder_path, 'stats': stats}, Query().path == folder_path)

    def remove(self, folder_path):
        return self.stats_table.remove(Query().path == folder_path)

    def get_all(self):
        return self.stats_table.all()

    def get_drive_stats(self, name):
        return self.stats_table.search(Query().stats.name == name)
