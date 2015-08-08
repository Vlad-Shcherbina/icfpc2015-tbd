import os
import json
import sys
import itertools

import nose
from nose.tools import eq_

from production import game
from production import utils
from production.interfaces import CHARS_BY_COMMAND, Action


def smoke_test():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_0.json')
    with open(path) as fin:
        data = json.load(fin)

    g = game.Game(data, data['sourceSeeds'][0])
    str(g)


def smoke_test_with_nonempty_board():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_2.json')
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

    g.execute_char(CHARS_BY_COMMAND[Action.se][0])
    g.execute_char(CHARS_BY_COMMAND[Action.w][0])

    eq_(g.remaining_units, 8)

    try:
        g.execute_char(CHARS_BY_COMMAND[Action.se][0])
        assert False
    except game.GameEnded as e:
        assert "can't spawn" in e.reason
        eq_(e.total_score, 2)


def test_row_collapse():
    g = get_2x2_game()

    eq_(g.remaining_units, 9)

    g.execute_char(CHARS_BY_COMMAND[Action.se][0])
    g.execute_char(CHARS_BY_COMMAND[Action.e][0])
    g.execute_char(CHARS_BY_COMMAND[Action.e][0])
    eq_(g.remaining_units, 8)

    g.execute_char(CHARS_BY_COMMAND[Action.se][0])
    g.execute_char(CHARS_BY_COMMAND[Action.se][0])
    eq_(g.remaining_units, 7)

    eq_(g.filled, set())

    eq_(g.move_score, 102)


def test_turn_leading_to_repetition():
    g = get_2x2_game()

    try:
        g.execute_string('d')
        print(g)
    except game.GameEnded as e:
        assert 'placement repeated' in e.reason


def test_unit_exhaustion():
    g = get_2x2_game()
    n = 10

    n -= 1
    eq_(g.remaining_units, n)

    try:
        for _ in range(5):
            g.execute_char(CHARS_BY_COMMAND[Action.se][0])
            g.execute_char(CHARS_BY_COMMAND[Action.e][0])
            g.execute_char(CHARS_BY_COMMAND[Action.e][0])
            n -= 1
            eq_(g.remaining_units, n)

            g.execute_char(CHARS_BY_COMMAND[Action.se][0])
            g.execute_char(CHARS_BY_COMMAND[Action.se][0])
            n -= 1
            eq_(g.remaining_units, n)

    except game.GameEnded as e:
        eq_(n, 0)
        assert 'no more units' in e.reason
        # We used all ten 1-cell units, and we collapsed 5 rows.
        eq_(e.move_score, 510)
    else:
        assert False


def test_power_score():
    g = get_2x2_game()

    g.execute_string('Ei!')

    try:
        while True:
            g.execute_char(CHARS_BY_COMMAND[Action.se][0])
    except game.GameEnded as e:
        eq_(e.power_score, 300 + 2 * 3 * 1)
    else:
        assert False


def test_lcg():
    eq_(list(itertools.islice(game.lcg(17), 10)),
        [0,24107,16552,12125,9427,13152,21440,3383,6873,16117])


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
