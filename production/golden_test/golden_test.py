import os
import json
import sys
import itertools
import logger

import nose
from nose.tools import eq_

from production import game
from production import utils


#def read_json(filename):
#    print 'hello'
#    path = os.path.join(utils.get_data_dir(), 'golden_tests', filename)
#    print(path)
#    with open(path) as f:
#        return json.load(f)

#def run_test


def test_something():
    pass
    #data = read_json('a.json')
 #   data
    #eq_(list(itertools.islice(game.lcg(17), 10)),
    #    [0,24107,16552,12125,9427,13152,21440,3383,6873,16117])


if __name__ == '__main__':
    logger.fatal('a')
    print 'a'
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
