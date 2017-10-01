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

    my_log('Begin read posts')
    post_dict = read_posts_dict(filename)
    my_log('End read posts')

    if post_dict:
        min_pid = sorted(post_dict)[-1]
    else:
        min_pid = 32860  # May change
    my_log('Min pid: {}'.format(min_pid))

    my_log('Begin write bak')
    write_posts(filename_bak, post_dict_to_list(post_dict))
    my_log('End write bak')

    finish = False
    page = 1
    while True:
        my_log('Page {}'.format(page))

        request_success = False
        for retry_count in range(10):
            try:
                r = requests.get(
                    'http://www.pkuhelper.com/services/pkuhole/api.php?action=getlist&p={}'.
                    format(page),
                    headers={'User-Agent': user_agent.generate_user_agent()},
                    timeout=5)
            except CtrlCError:
                break
            except Exception as e:
                print(e)
            else:
                request_success = True
                break
            time.sleep(5 + random.random())
            my_log('Page {} retry {}'.format(page, retry_count))
        if not request_success:
            my_log('Request error')
            write_posts(filename, post_dict_to_list(post_dict))
            exit()

        time.sleep(0.5 + random.random() * 0.5)
        r.encoding = 'utf-8'
        try:
            data = r.json()
            r.close()
        except Exception as e:
            my_log('Parse json error: {}'.format(e))
            write_posts(filename, post_dict_to_list(post_dict))
            exit()

        if not data.get('data'):
            # Finished
            break

        for post in data['data']:
            pid = int(post['pid'])
            if pid <= min_pid:
                finish = True
                break

            post_dict[pid] = {
                'pid': pid,
                'timestamp': int(post['timestamp']),
                'likenum': int(post['likenum']),
                'reply': -1,
                'text': trim_lines(post['text']) + '\n',
                'comments': []
            }

        if finish:
            break

        page += 1

    my_log('Begin write posts')
    write_posts(filename, post_dict_to_list(post_dict))
    my_log('End write posts')
