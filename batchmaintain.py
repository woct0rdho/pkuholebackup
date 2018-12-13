#!/usr/bin/python3

import logging
import os

from maintain import compare_file
from utils import my_log

logging.getLogger().handlers = []
logging.basicConfig(
    handlers=[logging.FileHandler('maintain.out', 'w', 'utf-8')],
    level=logging.INFO,
    format='%(asctime)s %(message)s')

cdname = os.path.dirname(__file__)
# 1: old, 2: new
input_dir1 = os.path.join(cdname, 'archive')
input_dir2 = os.path.join(cdname, 'archivebak')
output_dir = os.path.join(cdname, 'archive')

if __name__ == '__main__':
    for root, dirs, files in os.walk(input_dir2):
        for file in sorted(files):
            in_filename2 = os.path.join(root, file)
            in_filename1 = in_filename2.replace(input_dir2, input_dir1)
            out_filename = in_filename2.replace(input_dir2, output_dir)
            my_log(in_filename2)
            compare_file(in_filename1, in_filename2, out_filename)
