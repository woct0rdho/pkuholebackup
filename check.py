#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')

if __name__ == '__main__':
    post_list = list(reversed(read_posts(filename)))
    last_pid = post_list[0]['pid']

    for post in post_list:
        pid = post['pid']
        if pid > last_pid and pid < last_pid + 100:
            if pid > last_pid + 1:
                for i in range(last_pid + 1, pid):
                    print(i,
                          datetime.fromtimestamp(int(post['timestamp']))
                          .strftime('%Y-%m-%d %H:%M:%S'))
            last_pid = pid
