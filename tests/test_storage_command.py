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

from click.testing import CliRunner

import tests as utils
from commands import Config
from commands import drive_command, storage_command, config_command
from db.stats_db import DB


class TestStorageCommand(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestStorageCommand, self).__init__(*args, **kwargs)
        self.expected_drive_names = utils.drive_names
        self.expected_drive_paths = utils.drive_paths
        self.temp_file_path = utils.temp_file_path
        self.config = Config()

    def cleanup(self):
        DB.drop_tables()
        for path in self.expected_drive_paths:
            if utils.delete_folder(path=path) is False:
                utils.create_folder(path=path)
        if utils.delete_temp_file() is False:
            utils.create_temp_file()
        utils.delete_file_with_extensions()

    def setUp(self) -> None:
        self.cleanup()
        self.runner = CliRunner()

    def tearDown(self) -> None:
        self.cleanup()

    def test_storage_command(self):
        actual = self.runner.invoke(storage_command.storage)
        self.assertIsNotNone(actual)
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Usage', actual.output)

    def test_storage_info_error(self):
        actual = self.runner.invoke(storage_command.info)
        self.assertNotEqual(actual.exit_code, 0)
        self.assertNotIn('Usage', actual.output)

    def test_storage_info_valid(self):
        for drive_name, drive_path in zip(self.expected_drive_names, self.expected_drive_paths):
            actual = self.runner.invoke(drive_command.add, [drive_name, drive_path])
            self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(storage_command.info)
        self.assertEqual(actual.exit_code, 0)

    def test_storage_refresh(self):
        for drive_name, drive_path in zip(self.expected_drive_names, self.expected_drive_paths):
            actual = self.runner.invoke(drive_command.add, [drive_name, drive_path])
            self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(storage_command.refresh)
        self.assertEqual(actual.exit_code, 0)
        self.assertNotIn('Usage', actual.output)

    def test_storage_refresh_without_drives(self):
        actual = self.runner.invoke(storage_command.refresh)
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('No drives found', actual.output)

    def test_storage_refresh_force(self):
        for drive_name, drive_path in zip(self.expected_drive_names, self.expected_drive_paths):
            actual = self.runner.invoke(drive_command.add, [drive_name, drive_path])
            self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(storage_command.refresh, ['--force'])
        self.assertEqual(actual.exit_code, 0)
        self.assertNotIn('Usage', actual.output)

    def test_storage_insert_without_arguments(self):
        actual = self.runner.invoke(storage_command.insert)
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('Usage', actual.output)

    def test_storage_insert_with_invalid_arguments(self):
        actual = self.runner.invoke(storage_command.insert, ['drive-a', __file__])
        self.assertNotEqual(actual.exit_code, 0)
        self.assertNotIn('Usage', actual.output)

    def test_storage_insert_balanced(self):
        for drive_name, drive_path in zip(self.expected_drive_names, self.expected_drive_paths):
            actual = self.runner.invoke(drive_command.add, [drive_name, drive_path])
            self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(config_command.set, ['strategy', 'balanced'])
        self.assertEqual(actual.exit_code, 0)
        self.assertFalse(os.path.exists(
            os.path.join(self.expected_drive_paths[0], 'movies', os.path.basename(self.temp_file_path))) or
                         os.path.exists(os.path.join(self.expected_drive_paths[1], 'movies',
                                                     os.path.basename(self.temp_file_path))))

        actual = self.runner.invoke(storage_command.insert, ['movies', self.temp_file_path])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Copied', actual.output)
        self.assertIn(True, [os.path.exists(os.path.join(path, 'movies', os.path.basename(self.temp_file_path)))
                             for path in self.expected_drive_paths])

    def test_storage_insert_random(self):
        for drive_name, drive_path in zip(self.expected_drive_names, self.expected_drive_paths):
            actual = self.runner.invoke(drive_command.add, [drive_name, drive_path])
            self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(config_command.set, ['strategy', 'random'])
        self.assertEqual(actual.exit_code, 0)
        self.assertFalse(os.path.exists(
            os.path.join(self.expected_drive_paths[0], 'movies', os.path.basename(self.temp_file_path))) or
                         os.path.exists(os.path.join(self.expected_drive_paths[1], 'movies',
                                                     os.path.basename(self.temp_file_path))))

        actual = self.runner.invoke(storage_command.insert, ['movies', self.temp_file_path])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Copied', actual.output)
        self.assertIn(True, [os.path.exists(os.path.join(path, 'movies', os.path.basename(self.temp_file_path)))
                             for path in self.expected_drive_paths])
