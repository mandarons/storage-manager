__author__ = 'mandar'

import unittest

from click.testing import CliRunner
from tinydb import Query

from commands import config_command
from db.meta_db import DB


class TestConfigCommand(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestConfigCommand, self).__init__(*args, **kwargs)
        self.strategy_key = 'strategy'
        self.expected_strategies = ['balanced', 'random']
        self.config_table = DB.table('config', cache_size=0)

    def setUp(self) -> None:
        DB.drop_tables()
        self.runner = CliRunner()

    def tearDown(self) -> None:
        DB.drop_tables()

    def test_set_config(self):
        actual = self.runner.invoke(config_command.set, [self.strategy_key, self.expected_strategies[0]])
        self.assertEqual(actual.exit_code, 0)
        self.assertEqual(self.config_table.search(Query().key == self.strategy_key)[0]['value'],
                         self.expected_strategies[0])

    def test_set_duplicate_config(self):
        actual = self.runner.invoke(config_command.set, [self.strategy_key, self.expected_strategies[0]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(config_command.set, [self.strategy_key, self.expected_strategies[1]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.config_table.search(Query().key == self.strategy_key)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0]['value'], self.expected_strategies[1])

    def test_reset_existing_config(self):
        actual = self.runner.invoke(config_command.set, [self.strategy_key, self.expected_strategies[1]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.config_table.search(Query().key == self.strategy_key)
        self.assertEqual(actual[0]['value'], self.expected_strategies[1])
        actual = self.runner.invoke(config_command.reset, [self.strategy_key])
        self.assertEqual(actual.exit_code, 0)
        actual = self.config_table.search(Query().key == self.strategy_key)
        self.assertEqual(actual[0]['value'], self.expected_strategies[0])

    def test_reset_non_existing_config(self):
        actual = self.runner.invoke(config_command.reset, ['non-existing-key'])
        self.assertNotEqual(actual.exit_code, 0)

    def test_get_existing_config(self):
        actual = self.runner.invoke(config_command.set, [self.strategy_key, self.expected_strategies[0]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(config_command.get, [self.strategy_key])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn(self.expected_strategies[0], actual.output)

    def test_get_all_configs(self):
        actual = self.runner.invoke(config_command.set, [self.strategy_key, self.expected_strategies[0]])
        self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(config_command.set, ['some-key', 'some-value'])
        self.assertEqual(actual.exit_code, 0)
        actual = self.runner.invoke(config_command.get_all, [])
        self.assertEqual(actual.exit_code, 0)
        self.assertIn(self.strategy_key, actual.output)
        self.assertIn(self.expected_strategies[0], actual.output)
        self.assertIn('some-key', actual.output)
        self.assertIn('some-value', actual.output)

    def test_get_all_empty_configs(self):
        actual = self.runner.invoke(config_command.get_all, [])
        self.assertNotEqual(actual.exit_code, 0)
        self.assertIn('No configuration is found.', actual.output)
