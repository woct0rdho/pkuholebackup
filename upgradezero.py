#!/usr/bin/python3

import os
from utils import *

cdname = os.path.dirname(__file__)
input_folder = os.path.join(cdname, 'in2')
output_folder = os.path.join(cdname, 'archive2')

if __name__ == '__main__':
    for root, dirs, files in os.walk(input_folder):
        for file in sorted(files):
            my_log(file)
            write_posts(
                os.path.join(output_folder, file),
                filter(lambda x: x['reply'] > 0,
                       map(get_comment,
                           filter(lambda x: x['reply'] <= 0,
                                  parse_file_old(
                                      os.path.join(input_folder, file))))))
