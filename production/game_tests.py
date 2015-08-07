import os
import json
import sys
import itertools

import nose
from nose.tools import eq_

from production import game
from production import utils


def smoke_test():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_0.json')
    with open(path) as fin:
        data = json.load(fin)

    g = game.Game(data, data['sourceSeeds'][0])
    str(g)


def test_lcg():
    eq_(list(itertools.islice(game.lcg(17), 10)),
        [0,24107,16552,12125,9427,13152,21440,3383,6873,16117])


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
