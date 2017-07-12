#!/usr/bin/python3
# post和comment的text以\n\n结尾

import codecs
import logging
import os
import random
import re
import requests
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


def parse_metadata_old(line):
    t = line.split()
    return {
        'pid':
        int(t[0]),
        'timestamp':
        datetime.strptime('{} {}'.format(t[1], t[2]),
                          '%Y-%m-%d %H:%M:%S').timestamp(),
        'likenum':
        int(t[3]),
        'reply':
        int(t[4]),
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


def check_lock(filename):
    while os.path.exists(filename):
        time.sleep(0.01)


def add_lock(filename):
    if not os.path.exists(filename):
        open(filename, 'w').close()


def release_lock(filename):
    if os.path.exists(filename):
        os.remove(filename)


def read_posts(filename):
    check_lock(filename + '.readlock')
    add_lock(filename + '.writelock')
    f = codecs.open(filename, 'r', 'utf-8')
    line_list = f.read().splitlines()
    f.close()
    release_lock(filename + '.writelock')

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


def read_posts_old(filename):
    f = codecs.open(filename, 'r', 'utf-8')
    line_list = f.read().splitlines()
    f.close()
    post_list = []
    now_post = parse_metadata_old(line_list[0])
    for line in line_list[1:]:
        if re.compile(
                '[0-9]+ [0-9]+-[0-9]+-[0-9]+ [0-9]+:[0-9]+:[0-9]+ -?[0-9]+ -?[0-9]+'
        ).fullmatch(line):
            if len(post_list) > 2 and now_post['pid'] == post_list[-2]['pid']:
                # 检测顺序错误的树洞
                my_log('Rec {}'.format(now_post['pid']))
                post_list[-2] = now_post
            elif len(post_list) > 0 and now_post['pid'] == post_list[-1]['pid']:
                # 检测重复的树洞
                my_log('Dup {}'.format(now_post['pid']))
            elif len(post_list
                     ) > 0 and now_post['pid'] != post_list[-1]['pid'] - 1:
                # 检测缺少的树洞
                # 目前没有检测第一条树洞与上个文件的最后一条之间是否有缺少
                my_log(
                    'Mis {} {}'.format(now_post['pid'], post_list[-1]['pid']))
                for pid in range(post_list[-1]['pid'] - 1, now_post['pid'],
                                 -1):
                    post_list.append({
                        'pid': pid,
                        'timestamp': now_post['timestamp'],
                        'likenum': 0,
                        'reply': -1,
                        'text': '#MISSED\n\n',
                        'comments': []
                    })
                post_list.append(now_post)
            else:
                post_list.append(now_post)
            now_post = parse_metadata_old(line)
        else:
            now_post['text'] += line + '\n'
    if len(post_list) > 2 and now_post['pid'] == post_list[-2]['pid']:
        # 检测顺序错误的树洞
        my_log('Rec {}'.format(now_post['pid']))
        post_list[-2] = now_post
    elif len(post_list) > 0 and now_post['pid'] == post_list[-1]['pid']:
        # 检测重复的树洞
        my_log('Dup {}'.format(now_post['pid']))
    elif len(post_list) > 0 and now_post['pid'] != post_list[-1]['pid'] - 1:
        # 检测缺少的树洞
        # 目前没有检测第一条树洞与上个文件的最后一条之间是否有缺少
        my_log('Mis {} {}'.format(now_post['pid'], post_list[-1]['pid']))
        for pid in range(post_list[-1]['pid'] - 1, now_post['pid'], -1):
            post_list.append({
                'pid': pid,
                'timestamp': now_post['timestamp'],
                'likenum': 0,
                'reply': -1,
                'text': '#MISSED\n\n',
                'comments': []
            })
        post_list.append(now_post)
    else:
        post_list.append(now_post)
    return post_list


def write_posts(filename, posts):
    check_lock(filename + '.writelock')
    add_lock(filename + '.readlock')
    add_lock(filename + '.writelock')
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    g = codecs.open(filename, 'w', 'utf-8')
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
    g.close()
    release_lock(filename + '.readlock')
    release_lock(filename + '.writelock')


def get_comment(post):
    request_success = False
    # 尝试连接10次
    for retry_count in range(10):
        try:
            r = requests.get(
                'http://www.pkuhelper.com/services/pkuhole/api.php?action=getcomment&pid={}'.
                format(post['pid']),
                headers={'User-Agent': user_agent.generate_user_agent()},
                timeout=5)
        except Exception as e:
            pass
        else:
            request_success = True
            break
        time.sleep(2 + random.random())
        my_log('Post {} retry {}'.format(post['pid'], retry_count))
    if not request_success:
        my_log('Post {} request failed'.format(post['pid']))
        return post

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
            'text': comment['text'] + '\n\n'
        })
    post['reply'] = len(post['comments'])
    return post


def clean_comment(post):
    post['reply'] = 0
    return post
