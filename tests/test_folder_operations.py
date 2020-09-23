__author__ = 'mandar'

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
                                                folder_path=os.path.dirname(os.path.dirname(__file__)))
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
