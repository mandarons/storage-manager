__author__ = 'mandar'

import click

from config import app_config
from db.meta_db import MetaDB
from db.stats_db import StatsDB
from operations import folder_operations

class Config(object):
    def __init__(self):
        self.stats_db = StatsDB()
        self.meta_db = MetaDB()
        self.folder_operations = folder_operations
        self.verbose = False
        self.app_config = app_config.APP_CONFIG

    def error(self, message):
        return click.echo(click.style(message, fg='red'))

    def warning(self, message):
        return click.echo(click.style(message, fg='yellow'))

    def info(self, message):
        return click.echo(click.style(message, fg='blue'))

    def debug(self, message):
        return click.echo(message=message) if self.verbose else ''


pass_config = click.make_pass_decorator(Config, ensure=True)
