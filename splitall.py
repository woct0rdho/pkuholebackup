#!/usr/bin/python3

import os
from datetime import date

from utils import my_log, post_dict_to_list, read_posts, write_posts

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')
archive_dir = os.path.join(cdname, 'archivebak')
archive_basename = 'pkuhole'
archive_extname = '.txt'

if __name__ == '__main__':
    post_list = read_posts(filename)
    last_date = date.fromtimestamp(post_list[0]['timestamp'])
    now_post_dict = {}
    for post in post_list:
        now_date = date.fromtimestamp(post['timestamp'])
        if now_date < last_date:
            archive_filename = os.path.join(
                archive_dir, last_date.strftime('%Y%m'), archive_basename +
                last_date.strftime('%Y%m%d') + archive_extname)
            write_posts(archive_filename, post_dict_to_list(now_post_dict))
            last_date = now_date
            now_post_dict = {}
            my_log(last_date.strftime('%Y%m%d'))
        now_post_dict[post['pid']] = post
    archive_filename = os.path.join(
        archive_dir, last_date.strftime('%Y%m'),
        archive_basename + last_date.strftime('%Y%m%d') + archive_extname)
    write_posts(archive_filename, post_dict_to_list(now_post_dict))
