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

    def test_set_invalid_strategy(self):
        actual = self.runner.invoke(config_command.set, [self.strategy_key, 'invalid-strategy'])
        self.assertNotEqual(actual.exit_code, 0)

    def test_get_invalid_config(self):
        actual = self.runner.invoke(config_command.get, ['invalid-key'])
        self.assertNotEqual(actual.exit_code, 0)
