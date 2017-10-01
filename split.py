#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')
archive_folder = os.path.join(cdname, 'archive')
archive_basename = 'pkuhole'
archive_extname = '.txt'
day_count = 2

if __name__ == '__main__':
    min_date = datetime.combine(date.today(),
                                datetime.min.time()) - timedelta(day_count)
    min_timestamp = (datetime.combine(date.today(), datetime.min.time()) -
                     timedelta(day_count - 1)).timestamp()
    archive_filename = os.path.join(
        archive_folder,
        min_date.strftime('%Y%m'),
        archive_basename + min_date.strftime('%Y%m%d') + archive_extname)
    if os.path.exists(archive_filename):
        my_log('Archive file exists')
        exit()

    post_list = read_posts(filename)
    out_list1 = []
    out_list2 = []
    for post in post_list:
        if post['timestamp'] >= min_timestamp:
            out_list1.append(post)
        else:
            out_list2.append(post)

    write_posts(filename, out_list1)
    my_log('Archive {}'.format(archive_filename))
    try:
        write_posts(archive_filename, map(get_comment, out_list2))
    except Exception as e:
        my_log('Error: {}'.format(e))
        write_posts(filename, out_list1 + out_list2)
        force_remove(archive_filename)
