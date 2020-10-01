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

import hashlib
import os
import re
import subprocess

from humanfriendly import format_size
from tqdm import tqdm


def calculate_hash(file_path, hash_name, buffer_size=4096):
    """Calculate the hash of a file. The available hashes are given by the hashlib module.
    The available hashes can be listed with hashlib.algorithms_available."""

    hash_name = hash_name.lower()
    if not hasattr(hashlib, hash_name):
        raise Exception('Hash algorithm not available : {}' .format(hash_name))

    with open(file_path, 'rb') as f:
        checksum = getattr(hashlib, hash_name)()
        total_size = os.path.getsize(filename=file_path)
        total_chunks = int(total_size / buffer_size)
        progress_bar = tqdm(total=100, desc='Hashing', bar_format='{desc}|{bar}|{postfix}')
        progress_bar.set_postfix_str(f'{os.path.basename(file_path)}')
        for chunk, index in zip(iter(lambda: f.read(buffer_size), b''), range(total_chunks)):
            checksum.update(chunk)
            percent = 100 * (index + 1) / total_chunks
            progress_bar.update(percent - progress_bar.n)
        progress_bar.close()
        return checksum.hexdigest()


def _recursive_folder_stats(config, folder_path, parent_path, hash_name,
                            ignore_hidden=False, depth=0, idx=1, parent_idx=0):
    items = {}
    folder_size, num_files = 0, 0
    current_idx = idx
    if os.access(folder_path, os.R_OK):
        for f in os.listdir(folder_path):
            if ignore_hidden and f.startswith('.'):
                continue

            file_path = os.path.join(folder_path, f)
            stats = os.stat(file_path)
            folder_size += stats.st_size
            idx += 1

            if os.path.isdir(file_path):
                if config.verbose:
                    print('FOLDER : {}'.format(file_path))

                idx, items[file_path], _foldersize, _num_files = _recursive_folder_stats(
                    config=config, folder_path=file_path, parent_path=folder_path, hash_name=hash_name,
                    ignore_hidden=ignore_hidden, depth=depth + 1, idx=idx, parent_idx=current_idx)
                folder_size += _foldersize
                num_files += _num_files
            else:
                filename, extension = os.path.splitext(f)
                extension = extension[1:] if extension else None
                item = {
                    'index': idx,
                    'path': file_path,
                    'filename': filename,
                    'extension': extension,
                    'size': stats.st_size,
                    'last_accessed': stats.st_atime,
                    'last_modified': stats.st_mtime,
                    'last_metadata_changed': stats.st_ctime,
                    'is_folder': False,
                    'num_of_files': None,
                    'depth': depth,
                    'parent_index': current_idx,
                    'parent_path': folder_path,
                    'uid': stats.st_uid,
                    'hash': calculate_hash(file_path=file_path, hash_name=hash_name)
                }
                items[file_path] = item
                num_files += 1

    stats = os.stat(folder_path)
    foldername = os.path.basename(folder_path)
    item = {
        'index': current_idx,
        'path': folder_path,
        'filename': foldername,
        'extension': None,
        'size': folder_size,
        'atime': stats.st_atime,
        'mtime': stats.st_mtime,
        'ctime': stats.st_ctime,
        'is_folder': True,
        'num_of_files': num_files,
        'depth': depth,
        'parent_index': parent_idx,
        'parent_path': parent_path,
        'uid': stats.st_uid
    }
    items['.'] = item
    return idx, items, folder_size, num_files


def folder_stats(config, folder_path, hash_name='md5', ignore_hidden=False):
    idx, items, folder_size, num_files = _recursive_folder_stats(
        config,
        folder_path,
        parent_path=os.path.dirname(folder_path),
        hash_name=hash_name,
        ignore_hidden=ignore_hidden)
    return items, folder_size, num_files


def get_transfer_size(source):
    cmd = ['rsync', '-r', '--no-h', '--no-i-r', '--ignore-existing', '--stats', source]
    with subprocess.Popen(args=cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding='utf-8') as proc:
        output = proc.stdout.readlines()
        proc.stdout.close()
        proc.stderr.close()
        proc.kill()
        proc.wait()
    output = list(filter(lambda e: 'Total file size' in e, output))
    if len(output) > 0:
        m = re.findall(r'(\d+)', output[0])
        if len(m) > 0:
            output = m[0]
    return int(output)


def cpsync(config, source, destination, dry_run=False):
    cmd = ['rsync', '--progress', '--info=progress2', '-r',
           '--no-h', '--no-i-r', '--ignore-existing', '--stats']
    dry_run and cmd.append('--dry-run')
    total_size = get_transfer_size(source=source)
    cmd.append(source)
    cmd.append(destination)
    config.info(f'Source: {source}\nDestination: {destination}')
    with subprocess.Popen(args=cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          encoding='utf-8') as proc:
        progress_bar = tqdm(total=100, desc='Copying', bar_format='{{desc}}|{{bar}}|{{postfix}}')
        while proc.poll() is None:
            output = proc.stdout.readline()
            m = re.findall(r'(\d+)\s+(\d+)%\s+([0-9]*.[0-9]+\w*/s)\s+', output)
            if len(m) == 1 and len(m[0]) == 3:
                size = int(m[0][0])
                percent = int(m[0][1])
                speed = m[0][2]
                progress_bar.set_postfix_str(
                    f'{percent}% {speed} {format_size(size).replace(" ", "")}/{format_size(total_size).replace(" ", "")}')
                progress_bar.update(percent - progress_bar.n)
        progress_bar.close()
        proc.stdout.close()
        proc.stderr.close()
        proc.kill()
        proc.wait()
    return True
