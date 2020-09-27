# Storage Manager [![PyPI version](https://badge.fury.io/py/storage-manager.svg)](https://badge.fury.io/py/storage-manager) [![Build Status](https://travis-ci.org/mandarons/storage-manager.svg?branch=master)](https://travis-ci.org/mandarons/storage-manager) <a href="https://www.buymeacoffee.com/mandarons" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 20px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a> 
Simple command line utility written in Python, to manage your storage distributed over multiple hard drives.

## Requirements
* Python 3.8+
## Installation, Uninstallation and Upgrade
* To install, run 
    ```
    pip3 install storage-manager
    ```
* To uninstall, run
    ```
    pip3 uninstall storage-manager
    ``` 
* To upgrade, run
    ```
    pip3 install --upgrade storage-manager
    ```
## Examples
* Add an existing drive mounted at /mount/d to storage as drive-d
    ```
    storage drive add drive-d /mount/d
    ```
* Configure storage to use ```balanced``` strategy (default is ```random```)
    ```
    storage config set strategy balanced
    ```
* Insert a file ```/home/username/downloads/movie-file.mp4``` into the storage at path ```movies```
    ```
    storage insert movies /home/username/downloads/movie-file.mp4
    ```
  This will copy the file into storage. It will not delete source file.
* Check overall storage status
    ```
    storage stats show-all
    ``` 
## Help
Command line is relatively self-explanatory. If required, use ```--help``` for help and ```--verbose``` for verbose output.
