__author__ = 'mandar'

import os
import unittest

from tinydb import Query

from commands import Config
from db.stats_db import StatsDB, DB
from operations import folder_operations


class TestStatsDBSuccess(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestStatsDBSuccess, self).__init__(*args, **kwargs)
        self.expected_folder = os.path.dirname(__file__)
        self.root_folder = os.path.dirname(self.expected_folder)
        self.mock_config = Config()
        items, folder_size, number_of_files = folder_operations.folder_stats(config=self.mock_config,
                                                                             folder_path=self.root_folder)
        self.root_stats = {
            'size': folder_size,
            'number_of_files': number_of_files,
            'name': 'root',
            'path': self.root_folder,
            'items': items
        }

    def setUp(self) -> None:
        DB.drop_tables()
        self.stats_db = StatsDB()
        self.table = DB.table('stats', cache_size=0)

    def tearDown(self) -> None:
        # pass
        DB.drop_tables()

    def test_init_config(self):
        self.assertIsNotNone(self.stats_db.stats_table)

    def test_upsert_new_document(self):
        self.stats_db.upsert(folder_path=self.expected_folder, stats={})
        actual = self.table.search(Query().path == self.expected_folder)
        self.assertEqual(self.expected_folder, actual[0]['path'])

    def test_upsert_existing_document(self):
        self.stats_db.upsert(folder_path=self.expected_folder, stats={})
        expected_stats = {'key': 'value'}
        self.stats_db.upsert(folder_path=self.expected_folder, stats=expected_stats)
        actual = self.table.search(Query().path == self.expected_folder)
        self.assertDictEqual(expected_stats, actual[0]['stats'])

    def test_remove(self):
        self.table.insert({'path': self.expected_folder, 'stats': {}})
        self.stats_db.remove(folder_path=self.expected_folder)
        self.assertEqual(len(self.table.search(Query().path == self.expected_folder)), 0)

    def test_get_drive_stats(self):
        self.table.insert({'path': self.root_folder, 'stats': self.root_stats})
        actual = self.stats_db.get_drive_stats(name='root')
        self.assertTrue(len(actual) > 0)
        self.assertEqual(actual[0]['path'], self.root_folder)

    def test_get_non_existing_drive_stats(self):
        actual = self.stats_db.get_drive_stats(name='non-existing-drive')
        self.assertEqual(len(actual), 0)
