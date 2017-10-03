#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')
archive_folder = os.path.join(cdname, 'archive')
archive_basename = 'pkuhole'
archive_extname = '.txt'
day_count = 2

if __name__ == '__main__':
    out_date = datetime.combine(date.today(),
                                datetime.min.time()) - timedelta(day_count)
    archive_filename = os.path.join(
        archive_folder,
        out_date.strftime('%Y%m'),
        archive_basename + out_date.strftime('%Y%m%d') + archive_extname)
    if os.path.exists(archive_filename):
        my_log('Archive file exists')
        exit()

    my_log('Archive {}'.format(archive_filename))
    try:
        max_timestamp = int((out_date + timedelta(1)).timestamp())
        write_posts(archive_filename,
                    map(get_comment,
                        filter(lambda post: post['timestamp'] < max_timestamp,
                               read_posts(filename))))
    except Exception as e:
        my_log('Error: {}'.format(e))
        force_remove(archive_filename)
    else:
        with codecs.open(os.path.join(cdname, 'split.flag'), 'w',
                         'utf-8') as g:
            g.write(str(max_timestamp))
