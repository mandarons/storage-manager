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

import unittest

from tinydb import Query

import tests as utils
from db.meta_db import MetaDB, DB


class TestMetaDB(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMetaDB, self).__init__(*args, **kwargs)
        self.expected_drive_path = utils.drive_paths[0]
        self.expected_drive_name = utils.drive_names[0]

    def cleanup(self):
        DB.drop_tables()
        utils.delete_file_with_extensions()

    def setUp(self) -> None:
        self.cleanup()
        self.meta_db = MetaDB()

    def tearDown(self) -> None:
        self.cleanup()

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
