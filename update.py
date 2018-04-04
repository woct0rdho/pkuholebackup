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

    if os.path.exists(os.path.join(cdname, 'update.flag')):
        my_log('Update is already running')
        exit()

    with codecs.open(os.path.join(cdname, 'update.flag'), 'w', 'utf-8') as g:
        g.write(str(os.getpid()))

    my_log('Begin read posts')
    post_dict = read_posts_dict(filename)
    my_log('End read posts')

    my_log('Begin write bak')
    write_posts(filename_bak, post_dict_to_list(post_dict))
    my_log('End write bak')

    page = 1

    if page == 1 and post_dict:
        min_pid = sorted(post_dict)[-1]
    else:
        min_pid = 11320  # May change
    my_log('Min pid: {}'.format(min_pid))

    try:
        while True:
            my_log('Page {}'.format(page))

            if page % 100 == 0:
                my_log('Begin write posts')
                write_posts(filename, post_dict_to_list(post_dict))
                my_log('End write posts')

            request_success = False
            for retry_count in range(10):
                try:
                    r = requests.get(
                        'http://www.pkuhelper.com/services/pkuhole/api.php?action=getlist&p={}'.
                        format(page),
                        headers={
                            'User-Agent': user_agent.generate_user_agent()
                        },
                        timeout=5)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except Exception as e:
                    my_log('{}'.format(e))
                else:
                    request_success = True
                    break
                time.sleep(5 + random.random())
                my_log('Page {} retry {}'.format(page, retry_count))
            if not request_success:
                raise Exception('Request error')

            time.sleep(0.5 + random.random() * 0.5)
            r.encoding = 'utf-8'
            try:
                data = r.json()
            except Exception as e:
                raise e

            if not data.get('data'):
                # Finished
                break

            finish = False
            for post in data['data']:
                pid = int(post['pid'])
                if pid <= min_pid:
                    finish = True
                    break

                post_dict[pid] = {
                    'pid': pid,
                    'timestamp': int(post['timestamp']),
                    'likenum': int(post['likenum']),
                    'reply': int(post['reply']),
                    'text': trim_lines(post['text']) + '\n',
                    'comments': []
                }

            if finish:
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

        with codecs.open(os.path.join(cdname, 'split.flag'), 'r',
                         'utf-8') as f:
            max_timestamp = int(f.read())

        my_log('Begin write posts')
        write_posts(filename,
                    filter(lambda post: post['timestamp'] >= max_timestamp,
                           post_dict_to_list(post_dict)))
        my_log('End write posts')

        os.remove(os.path.join(cdname, 'split.flag'))
    else:
        my_log('Begin write posts')
        write_posts(filename, post_dict_to_list(post_dict))
        my_log('End write posts')

    os.remove(os.path.join(cdname, 'update.flag'))
