#!/usr/bin/python3

import os

from merge import merge_file
from utils import my_log

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
            merge_file(in_filename1, in_filename2, out_filename)
