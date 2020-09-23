__author__ = 'mandar'

import unittest

from config import app_config


class TestAppConfigSuccess(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAppConfigSuccess, self).__init__(*args, **kwargs)
        self.env_dict = {}
        with open('../config/.env', 'r') as f:
            lines = f.readlines()
            for line in lines:
                tokens = line.split('=')
                tokens[1] = tokens[1].replace('"', '')
                self.env_dict[tokens[0]] = f'{tokens[1]}'

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def test_app_config_dict(self):
        self.assertNotEqual(len(app_config.APP_CONFIG), 0)
        self.assertEqual(app_config.APP_CONFIG['db_path'], self.env_dict['DB_PATH'])
