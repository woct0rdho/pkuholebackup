#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')

max_missed_pid = 100


def check_file(filename):
    post_list = list(reversed(read_posts(filename)))
    if not post_list:
        return None, None

    last_pid = None
    for post in post_list:
        pid = post['pid']
        time_str = datetime.fromtimestamp(int(
            post['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
        if last_pid and pid > last_pid + 1 and pid < last_pid + max_missed_pid:
            for i in range(last_pid + 1, pid):
                print(i, time_str, 'N')
        last_pid = pid
        first_line = post['text'].splitlines()[0]
        if first_line == '#DELETED':
            print(pid, time_str, 'D')
        if first_line == '#MISSED':
            print(pid, time_str, 'M')
        if post['reply'] >= 0 and post['reply'] != len(post['comments']):
            print(pid, time_str, 'R')

    oldest_pid = post_list[0]['pid']
    newest_pid = post_list[-1]['pid']
    return oldest_pid, newest_pid


if __name__ == '__main__':
    check_file(filename)
