__author__ = 'mandar'

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='storage-manager',
    version='0.0.5',
    author='Mandar Patil',
    author_email='mandarons@pm.me',
    description='Storage - a load-balanced storage manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mandarons/storage-manager',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.8',
    py_modules=['main'],
    install_requires=[
        'click==7.1.2',
        'python-dotenv==0.14.0',
        'tinydb==4.1.1',
        'humanfriendly==8.2',
        'tabulate==0.8.7',
        'tqdm==4.48.2'
    ],
    entry_points='''
    [console_scripts]
    storage=commands.storage_command:storage
    '''
)
