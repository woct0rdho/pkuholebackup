#!/usr/bin/python3
#
# DELETED posts must have latest comments

import logging
import os
from datetime import datetime

from utils import get_comment, my_log, read_posts, write_posts

cdname = os.path.dirname(__file__)
# 1: old, 2: new
input_dir1 = os.path.join(cdname, 'archive')
input_dir2 = os.path.join(cdname, 'archivebak')
output_dir = os.path.join(cdname, 'archive')

default_reply = -1
dry_run = False

logging.getLogger().handlers = []
logging.basicConfig(
    handlers=[logging.FileHandler('compare_out.txt', 'w', 'utf-8')],
    level=logging.INFO,
    format='%(asctime)s %(message)s')


def get_comment_fake(post):
    return post


def write_posts_fake(filename, posts):
    return


if dry_run:
    get_comment = get_comment_fake
    write_posts = write_posts_fake


def compare_reply(post1, post2, out_list, pid, time_str):
    if post1['reply'] == default_reply:
        if post2['reply'] == default_reply:
            out_list.append(post1)
        else:
            out_list.append(get_comment(post1))
    else:
        if post2['reply'] == default_reply:
            out_list.append(post1)
        else:
            if post1['reply'] < post2['reply']:
                out_list.append(get_comment(post1))
            elif post1['reply'] > post2['reply']:
                out_list.append(post1)
            else:
                out_list.append(post1)


def compare_file(filename):
    post_list1 = read_posts(filename.replace(input_dir2, input_dir1))
    post_list2 = read_posts(filename)
    out_list = []

    i = 0
    j = 0
    while i < len(post_list1) and j < len(post_list2):
        post1 = post_list1[i]
        post2 = post_list2[j]
        if post1['text']:
            first_line1 = post1['text'].splitlines()[0]
        else:
            first_line1 = ''
        if post2['text']:
            first_line2 = post2['text'].splitlines()[0]
        else:
            first_line2 = ''

        if post1['pid'] > post2['pid']:
            pid = post1['pid']
            time_str = datetime.fromtimestamp(
                post1['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

            if first_line1 == '#DELETED':
                out_list.append(post1)
            elif first_line1 == '#MISSED':
                out_list.append(post1)
            else:
                my_log('{} {} DELETED\n{}'.format(pid, time_str,
                                                  post1['text'].strip()))
                post1['text'] = '#DELETED\n' + post1['text']
                out_list.append(get_comment(post1))

            i += 1
        elif post1['pid'] < post2['pid']:
            pid = post2['pid']
            time_str = datetime.fromtimestamp(
                post2['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

            if first_line2 == '#DELETED':
                out_list.append(get_comment(post2))
            elif first_line2 == '#MISSED':
                out_list.append(get_comment(post2))
            else:
                my_log('{} {} REBORN'.format(pid, time_str))
                out_list.append(get_comment(post2))

            j += 1
        else:
            pid = post1['pid']
            time_str = datetime.fromtimestamp(
                post1['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

            if first_line1 == '#DELETED':
                if first_line2 == '#DELETED':
                    out_list.append(post1)
                elif first_line2 == '#MISSED':
                    out_list.append(post1)
                else:
                    my_log('{} {} REBORN'.format(pid, time_str))
                    out_list.append(get_comment(post2))
            elif first_line1 == '#MISSED':
                if first_line2 == '#DELETED':
                    my_log('{} {} RECOVERED'.format(pid, time_str))
                    out_list.append(get_comment(post2))
                elif first_line2 == '#MISSED':
                    out_list.append(post1)
                else:
                    my_log('{} {} REBORN'.format(pid, time_str))
                    out_list.append(get_comment(post2))
            else:
                if first_line2 == '#DELETED':
                    my_log('{} {} DELETED\n{}'.format(pid, time_str,
                                                      post1['text'].strip()))
                    post1['text'] = '#DELETED\n' + post1['text']
                    out_list.append(get_comment(post1))
                elif first_line2 == '#MISSED':
                    my_log('{} {} DELETED\n{}'.format(pid, time_str,
                                                      post1['text'].strip()))
                    post1['text'] = '#DELETED\n' + post1['text']
                    out_list.append(get_comment(post1))
                else:
                    compare_reply(post1, post2, out_list, pid, time_str)

            i += 1
            j += 1

    while i < len(post_list1):
        post1 = post_list1[i]
        if post1['text']:
            first_line1 = post1['text'].splitlines()[0]
        else:
            first_line1 = ''

        pid = post1['pid']
        time_str = datetime.fromtimestamp(
            post1['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

        if first_line1 == '#DELETED':
            out_list.append(post1)
        elif first_line1 == '#MISSED':
            out_list.append(post1)
        else:
            my_log('{} {} DELETED\n{}'.format(pid, time_str,
                                              post1['text'].strip()))
            post1['text'] = '#DELETED\n' + post1['text']
            out_list.append(get_comment(post1))

        i += 1

    while j < len(post_list2):
        post2 = post_list2[j]
        if post2['text']:
            first_line2 = post2['text'].splitlines()[0]
        else:
            first_line2 = ''

        pid = post2['pid']
        time_str = datetime.fromtimestamp(
            post2['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

        if first_line2 == '#DELETED':
            out_list.append(get_comment(post2))
        elif first_line2 == '#MISSED':
            out_list.append(get_comment(post2))
        else:
            my_log('{} {} REBORN'.format(pid, time_str))
            out_list.append(get_comment(post2))

        j += 1

    write_posts(filename.replace(input_dir2, output_dir), out_list)


if __name__ == '__main__':
    for root, dirs, files in os.walk(input_dir2):
        for file in sorted(files):
            filename = os.path.join(root, file)
            my_log(filename)
            compare_file(filename)
