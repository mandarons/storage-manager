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
import sys

import click
import humanfriendly
from tabulate import tabulate

from commands import pass_config
from operations import storage_operations


@click.group(short_help='Manage drives.')
@pass_config
def drive(config):
    pass


@drive.command(short_help='Adds a new drive to the storage.')
@click.argument('name', type=str, metavar='<name>')
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True, readable=True),
                metavar='<path>')
@pass_config
@click.pass_context
def add(context, config, name, path):
    '''
    Add a new drive

    name: name of the drive

    path: mount path of the drive

    '''
    config.debug(f'Adding the drive {name} mounted at {path} ...')

    result = config.meta_db.add_drive(name=name, path=os.path.join(os.path.abspath(path=path), ''))
    if len(result) == 0:
        config.error(f'Failed to add the drive {drive} with path {path}.')
        sys.exit(1)
    context.invoke(refresh, name=name)
    config.debug(f'Drive {name} added to the storage.')


@drive.command(short_help='Removes existing drive from the storage.')
@click.argument('name', type=str, metavar='<name>')
@pass_config
def remove(config, name):
    '''
    Delete all the content of the drive <name> and remove it

    name: drive to be removed

    '''
    config.debug(f'Removing {name} ...')
    drive_path = config.meta_db.get_drive_path(name=name)
    if drive_path is None:
        config.warning('Path for drive does not exist. Stats will not be removed.')
    result = config.stats_db.remove(folder_path=drive_path)
    if len(result) == 0:
        config.warning('Stats were not available.')
    result = config.meta_db.remove_drive(name=name)
    if len(result) == 0:
        config.error(f'Nothing to remove. Drive {name} does not exist.')
        sys.exit(1)
    config.debug(f'Drive {name} removed.')


@drive.command(short_help='Shows current list of drives from the storage.')
@pass_config
def list(config):
    '''
    Shows current list of drives in the storage.
    '''
    config.debug('Retrieving the list of drives ...')

    result = config.meta_db.get_drives()
    if len(result) > 0:
        header = result[0].keys()
        rows = [r.values() for r in result]
        config.info(tabulate(rows, header))
    else:
        config.error('No drives found.')
        sys.exit(1)
    config.debug('Listing of drives completed.')

    return result


def _refresh_drive(config, name):
    drive_path = config.meta_db.get_drive_path(name=name)
    if drive_path is None:
        config.error(f'Drive with name: {name} does not exist.')
        sys.exit(1)
    items, drive_size, num_of_files = config.folder_operations.folder_stats(config=config, folder_path=drive_path)
    usage = storage_operations.calculate_storage_usage(config=config, path=drive_path)
    result = config.stats_db.upsert(folder_path=drive_path, stats={
        'total': usage[drive_path]['total'],
        'free': usage[drive_path]['free'],
        'used': usage[drive_path]['used'],
        'number_of_files': num_of_files,
        'name': name,
        'path': drive_path,
        'items': items,

    })
    return result, usage[drive_path]['total'], num_of_files


@drive.command(short_help='Refreshes the drive <name> statistics')
@click.argument('name', type=str, metavar='<name>')
@pass_config
def refresh(config, name):
    '''
    Refreshes the folder statistics for the drive <name>

    name: name of the drive
    '''
    config.debug(f'Refreshing the drive {name} ...')
    result, drive_size, num_of_files = _refresh_drive(config=config, name=name)
    config.info(tabulate([[humanfriendly.format_size(drive_size), humanfriendly.format_number(num_of_files)]],
                         ['Drive Size', 'Number of Files']))
    if len(result) == 0:
        config.error(f'Failed to store the stats for drive {name}. Please try again.')
        sys.exit(1)

    config.debug(f'Drive {name} refreshed.')
