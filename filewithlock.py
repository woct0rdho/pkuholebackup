import builtins
import os
import time

wait_lock_time = 0.001


def wait_lock(filename):
    while os.path.exists(filename):
        time.sleep(wait_lock_time)


def add_lock(filename):
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.exists(filename):
        builtins.open(filename, 'w').close()


def release_lock(filename):
    if os.path.exists(filename):
        os.remove(filename)


class FileWithLock(object):
    def __init__(self, filename, mode='r', **kwargs):
        self.filename = filename
        self.mode = mode
        self.kwargs = kwargs
        self.file = None

    def __enter__(self):
        if self.mode == 'r':
            if not os.path.exists(self.filename):
                builtins.open(self.filename, 'w').close()
            wait_lock(self.filename + '.readlock')
            add_lock(self.filename + '.writelock')
        elif self.mode == 'w':
            wait_lock(self.filename + '.writelock')
            add_lock(self.filename + '.readlock')
            add_lock(self.filename + '.writelock')
        else:
            raise ValueError('invalid mode: \'{}\''.format(self.mode))
        self.file = builtins.open(self.filename, self.mode, **self.kwargs)
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.mode == 'r':
            release_lock(self.filename + '.writelock')
        elif self.mode == 'w':
            release_lock(self.filename + '.readlock')
            release_lock(self.filename + '.writelock')
        else:
            raise ValueError('invalid mode: \'{}\''.format(self.mode))
        self.file.close()


def open(filename, mode='r', **kwargs):
    return FileWithLock(filename, mode, **kwargs)
