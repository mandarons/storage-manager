#  Copyright (c) 2020, Mandar Patil <mandarons@pm.me>
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
        self.mock_config = Config()
        items, folder_size, number_of_files = folder_operations.folder_stats(config=self.mock_config,
                                                                             folder_path=self.expected_folder)
        self.expected_stats = {
            'size': folder_size,
            'number_of_files': number_of_files,
            'name': 'root',
            'path': self.expected_folder,
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
        self.table.insert({'path': self.expected_folder, 'stats': self.expected_stats})
        actual = self.stats_db.get_drive_stats(name='root')
        self.assertTrue(len(actual) > 0)
        self.assertEqual(actual[0]['path'], self.expected_folder)

    def test_get_non_existing_drive_stats(self):
        actual = self.stats_db.get_drive_stats(name='non-existing-drive')
        self.assertEqual(len(actual), 0)
