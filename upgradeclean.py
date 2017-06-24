#!/usr/bin/python3

import os
from utils import *

cdname = os.path.dirname(__file__)

write_posts(
    os.path.join(cdname, 'pkuhole.txt'),
    map(clean_comment, read_posts_old(os.path.join(cdname, 'pkuholeold.txt'))))
