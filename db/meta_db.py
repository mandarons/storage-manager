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

from tinydb import Query

from db import DB


class MetaDB(object):
    def __init__(self):
        self.drives_table = DB.table('drives', cache_size=0)
        self.config_table = DB.table('config', cache_size=0)

    def add_drive(self, name, path):
        return self.drives_table.upsert({'name': name, 'path': path}, Query().name == name)

    def remove_drive(self, name):
        return self.drives_table.remove(Query().name == name)

    def get_drives(self):
        return self.drives_table.all()

    def get_drive_path(self, name):
        drive_path = None
        drive_info = self.drives_table.search(Query().name == name)
        if len(drive_info) > 0:
            drive_path = drive_info[0]['path']
        return drive_path

    def set_config(self, key, value):
        self.config_table.upsert({'key': key, 'value': value}, Query().key == key)

    def get_config(self, key):
        data = self.config_table.get(Query().key == key)
        return data if data is not None else {}

    def get_all_config(self):
        return self.config_table.all()
