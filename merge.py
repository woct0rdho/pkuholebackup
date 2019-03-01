#!/usr/bin/python3

import os

from utils import my_log, read_posts, write_posts

cdname = os.path.dirname(__file__)
in_filename1 = os.path.join(cdname, 'pkuhole.txt')
in_filename2 = os.path.join(cdname, 'pkuhole2.txt')
out_filename = os.path.join(cdname, 'pkuholeout.txt')


# True: keep post1, False: keep post2
def cmp(post1, post2):
    if post1['text']:
        first_line1 = post1['text'].splitlines()[0]
    else:
        first_line1 = ''
    if post2['text']:
        first_line2 = post2['text'].splitlines()[0]
    else:
        first_line2 = ''

    if first_line2 == '#MISSED':
        return True
    elif first_line1 == '#MISSED':
        return False
    elif first_line1 == '#DELETED':
        return True
    elif first_line2 == '#DELETED':
        return False
    elif post1['reply'] > post2['reply']:
        return True
    else:
        return False


def merge_file(in_filename1, in_filename2, out_filename):
    post_list1 = read_posts(in_filename1)
    post_list2 = read_posts(in_filename2)
    out_list = []
    i = 0
    j = 0
    while i < len(post_list1) and j < len(post_list2):
        if post_list1[i]['pid'] > post_list2[j]['pid']:
            out_list.append(post_list1[i])
            i += 1
        elif post_list1[i]['pid'] < post_list2[j]['pid']:
            out_list.append(post_list2[j])
            j += 1
        else:
            if cmp(post_list1[i], post_list2[j]):
                out_list.append(post_list1[i])
            else:
                out_list.append(post_list2[j])
            if len(post_list1[i]['comments']) > len(post_list2[j]['comments']):
                out_list[-1]['comments'] = post_list1[i]['comments']
            else:
                out_list[-1]['comments'] = post_list2[j]['comments']
            i += 1
            j += 1
    out_list += post_list1[i:]
    out_list += post_list2[j:]
    write_posts(out_filename, out_list)


if __name__ == '__main__':
    merge_file(in_filename1, in_filename2, out_filename)
