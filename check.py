#!/usr/bin/python3

import os
from datetime import datetime

from utils import my_log, read_posts

max_missed_pid = 100
default_reply = -1

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')


def check_file(filename):
    post_list = list(reversed(read_posts(filename)))
    if not post_list:
        return None, None

    last_pid = None
    for post in post_list:
        pid = post['pid']
        time_str = datetime.fromtimestamp(
            post['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        if last_pid and pid > last_pid + 1 and pid < last_pid + max_missed_pid:
            for i in range(last_pid + 1, pid):
                my_log('{} {} really MISSED'.format(i, time_str))
        last_pid = pid
        first_line = post['text'].splitlines()[0]
        if first_line == '#DELETED':
            my_log('{} {} DELETED'.format(pid, time_str))
        if first_line == '#MISSED':
            my_log('{} {} MISSED'.format(pid, time_str))
        if default_reply is not False and (
                post['reply'] != default_reply
                and post['reply'] != len(post['comments'])):
            my_log('{} {} replies not match {} {}'.format(
                pid, time_str, post['reply'], len(post['comments'])))

    oldest_pid = post_list[0]['pid']
    newest_pid = post_list[-1]['pid']
    return oldest_pid, newest_pid


if __name__ == '__main__':
    default_reply = False
    check_file(filename)
