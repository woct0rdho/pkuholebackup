#!/usr/bin/python3
# text end with \n\n

import codecs
import filewithlock
import logging
import os
import random
import re
import requests
import signal
import sys
import time
import user_agent
from datetime import date, datetime, timedelta

logging.getLogger().handlers = []
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)


def my_log(s):
    logging.info(s)


def sigint_disabled(signum, frame):
    my_log('SIGINT disabled')


def sigint_handler(signum, frame):
    my_log('SIGINT received')
    signal.signal(signal.SIGINT, sigint_disabled)
    raise KeyboardInterrupt


signal.signal(signal.SIGINT, sigint_handler)


def trim_lines(s):
    return '\n'.join(map(lambda x: ' '.join(x.split()), s.splitlines())) + '\n'


def parse_metadata(line):
    t = line.split()
    return {
        'pid':
        int(t[1]),
        'timestamp':
        datetime.strptime('{} {}'.format(t[2], t[3]),
                          '%Y-%m-%d %H:%M:%S').timestamp(),
        'likenum':
        int(t[4]),
        'reply':
        int(t[5]),
        'text':
        '',
        'comments': []
    }


def parse_comment_metadata(line):
    t = line.split()
    return {
        'cid':
        int(t[1]),
        'timestamp':
        datetime.strptime('{} {}'.format(t[2], t[3]),
                          '%Y-%m-%d %H:%M:%S').timestamp(),
        'text':
        ''
    }


def read_posts(filename):
    with filewithlock.open(filename, 'r', 'utf-8') as f:
        line_list = f.read().splitlines()

    if not line_list:
        return []

    post_list = []
    now_post = parse_metadata(line_list[0])
    now_comment = None
    for line in line_list[1:]:
        if line[:2] == '#p':
            if now_comment:
                now_post['comments'].append(now_comment)
                now_comment = None
            post_list.append(now_post)
            now_post = parse_metadata(line)
        elif line[:2] == '#c':
            if now_comment:
                now_post['comments'].append(now_comment)
            now_comment = parse_comment_metadata(line)
        else:
            if now_comment:
                now_comment['text'] += line + '\n'
            else:
                now_post['text'] += line + '\n'
    if now_comment:
        now_post['comments'].append(now_comment)
    post_list.append(now_post)

    return post_list


def read_posts_dict(filename):
    with filewithlock.open(filename, 'r', 'utf-8') as f:
        line_list = f.read().splitlines()

    if not line_list:
        return {}

    post_dict = {}
    now_post = parse_metadata(line_list[0])
    now_comment = None
    for line in line_list[1:]:
        if line[:2] == '#p':
            if now_comment:
                now_post['comments'].append(now_comment)
                now_comment = None
            if not (post_dict.get(now_post['pid'])
                    and '#MISSED' in now_post['text']):
                post_dict[now_post['pid']] = now_post
            now_post = parse_metadata(line)
        elif line[:2] == '#c':
            if now_comment:
                now_post['comments'].append(now_comment)
            now_comment = parse_comment_metadata(line)
        else:
            if now_comment:
                now_comment['text'] += line + '\n'
            else:
                now_post['text'] += line + '\n'
    if now_comment:
        now_post['comments'].append(now_comment)
    if not (post_dict.get(now_post['pid']) and '#MISSED' in now_post['text']):
        post_dict[now_post['pid']] = now_post

    return post_dict


def post_dict_to_list(post_dict):
    if not post_dict:
        return []

    post_list = []
    last_time = 0
    sort_keys = sorted(post_dict)
    for pid in range(sort_keys[-1], sort_keys[0] - 1, -1):
        if post_dict.get(pid):
            post_list.append(post_dict[pid])
            last_time = post_dict[pid]['timestamp']
        else:
            post_list.append({
                'pid': pid,
                'timestamp': last_time,
                'likenum': -1,
                'reply': -1,
                'text': '#MISSED\n\n',
                'comments': []
            })
    return post_list


def write_posts(filename, posts):
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    with filewithlock.open(filename, 'w', 'utf-8') as g:
        for post in posts:
            g.write('#p {} {} {} {}\n{}'.format(
                post['pid'],
                datetime.fromtimestamp(int(post['timestamp'])).strftime(
                    '%Y-%m-%d %H:%M:%S'), post['likenum'], post['reply'], post[
                        'text']))
            for comment in post['comments']:
                g.write('#c {} {}\n{}'.format(
                    comment['cid'],
                    datetime.fromtimestamp(int(comment['timestamp'])).strftime(
                        '%Y-%m-%d %H:%M:%S'), comment['text']))


def get_comment(post):
    request_success = False
    for retry_count in range(10):
        try:
            r = requests.get(
                'http://www.pkuhelper.com/services/pkuhole/api.php?action=getcomment&pid={}'.
                format(post['pid']),
                headers={'User-Agent': user_agent.generate_user_agent()},
                timeout=5)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            my_log('{}'.format(e))
        else:
            request_success = True
            break
        time.sleep(5 + random.random())
        my_log('Post {} retry {}'.format(post['pid'], retry_count))
    if not request_success:
        raise Exception('Post {} request failed'.format(post['pid']))

    time.sleep(0.5 + random.random() * 0.5)
    r.encoding = 'utf-8'
    try:
        data = r.json()
        r.close()
    except Exception as e:
        my_log('Post {} parse json error: {}'.format(post['pid'], e))
        return post

    if data['code'] != 0:
        my_log('Post {} get comment error: {}'.format(post['pid'], data))
        return post

    for comment in data['data']:
        post['comments'].append({
            'cid': int(comment['cid']),
            'timestamp': int(comment['timestamp']),
            'text': trim_lines(comment['text']) + '\n'
        })
    post['reply'] = len(post['comments'])

    return post


def clean_comment(post):
    post['reply'] = 0
    return post


def force_remove(filename):
    os.remove(filename)
    filewithlock.release_lock(filename + '.readlock')
    filewithlock.release_lock(filename + '.writelock')
