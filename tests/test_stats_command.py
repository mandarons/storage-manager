__author__ = 'mandar'

import unittest

from click.testing import CliRunner

import tests as utils
from commands import stats_command
from db.meta_db import DB


class TestStatsCommand(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestStatsCommand, self).__init__(*args, **kwargs)
        self.expected_stats_names = utils.drive_names
        self.expected_stats_paths = utils.drive_paths

    def setUp(self) -> None:
        DB.drop_tables()
        self.runner = CliRunner()

    def tearDown(self) -> None:
        DB.drop_tables()

    def test_show_all_empty_stats(self):
        actual = self.runner.invoke(stats_command.show_all)
        self.assertNotEqual(actual.exit_code, 0)
