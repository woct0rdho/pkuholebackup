#!/usr/bin/python3

from check import check_file
from utils import *

cdname = os.path.dirname(__file__)
archive_folder = os.path.join(cdname, 'archive', '201709')

if __name__ == '__main__':
    for root, dirs, files in os.walk(archive_folder):
        for file in sorted(files):
            check_file(os.path.join(root, file))
