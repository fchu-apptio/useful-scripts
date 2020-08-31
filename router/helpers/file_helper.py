import os


class FileArg(object):
    def __call__(self, value):
        if os.path.exists(value):
            return value
        else:
            raise KeyError('File {} does not exist'.format(value, ','.join(value)))
