__author__ = 'mandar'

import os
import shutil

temp_file_path = os.path.join(os.path.dirname(__file__), 'temp_file_1GB.bin')
drive_names = ['d', 'e', 'f', 'g', 'h']
drive_paths = [os.path.join(os.path.dirname(__file__), p, '') for p in drive_names]


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
