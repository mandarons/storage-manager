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
            if utils.delete_folder(path=path) is False:
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
