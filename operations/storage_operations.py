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

import random
import shutil


def calculate_storage_usage(config, path):
    usage = {}
    total, used, free = shutil.disk_usage(path=path)
    usage[path] = {
        'total': total,
        'used': used,
        'free': free
    }
    return usage


def determine_destination_drive(config, space_required):
    algorithm = config.meta_db.get_config(key='strategy')
    algorithm = algorithm['value'] if 'value' in algorithm else ''
    drives = config.meta_db.get_drives()
    eligible_drives = []
    for drive in drives:
        usage = calculate_storage_usage(config=config, path=drive['path'])
        usage = usage[drive['path']]
        if space_required < usage['free']:
            eligible_drives.append({'name': drive['name'], 'free': usage['free'], 'path': drive['path']})
    if algorithm == 'balanced':
        max_free = max([e['free'] for e in eligible_drives])
        destination_drive = next((x for x in eligible_drives if x['free'] == max_free))
    else:
        destination_drive = random.choice(eligible_drives)
    return destination_drive
