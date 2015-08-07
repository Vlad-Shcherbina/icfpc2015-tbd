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


def get_2x2_game():
    path = os.path.join(utils.get_data_dir(), 'test_problems/2x2.json')
    with open(path) as fin:
        data = json.load(fin)

    return game.Game(data, seed=0)


def test_blockage():
    g = get_2x2_game()
    eq_(g.remaining_units, 9)

    g._execute_command(game.MOVE_SE)
    g._execute_command(game.MOVE_W)

    eq_(g.remaining_units, 8)

    try:
        g._execute_command(game.MOVE_SE)
        assert False
    except game.GameEnded as e:
        assert "can't spawn" in e.reason
        eq_(e.total_score, 2)


def test_row_collapse():
    g = get_2x2_game()

    eq_(g.remaining_units, 9)

    g._execute_command(game.MOVE_SE)
    g._execute_command(game.MOVE_E)
    g._execute_command(game.MOVE_E)
    eq_(g.remaining_units, 8)

    g._execute_command(game.MOVE_SE)
    g._execute_command(game.MOVE_SE)
    eq_(g.remaining_units, 7)

    eq_(g.filled, set())

    eq_(g.move_score, 102)


def test_power_score():
    g = get_2x2_game()

    g.execute_string('Ei!')

    try:
        while True:
            g._execute_command(game.MOVE_SE)
        assert False
    except game.GameEnded as e:
        eq_(e.power_score, 300 + 2 * 3 * 1)


def test_lcg():
    eq_(list(itertools.islice(game.lcg(17), 10)),
        [0,24107,16552,12125,9427,13152,21440,3383,6873,16117])


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
