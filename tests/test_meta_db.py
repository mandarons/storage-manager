__author__ = 'mandar'

import unittest

from tinydb import Query

import tests as utils
from db.meta_db import MetaDB, DB


class TestMetaDB(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMetaDB, self).__init__(*args, **kwargs)
        self.expected_drive_path = utils.drive_paths[0]
        self.expected_drive_name = utils.drive_names[0]

    def setUp(self) -> None:
        DB.drop_tables()
        self.meta_db = MetaDB()

    def tearDown(self) -> None:
        DB.drop_tables()

    def test_init_config(self):
        self.assertIsNotNone(self.meta_db.drives_table)

    def test_add_drive(self):
        self.meta_db.add_drive(name=self.expected_drive_name, path=self.expected_drive_path)
        self.assertEqual(self.expected_drive_path,
                         DB.table('drives').search(Query().name == self.expected_drive_name)[0]['path'])

    def test_remove_drive(self):
        DB.table('drives').insert({'name': self.expected_drive_name, 'path': self.expected_drive_path})
        self.meta_db.remove_drive(name=self.expected_drive_name)
        self.assertEqual(len(DB.table('drives').search(Query().name == self.expected_drive_name)), 0)
