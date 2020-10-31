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

from commands import pass_config, drive_command, config_command, stats_command
from operations import folder_operations, storage_operations


@click.group()
@click.option('--verbose', is_flag=True)
@pass_config
def storage(config, verbose):
    config.verbose = verbose


@storage.command(short_help='Manage your storage.')
@pass_config
def info(config):
    '''
    Get the information about your storage.
    '''
    config.debug('Getting information about your storage ...')
    all_drives_stat = config.stats_db.get_all()
    if len(all_drives_stat) == 0:
        config.error('No drives found.')
        sys.exit(1)
    total_storage = 0
    used_storage = 0
    free_storage = 0
    db_path = config.app_config['db_path']
    for drive in all_drives_stat:
        total_storage += drive['stats']['total']
        used_storage += drive['stats']['used']
        free_storage += drive['stats']['free']
    config.info(message='Summary of storage', bold=True)
    config.info(tabulate([
        ['db_path', db_path],
        ['total', humanfriendly.format_size(total_storage)],
        ['free', humanfriendly.format_size(free_storage)],
        ['used', humanfriendly.format_size(used_storage)]
    ]))
    config.info(message='Stats of storage', bold=True)
    stats_command._show_all_stats(config)


@storage.command(short_help='Refresh metadata of the storage.')
@click.option('--force', is_flag=True)
@pass_config
def refresh(config, force):
    '''
    Refreshes the metadata of your storage. Depending on number of files, this operation may take a while.
    '''
    config.debug('Refreshing the storage metadata ...')
    list_of_drives = config.meta_db.get_drives()
    if len(list_of_drives) == 0:
        config.error('No drives found. Nothing to refresh.')
        sys.exit(1)
    drive_names = [d['name'] for d in list_of_drives]
    for drive_name in drive_names:
        config.info(f'Refreshing drive: {drive_name} ...')
        drive_command._refresh_drive(config=config, name=drive_name, force_hash=force)


@storage.command(short_help='Insert a new file or folder into the storage.')
@click.option('--delete-source', is_flag=True, default=False)
@click.argument('storage_path', type=str, metavar='<storage_path>')
@click.argument('source_path', type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
                metavar='<source_path>')
@pass_config
@click.pass_context
def insert(context, config, storage_path, source_path, delete_source):
    '''
    Insert a new file or folder into the storage

    storage_path: Destination path within the storage e.g. movies/, music/ etc.
    source_path: Source path of the data (file or folder) to be inserted into the storage
    delete_source: Flag to indicate if source to be deleted or not (move operation)
    '''
    config.debug(f'Inserting {source_path} at {storage_path} ...')
    # algorithm:
    #   Get size of transfer, identify destination (based on algorithm, capacity available etc.), initiate cpsync
    transfer_size = folder_operations.get_transfer_size(source=source_path)
    destination_drive = storage_operations.determine_destination_drive(config=config, space_required=transfer_size)
    destination_path = os.path.join(destination_drive['path'], storage_path)
    if not os.path.isdir(s=destination_path):
        os.mkdir(destination_path)
    config.debug(message=f'Copying the file {source_path} to {destination_path}')
    result = folder_operations.cpsync(config=config, source=source_path, destination=destination_path, dry_run=False,
                                      delete_source=delete_source)
    if result:
        if delete_source:
            config.info(message='Moved.')
        else:
            config.info(message='Copied. Please delete the local copy.')
        context.invoke(refresh, force=False)
    config.debug(f'File {source_path} copied to {destination_path}.')


@storage.command(short_help='Move files within the storage.')
@click.option('--copy-only', is_flag=True, default=False)
@click.argument('storage_path', type=str, metavar='<storage_path>')
@click.argument('source_storage_path', type=str, metavar='<source_storage_path>')
@pass_config
@click.pass_context
def move(context, config, storage_path, source_storage_path, copy_only):
    '''
    Move an existing file or folder within the storage

    storage_path: Destination path within the storage e.g. movies/, music/ etc.
    source_storage_path: Source storage path within the storage e.g. drive-1:/movies/movie-1, drive-2:/music/ etc.
    copy_only: Flag to indicate if source should not be deleted (copy operation)
    '''
    config.debug(f'Moving {source_storage_path} to {storage_path} ...')
    # algorithm:
    # Check for the valid storage source path
    source_tokens = source_storage_path.split(':')
    if len(source_tokens) != 2:
        config.error('Invalid source storage path. Correct format is <drive_name>:/<path_within_the_drive>.')
        sys.exit(1)

    # Resolve source storage path to absolute path
    source_drive_path = config.meta_db.get_drive_path(name=source_tokens[0])
    source_path = folder_operations.join_paths(source_drive_path, source_tokens[1])

    # Get transfer size
    transfer_size = folder_operations.get_transfer_size(source=source_path)

    # Determine destination path, excluding the source drive
    destination_drive = storage_operations.determine_destination_drive(config=config, space_required=transfer_size,
                                                                       exclude_drives=[source_tokens[0]])
    destination_path = os.path.join(destination_drive['path'], storage_path)

    # Initiate cpsync
    if not os.path.isdir(s=destination_path):
        os.mkdir(destination_path)
    config.debug(message=f'Copying the file {source_path} to {destination_path}')
    result = folder_operations.cpsync(config=config, source=source_path, destination=destination_path, dry_run=False,
                                      delete_source=not copy_only)
    if result:
        if not copy_only:
            config.info(message='Moved.')
        else:
            config.info(message='Copied. Please delete the local copy.')
    # Invoke refresh
    context.invoke(refresh, force=False)


storage.add_command(drive_command.drive)
storage.add_command(config_command.config)
storage.add_command(stats_command.stats)
