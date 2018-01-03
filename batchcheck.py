#!/usr/bin/python3

from check import *
from utils import *

cdname = os.path.dirname(__file__)
archive_folder = os.path.join(cdname, 'archive', '201801')

if __name__ == '__main__':
    last_pid = None
    for root, dirs, files in os.walk(archive_folder):
        for file in sorted(files):
            oldest_pid, newest_pid = check_file(os.path.join(root, file))

            # Check missed posts between files
            if oldest_pid:
                if (last_pid and oldest_pid > last_pid + 1
                        and oldest_pid < last_pid + max_missed_pid):
                    for i in range(last_pid + 1, oldest_pid):
                        print(i, file, 'N')
                last_pid = oldest_pid
