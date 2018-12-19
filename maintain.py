#!/usr/bin/python3
#
# DELETED posts must have latest comments

from datetime import date, datetime, timedelta

from update import filename as update_filename
from utils import (
    get_page,
    my_log,
    post_dict_to_list,
    read_posts,
)
from utils import get_comment as _get_comment
from utils import write_posts as _write_posts

day_count = 2
default_reply = -1


def _get_comment_fake(post):
    return post


get_comment = _get_comment_fake


def _write_posts_fake(filename, posts):
    return


write_posts = _write_posts


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
                my_log('{} {} more replies\n{}'.format(pid, time_str,
                                                       post1['text'].strip()))
                out_list.append(post1)
            else:
                out_list.append(post1)


def compare_posts(post_list1, post_list2):
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
                my_log('{} {} DELETED YN\n{}'.format(pid, time_str,
                                                     post1['text'].strip()))
                post1['text'] = '#DELETED\n' + post1['text']
                out_list.append(_get_comment(post1))

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
                my_log('{} {} REBORN NY'.format(pid, time_str))
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
                    my_log('{} {} REBORN DY'.format(pid, time_str))
                    out_list.append(get_comment(post2))
            elif first_line1 == '#MISSED':
                if first_line2 == '#DELETED':
                    my_log('{} {} FILLED MD'.format(pid, time_str))
                    out_list.append(get_comment(post2))
                elif first_line2 == '#MISSED':
                    out_list.append(post1)
                else:
                    my_log('{} {} REBORN MY'.format(pid, time_str))
                    out_list.append(get_comment(post2))
            else:
                if first_line2 == '#DELETED':
                    my_log('{} {} DELETED YD\n{}'.format(
                        pid, time_str, post1['text'].strip()))
                    post1['text'] = '#DELETED\n' + post1['text']
                    out_list.append(_get_comment(post1))
                elif first_line2 == '#MISSED':
                    my_log('{} {} DELETED YM\n{}'.format(
                        pid, time_str, post1['text'].strip()))
                    post1['text'] = '#DELETED\n' + post1['text']
                    out_list.append(_get_comment(post1))
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
            my_log('{} {} DELETED YNE\n{}'.format(pid, time_str,
                                                  post1['text'].strip()))
            post1['text'] = '#DELETED\n' + post1['text']
            out_list.append(_get_comment(post1))

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
            my_log('{} {} REBORN NYE'.format(pid, time_str))
            out_list.append(get_comment(post2))

        j += 1

    return out_list


def compare_file(in_filename1, in_filename2, out_filename):
    post_list1 = read_posts(in_filename1)
    post_list2 = read_posts(in_filename2)
    out_list = compare_posts(post_list1, post_list2)
    write_posts(out_filename, out_list)


if __name__ == '__main__':
    out_date = date.today() - timedelta(day_count)
    max_timestamp = int(
        datetime.combine(out_date + timedelta(1),
                         datetime.min.time()).timestamp())

    my_log('Begin read posts')
    post_list = read_posts(update_filename)
    my_log('End read posts')

    post_list_old = [
        post for post in post_list if post['timestamp'] < max_timestamp
    ]
    post_list = [
        post for post in post_list if post['timestamp'] >= max_timestamp
    ]

    if post_list:
        min_pid = post_list[-1]['pid'] - 1
    else:
        # May change
        min_pid = 32859
    my_log('Min pid: {}'.format(min_pid))

    post_dict_new = {}
    try:
        page = 1
        while True:
            my_log('Page {}'.format(page))
            finished = get_page(post_dict_new, page, min_pid)
            if finished:
                break
            page += 1
    except Exception as e:
        my_log('{}'.format(e))
        exit()

    out_list = compare_posts(post_list, post_dict_to_list(post_dict_new))

    my_log('Begin write posts')
    write_posts(update_filename, out_list + post_list_old)
    my_log('End write posts')
