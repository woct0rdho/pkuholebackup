#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
archive_dir = os.path.join(cdname, 'archivetest')

if __name__ == '__main__':
    for root, dirs, files in os.walk(archive_dir):
        for file in sorted(files):
            filename = os.path.join(root, file)
            my_log(filename)
            post_dict = read_posts_dict(filename)
            for post in post_dict.values():
                post['text'] = trim_lines(post['text'])
            write_posts(filename, post_dict_to_list(post_dict))
