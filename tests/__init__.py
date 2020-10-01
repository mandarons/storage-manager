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

temp_file_path = os.path.join(os.path.dirname(__file__), 'temp_file_1GB.bin')
drive_names = ['d', 'e', 'f', 'g', 'h']
drive_paths = [os.path.join(os.path.dirname(__file__), p, '') for p in drive_names]
drive_root = os.path.dirname(__file__)


def create_file(path, size=1048576):
    # 1GB = 1073741824 bytes
    # 1MB = 1048576 bytes
    if not os.path.exists(path=path):
        with open(path, 'wb') as f:
            f.seek(size - 1)
            f.write(b'\0')
    return path


def delete_file(path):
    if os.path.exists(path=path):
        os.remove(path=path)
        return True
    return False


def create_folder(path):
    if not os.path.exists(path=path):
        os.mkdir(path=path)
        return True
    return False


def delete_folder(path):
    if os.path.exists(path=path):
        shutil.rmtree(path=path)
        return True
    return False


def delete_temp_file():
    return delete_file(path=temp_file_path)


def create_temp_file():
    return create_file(path=temp_file_path)


def delete_file_with_extensions(extensions=('md5')):
    for root, dir, files in os.walk(drive_root):
        for current_file in files:
            if current_file.lower().endswith(extensions):
                os.remove(os.path.join(root, current_file))
