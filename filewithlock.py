import os
import time
from contextlib import contextmanager

wait_lock_time = 0.001


def wait_lock(filename):
    while os.path.exists(filename):
        time.sleep(wait_lock_time)


def acquire_lock(filename):
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.exists(filename):
        open(filename, 'w').close()


def release_lock(filename):
    if os.path.exists(filename):
        os.remove(filename)


@contextmanager
def open_with_lock(filename, mode='r', **kwargs):
    if mode == 'r':
        wait_lock(filename + '.readlock')
        acquire_lock(filename + '.writelock')
    elif mode == 'w':
        wait_lock(filename + '.writelock')
        acquire_lock(filename + '.readlock')
        acquire_lock(filename + '.writelock')
    else:
        raise ValueError('invalid mode: \'{}\''.format(mode))

    try:
        with open(filename, mode, **kwargs) as f:
            yield f
    finally:
        if mode == 'r':
            release_lock(filename + '.writelock')
        elif mode == 'w':
            release_lock(filename + '.readlock')
            release_lock(filename + '.writelock')
