__author__ = 'mandar'

import unittest

from click.testing import CliRunner

import tests as utils
from commands import drive_command
from db.meta_db import DB


class TestE2E(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestE2E, self).__init__(*args, **kwargs)
        self.expected_drive_names = utils.drive_names
        self.expected_drive_paths = utils.drive_paths

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

    def test_add_drive_flow(self):
        # Add non-existing drive
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        drives = self.runner.invoke(drive_command.list)
        self.assertIn(self.expected_drive_names[0], drives.output)

        # Check for no duplicate names
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[0], self.expected_drive_paths[0]])
        self.assertEqual(actual.exit_code, 0)
        drives = self.runner.invoke(drive_command.list)
        self.assertIn(self.expected_drive_names[0], drives.output)

        # Add multiple drives
        actual = self.runner.invoke(drive_command.add, [self.expected_drive_names[1], self.expected_drive_paths[1]])
        self.assertEqual(actual.exit_code, 0)
        drives = self.runner.invoke(drive_command.list)
        self.assertIn(self.expected_drive_names[0], drives.output)
        self.assertIn(self.expected_drive_names[1], drives.output)
