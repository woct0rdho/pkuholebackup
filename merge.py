#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
input_folder1 = os.path.join(cdname, 'archive')
input_folder2 = os.path.join(cdname, 'archive2')
output_folder = os.path.join(cdname, 'archive')


# True: keep post1, False: keep post2
def cmp(post1, post2):
    if '#MISSED' in post2['text']:
        return True
    if '#MISSED' in post1['text']:
        return False
    if '#DELETED' in post1['text']:
        return True
    if '#DELETED' in post2['text']:
        return False
    if post1['reply'] > post2['reply']:
        return True
    return False


def merge_file(filename):
    post_list1 = read_posts(filename.replace(input_folder2, input_folder1))
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
    while i < len(post_list1):
        out_list.append(post_list1[i])
        i += 1
    while j < len(post_list2):
        out_list.append(post_list2[j])
        j += 1
    write_posts(filename.replace(input_folder2, output_folder), out_list)


if __name__ == '__main__':
    for root, dirs, files in os.walk(input_folder2):
        for file in sorted(files):
            filename = os.path.join(root, file)
            my_log(filename)
            merge_file(filename)
