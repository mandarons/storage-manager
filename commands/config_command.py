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

import sys

import click
from tabulate import tabulate

from commands import pass_config


@click.group(short_help='Configure the storage.')
@pass_config
def config(config):
    pass


@config.command(short_help='Set the value of a configuration key.')
@click.argument('key', type=str, metavar='<key>')
@click.argument('value', metavar='<value>')
@pass_config
def set(config, key, value):
    '''
    Set the configuration <key> with <value>.

    key: Configuration key to be set

    value: Value of the configuration <key> to be set
    '''
    config.debug(f'Setting {key} to {value} ...')
    if key == 'strategy':
        if not value in ['balanced', 'random']:
            config.error(f'Invalid strategy. Please select one of <balanced, random>.')
            sys.exit(1)
    config.meta_db.set_config(key=key, value=value)
    config.debug(f'Configration set successfully.')


@config.command(short_help='Reset the value of a configuration key to default.')
@click.argument('key', type=str, metavar='<key>')
@pass_config
def reset(config, key):
    '''
    Reset the configuration <key> to default.

    key: Configuration key to be reset
    '''
    config.debug(f'Resetting {key} to default ...')
    if key == 'strategy':
        value = 'balanced'
        config.meta_db.set_config(key=key, value=value)
    else:
        config.error(f'Invalid key: {key}')
        sys.exit(1)
    config.debug(f'Configuration reset successfully.')


@config.command(short_help='Get the current value of a configuration <key>.')
@click.argument('key', type=str, metavar='<key>')
@pass_config
def get(config, key):
    '''
    Get the value of configuration <key>.

    key: Configuration key to get the value of
    '''
    config.debug(f'Getting the value of configuration key: {key} ...')
    result = config.meta_db.get_config(key=key)
    if result == None:
        config.error(f'Key: {key} does not exist.')
        sys.exit(1)
    header = result.keys()
    rows = [result.values()]
    config.info(tabulate(rows, header))


@config.command(short_help='Get all the configuration keys and values.')
@pass_config
def get_all(config):
    '''
    Get all the pairs of configuration <key> and <value>.
    '''
    config.debug(f'Getting all the pairs of configuration keys and values ...')
    result = config.meta_db.get_all_config()
    if len(result) == 0:
        config.error('No configuration is found.')
        sys.exit(1)
    header = result[0].keys()
    rows = [r.values() for r in result]
    config.info(tabulate(rows, header))
