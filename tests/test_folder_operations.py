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
import shutil
import unittest

import tests as utils
from commands import Config
from operations import folder_operations


class TestFolderOperations(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestFolderOperations, self).__init__(*args, **kwargs)
        self.config = Config()
        self.expected_drive_names = utils.drive_names
        self.expected_drive_paths = utils.drive_paths

    @classmethod
    def setUpClass(cls) -> None:
        utils.create_temp_file()

    @classmethod
    def tearDownClass(cls) -> None:
        utils.delete_temp_file()

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_folder_stats(self):
        actual = folder_operations.folder_stats(config=self.config,
                                                folder_path=os.path.dirname(__file__))
        self.assertIsNotNone(actual)
        self.assertNotEqual(len(actual), 0)
        self.assertNotEqual(len(actual[0]), 0)

    def test_cpsync(self):
        source = utils.temp_file_path
        destination = os.path.join(os.path.dirname(__file__), 'd', '')
        actual = folder_operations.cpsync(config=self.config, source=source, destination=destination,
                                          dry_run=False)
        if os.path.exists(destination):
            shutil.rmtree(destination)
        self.assertIsNotNone(actual)
