#!/usr/bin/python3

import os

from utils import (
    get_page,
    internet_on,
    my_log,
    post_dict_to_list,
    read_posts_dict,
    write_posts,
)

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')
filename_bak = os.path.join(cdname, 'pkuholebak.txt')

if __name__ == '__main__':
    if not internet_on():
        my_log('No internet')
        exit()

    if os.path.exists(os.path.join(cdname, 'update.flag')):
        my_log('Update is already running')
        exit()

    with open(os.path.join(cdname, 'update.flag'), 'w', encoding='utf-8') as g:
        g.write(str(os.getpid()))

    my_log('Begin read posts')
    post_dict = read_posts_dict(filename)
    my_log('End read posts')

    my_log('Begin write bak')
    write_posts(filename_bak, post_dict_to_list(post_dict))
    my_log('End write bak')

    if post_dict:
        min_pid = max(post_dict)
    else:
        # May change
        min_pid = 32859
    my_log('Min pid: {}'.format(min_pid))

    try:
        page = 1
        while True:
            my_log('Page {}'.format(page))

            if page % 100 == 0:
                my_log('Begin write posts')
                write_posts(filename, post_dict_to_list(post_dict))
                my_log('End write posts')

            finished = get_page(post_dict, page, min_pid)
            if finished:
                break

            page += 1
    except Exception as e:
        my_log('{}'.format(e))

        my_log('Begin write posts at error')
        write_posts(filename, post_dict_to_list(post_dict))
        my_log('End write posts at error')

        os.remove(os.path.join(cdname, 'update.flag'))
        exit()

    if os.path.exists(os.path.join(cdname, 'split.flag')):
        my_log('split.flag found')

        with open(
                os.path.join(cdname, 'split.flag'), 'r',
                encoding='utf-8') as f:
            max_timestamp = int(f.read())

        my_log('Begin write posts')
        write_posts(filename, [
            post for post in post_dict_to_list(post_dict)
            if post['timestamp'] >= max_timestamp
        ])
        my_log('End write posts')

        os.remove(os.path.join(cdname, 'split.flag'))
    else:
        my_log('Begin write posts')
        write_posts(filename, post_dict_to_list(post_dict))
        my_log('End write posts')

    os.remove(os.path.join(cdname, 'update.flag'))
