__author__ = 'mandar'

import unittest

from click.testing import CliRunner

import tests as utils
from commands import Config
from commands import drive_command, stats_command
from db.stats_db import DB


class TestDriveCommand(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDriveCommand, self).__init__(*args, **kwargs)
        self.expected_drive_names = utils.drive_names
        self.expected_drive_paths = utils.drive_paths
        self.config = Config()

    def cleanup(self):
        DB.drop_tables()
        for path in self.expected_drive_paths:
            if False == utils.delete_folder(path=path):
                utils.create_folder(path=path)

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
        actual = self.runner.invoke(drive_command.refresh, [self.expected_drive_names[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn('Drive Size', actual.output)
        actual = self.runner.invoke(stats_command.show_all, [])
        self.assertEqual(actual.exit_code, 0)

    def test_refresh_non_existing_drive(self):
        actual = self.runner.invoke(drive_command.refresh, ['non-existing-drive-name'])
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('does not exist', actual.output)

    def test_refresh_existing_drive_with_invalid_path(self):
        pass
