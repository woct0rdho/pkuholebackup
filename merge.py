#!/usr/bin/python3

import os

from utils import my_log, read_posts, write_posts

cdname = os.path.dirname(__file__)
# 1: old, 2: new
input_dir1 = os.path.join(cdname, 'archive')
input_dir2 = os.path.join(cdname, 'archivebak')
output_dir = os.path.join(cdname, 'archive')


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


def merge_file(filename):
    post_list1 = read_posts(filename.replace(input_dir2, input_dir1))
    post_list2 = read_posts(filename)
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
            i += 1
            j += 1
    out_list += post_list1[i:]
    out_list += post_list2[j:]
    write_posts(filename.replace(input_dir2, output_dir), out_list)


if __name__ == '__main__':
    for root, dirs, files in os.walk(input_dir2):
        for file in sorted(files):
            filename = os.path.join(root, file)
            my_log(filename)
            merge_file(filename)
