#!/usr/bin/python3

import os
from datetime import date, datetime, timedelta

from utils import force_remove, get_comment, my_log, read_posts, write_posts

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')
archive_dir = os.path.join(cdname, 'archive')
archive_basename = 'pkuhole'
archive_extname = '.txt'

day_count = 2

if __name__ == '__main__':
    out_date = date.today() - timedelta(day_count)
    archive_filename = os.path.join(
        archive_dir, out_date.strftime('%Y%m'),
        archive_basename + out_date.strftime('%Y%m%d') + archive_extname)
    if os.path.exists(archive_filename):
        my_log('Archive file exists')
        exit()

    my_log('Archive {}'.format(archive_filename))
    try:
        max_timestamp = int(
            datetime.combine(out_date + timedelta(1),
                             datetime.min.time()).timestamp())
        write_posts(archive_filename, [
            get_comment(post) for post in read_posts(filename)
            if post['timestamp'] < max_timestamp
        ])
    except Exception as e:
        my_log('Error: {}'.format(e))
        force_remove(archive_filename)
    else:
        with open(
                os.path.join(cdname, 'split.flag'),
                'w',
                encoding='utf-8',
                newline='\n') as g:
            g.write(str(max_timestamp))
