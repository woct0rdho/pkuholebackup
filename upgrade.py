#!/usr/bin/python3

import os
from utils import *

cdname = os.path.dirname(__file__)
input_folder = os.path.join(cdname, 'in')
output_folder = os.path.join(cdname, 'archive')

if __name__ == '__main__':
    for root, dirs, files in os.walk(input_folder):
        for file in sorted(files):
            my_log(file)
            write_posts(
                os.path.join(output_folder, file),
                map(get_comment,
                    parse_file_old(os.path.join(input_folder, file))))
