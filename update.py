#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
filename = os.path.join(cdname, 'pkuhole.txt')
filename_bak = os.path.join(cdname, 'pkuholebak.txt')


def internet_on():
    try:
        requests.get('https://www.baidu.com', timeout=5)
    except:
        return False
    return True


if __name__ == '__main__':
    if not internet_on():
        my_log('No internet')
        exit()

    last_post_list = read_posts(filename)
    if len(last_post_list) == 0:
        my_log('Error: empty file')
        exit()

    write_posts(filename_bak, last_post_list)
    min_pid = last_post_list[0]['pid']
    my_log('Last pid: {}'.format(min_pid))

    post_list = []
    finish = False
    page = 1
    last_pid = -1
    while True:
        my_log('Page {}'.format(page))
        try:
            r = requests.get(
                'http://www.pkuhelper.com/services/pkuhole/api.php?action=getlist&p={}'.
                format(page),
                headers={'User-Agent': user_agent.generate_user_agent()},
                timeout=5)
        except Exception as e:
            my_log('Request error: {}'.format(e))
            exit()

        r.encoding = 'utf-8'
        try:
            data = r.json()
            r.close()
        except Exception as e:
            my_log('Parse json error: {}'.format(e))
            exit()
        time.sleep(0.5 + random.random() * 0.5)

        for post in data['data']:
            pid = int(post['pid'])
            if pid <= min_pid:
                finish = True
                break
            if last_pid != -1 and pid < last_pid - 1:
                my_log('Mis {} {}'.format(pid, last_pid))
                for i in range(last_pid - 1, pid, -1):
                    post_list.append({
                        'pid': i,
                        'timestamp': int(post['timestamp']),
                        'likenum': 0,
                        'reply': -1,
                        'text': '#MISSED\n\n',
                        'comments': []
                    })
            last_pid = pid
            post_list.append({
                'pid': pid,
                'timestamp': int(post['timestamp']),
                'likenum': int(post['likenum']),
                'reply': 0,
                'text': post['text'] + '\n\n',
                'comments': []
            })

        if finish:
            break
        page += 1

    my_log('Output started')
    write_posts(filename, post_list + last_post_list)
