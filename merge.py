#!/usr/bin/python3

from utils import *

cdname = os.path.dirname(__file__)
input_folder1 = os.path.join(cdname, 'archive')
input_folder2 = os.path.join(cdname, 'archive2')
output_folder = os.path.join(cdname, 'archive')


def merge_file(filename):
    post_list1 = parse_file(os.path.join(input_folder1, filename))
    post_list2 = parse_file(os.path.join(input_folder2, filename))
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
        elif post_list1[i]['pid'] == post_list2[j]['pid']:
            if post_list1[i]['reply'] > post_list2[j]['reply']:
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
    write_posts(os.path.join(output_folder, file), out_list)


if __name__ == '__main__':
    for root, dirs, files in os.walk(input_folder2):
        for file in sorted(files):
            my_log(file)
            merge_file(file)
