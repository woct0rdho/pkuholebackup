#!/usr/bin/python3

import os

from utils import get_comment, read_posts, write_posts

default_reply = -1
fix_comment = True

cdname = os.path.dirname(__file__)
archive_dir = os.path.join(cdname, 'archive')


def check_comment(filename):
    post_list = read_posts(filename)

    updated = False
    for post in post_list:
        comment_list = []
        cid_set = set()
        for comment in post['comments']:
            if comment['cid'] in cid_set:
                print(post['pid'], comment['cid'])
                updated = True
            else:
                comment_list.append(comment)
                cid_set.add(comment['cid'])
        post['comments'] = comment_list

        if default_reply is not False and (
                post['reply'] != default_reply
                and post['reply'] != len(post['comments'])):
            print(post['pid'], 'replies not match', post['reply'],
                  len(post['comments']))
            if fix_comment:
                get_comment(post)
                updated = True

    if updated:
        write_posts(filename, post_list)


if __name__ == '__main__':
    for root, dirs, files in os.walk(archive_dir):
        for file in sorted(files):
            if file < 'pkuhole201507':
                continue
            print(file)
            filename = os.path.join(root, file)
            check_comment(filename)
