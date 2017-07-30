#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
archive_folder = os.path.join(cdname, 'archive', '201707')

if __name__ == '__main__':
    for root, dirs, files in os.walk(archive_folder):
        for file in sorted(files):
            post_list = list(reversed(read_posts(os.path.join(root, file))))
            if not post_list:
                continue
            last_pid = post_list[0]['pid']

            for post in post_list:
                pid = post['pid']
                time_str = datetime.fromtimestamp(
                    int(post['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
                if pid > last_pid and pid < last_pid + 100:
                    if pid > last_pid + 1:
                        for i in range(last_pid + 1, pid):
                            print(i, time_str, 'N')
                    last_pid = pid
                if '#DELETED' in post['text']:
                    print(pid, time_str, 'D')
                if '#MISSED' in post['text']:
                    print(pid, time_str, 'M')
                if post['reply'] >= 0 and post['reply'] != len(
                        post['comments']):
                    print(pid, time_str, 'R')
