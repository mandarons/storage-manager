__author__ = 'mandar'

import sys

import click
import humanfriendly
from tabulate import tabulate

from commands import pass_config


@click.group(short_help='Shows various statistics.')
@pass_config
def stats(config):
    pass


@stats.command(short_help='Shows summary of storage.')
@pass_config
def show_all(config):
    '''
    Summary of storage.
    '''
    if config.verbose:
        config.debug(f'Showing summary of storage ...')
    result = config.stats_db.get_all()
    if len(result) == 0:
        config.error(f'No stats exist.')
        sys.exit(1)
    data = [list(r['stats'].values())[:-1] for r in result]
    for entry in data:
        entry[0] = humanfriendly.format_size(entry[0])
        entry[1] = humanfriendly.format_size(entry[1])
        entry[2] = humanfriendly.format_size(entry[2])
        entry[3] = humanfriendly.format_number(entry[3])
    headers = list(result[0]['stats'])
    headers.remove('items')
    config.info(tabulate(tabular_data=data, headers=headers))
    if config.verbose:
        config.debug(f'Completed.')
    return result
