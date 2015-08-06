import os

from production import utils


def load_example():
    """
    >>> load_example()
    'hello, world!'
    """
    with open(os.path.join(utils.get_data_dir(), 'example.txt')) as fin:
        return fin.read().rstrip()
