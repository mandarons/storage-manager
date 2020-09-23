__author__ = 'mandar'

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
            if False == utils.delete_folder(path=path):
                utils.create_folder(path=path)
        if False == utils.delete_temp_file():
            utils.create_temp_file()

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

    def test_storage_info(self):
        actual = self.runner.invoke(storage_command.info)
        self.assertNotEqual(actual.exit_code, 0)
        self.assertNotIn('Usage', actual.output)

    def test_storage_refresh(self):
        actual = self.runner.invoke(storage_command.refresh)
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
