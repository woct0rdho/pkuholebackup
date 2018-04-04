import codecs
import os
import time


def wait_lock(filename):
    while os.path.exists(filename):
        time.sleep(0.001)


def add_lock(filename):
    dirname = os.path.dirname(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.exists(filename):
        codecs.open(filename, 'w', 'utf-8').close()


def release_lock(filename):
    if os.path.exists(filename):
        os.remove(filename)


class FileWithLock(object):
    def __init__(self, filename, mode, encoding, errors, buffering):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.errors = errors
        self.buffering = buffering
        self.file = None

    def __enter__(self):
        if self.mode == 'r':
            if not os.path.exists(self.filename):
                codecs.open(self.filename, 'w', 'utf-8').close()
            wait_lock(self.filename + '.readlock')
            add_lock(self.filename + '.writelock')
        elif self.mode == 'w':
            wait_lock(self.filename + '.writelock')
            add_lock(self.filename + '.readlock')
            add_lock(self.filename + '.writelock')
        else:
            raise ValueError('invalid mode: \'{}\''.format(self.mode))
        self.file = codecs.open(self.filename, self.mode, self.encoding,
                                self.errors, self.buffering)
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


def open(filename, mode='r', encoding='utf-8', errors='strict', buffering=1):
    return FileWithLock(filename, mode, encoding, errors, buffering)
