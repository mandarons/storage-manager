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
import os

from click.testing import CliRunner

import tests as utils
from commands import Config
from commands import drive_command, stats_command
from db.stats_db import DB
from operations import folder_operations


class TestDriveCommand(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDriveCommand, self).__init__(*args, **kwargs)
        self.expected_drive_names = utils.drive_names
        self.expected_drive_paths = utils.drive_paths
        self.config = Config()

    def cleanup(self):
        DB.drop_tables()
        for path in self.expected_drive_paths:
            if utils.delete_folder(path=path) is False:
                utils.create_folder(path=path)
        utils.delete_file_with_extensions()

    def setUp(self) -> None:
        self.cleanup()
        self.runner = CliRunner()

    def tearDown(self) -> None:
        self.cleanup()

    def test_add_drive(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertIsNotNone(actual)
        self.assertEqual(actual.exit_code, 0)

    def test_add_duplicate_drive(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        drives = self.runner.invoke(drive_command.list)
        self.assertIn(self.expected_drive_names[0], drives.output)
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[1]])
        self.assertEqual(actual.exit_code, 0)
        drives = self.runner.invoke(drive_command.list)
        self.assertIn(self.expected_drive_names[0], drives.output)
        self.assertIn(self.expected_drive_paths[1], drives.output)
        self.assertNotIn(self.expected_drive_paths[0], drives.output)

    def test_add_invalid_drive(self):
        actual = self.runner.invoke(drive_command.add, ['invalid-name', 'invalid drive'])
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('Usage', actual.output)

    def test_add_multiple_drives(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[1], self.expected_drive_paths[1]])
        self.assertEqual(actual.exit_code, 0)
        drives = self.runner.invoke(drive_command.list)
        self.assertIn(self.expected_drive_names[0], drives.output)
        self.assertIn(self.expected_drive_names[1], drives.output)

    def test_remove_drive(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(drive_command.remove, [self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)

    def test_remove_non_existing_drive(self):
        actual = self.runner.invoke(drive_command.remove, ['non-existing-drive'])
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('Nothing to remove', actual.output)

    def test_get_all_drives(self):
        DB.table('drives').insert({'name': self.expected_drive_names[0], 'path': self.expected_drive_paths[0]})
        DB.table('drives').insert({'name': self.expected_drive_names[1], 'path': self.expected_drive_paths[1]})
        actual = self.runner.invoke(drive_command.list)
        self.assertEqual(actual.exit_code, 0)

    def test_get_empty_list_of_drives(self):
        actual = self.runner.invoke(drive_command.list)
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('No drives found.', actual.output)

    def test_refresh_drive(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        utils.create_file(path=os.path.join(self.expected_drive_paths[0], 'temp.bin'))
        actual = self.runner.invoke(drive_command.refresh, [self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Drive Size', actual.output)
        actual = self.runner.invoke(stats_command.show_all, [])
        self.assertEqual(actual.exit_code, 0)

    def test_refresh_non_existing_drive(self):
        actual = self.runner.invoke(drive_command.refresh, ['non-existing-drive-name'])
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('does not exist', actual.output)

    def test_refresh_drive_with_forced_hash_calculation(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        temp_file_path = os.path.join(self.expected_drive_paths[0], 'temp.bin')
        utils.create_file(path=temp_file_path)
        hash_file = folder_operations.generate_hash_file_path(file_path=temp_file_path, hash_name='md5')
        if os.path.exists(hash_file):
            os.remove(hash_file)
        actual = self.runner.invoke(drive_command.refresh, [self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertTrue(os.path.exists(hash_file))
        old_hash_file_stats = os.stat(hash_file)
        actual = self.runner.invoke(drive_command.refresh, ['--force-hash', self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Drive Size', actual.output)
        self.assertTrue(os.path.exists(hash_file))
        hash_file_stats = os.stat(hash_file)
        self.assertTrue(old_hash_file_stats.st_mtime < hash_file_stats.st_mtime)
        actual = self.runner.invoke(stats_command.show_all, [])
        self.assertEqual(actual.exit_code, 0)

    def test_refresh_drive_skip_hashing_if_md5_exists(self):
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        temp_file_path = os.path.join(self.expected_drive_paths[0], 'temp.bin')
        utils.create_file(path=temp_file_path)
        hash_file = folder_operations.generate_hash_file_path(file_path=temp_file_path, hash_name='md5')
        if os.path.exists(hash_file):
            os.remove(hash_file)
        actual = self.runner.invoke(drive_command.refresh, [self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertTrue(os.path.exists(hash_file))
        old_hash_file_stats = os.stat(hash_file)
        actual = self.runner.invoke(drive_command.refresh, [self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Drive Size', actual.output)
        self.assertTrue(os.path.exists(hash_file))
        hash_file_stats = os.stat(hash_file)
        self.assertEqual(old_hash_file_stats.st_mtime, hash_file_stats.st_mtime)
        actual = self.runner.invoke(stats_command.show_all, [])
        self.assertEqual(actual.exit_code, 0)

    def test_refresh_existing_drive_with_invalid_path(self):
        pass
