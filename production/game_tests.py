import os
import json
import sys
import itertools
import unittest

import nose
from nose.tools import eq_

from production import game
from production import big_step_game
from production import utils
from production import interfaces
from production.interfaces import CHARS_BY_COMMAND, Action


class CommonGameTests(object):
    def make_game(self, json_data, seed):
        raise NotImplemented

    def get_2x2_game(self):
        path = os.path.join(utils.get_data_dir(), 'test_problems/2x2.json')
        with open(path) as fin:
            data = json.load(fin)

        return self.make_game(data, seed=0)

    def smoke_test(self):
        path = os.path.join(utils.get_data_dir(), 'qualifier/problem_0.json')
        with open(path) as fin:
            data = json.load(fin)

        g = self.make_game(data, data['sourceSeeds'][0])
        str(g)


    def smoke_test_with_nonempty_board(self):
        path = os.path.join(utils.get_data_dir(), 'qualifier/problem_2.json')
        with open(path) as fin:
            data = json.load(fin)

        g = self.make_game(data, data['sourceSeeds'][0])
        str(g)

    def test_blockage(self):
        g = self.get_2x2_game()
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


    def test_row_collapse(self):
        g = self.get_2x2_game()

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


    def test_turn_leading_to_repetition(self):
        g = self.get_2x2_game()

        try:
            g.execute_string('d')
            print(g)
        except game.GameEnded as e:
            assert 'placement repeated' in e.reason


    def test_unit_exhaustion(self):
        g = self.get_2x2_game()
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


    def test_power_score(self):
        g = self.get_2x2_game()

        g.execute_string('Ei!')

        try:
            while True:
                g.execute_char(CHARS_BY_COMMAND[Action.se][0])
        except game.GameEnded as e:
            eq_(e.power_score, 300 + 2 * 3 * 1)
        else:
            assert False


    def test_custom_power_phrases(self):
        with interfaces.with_custom_power_phrases(['hello']):
            assert 'ei!' not in interfaces.POWER_PHRASES
            g = self.get_2x2_game()

            g.execute_string('Ei!')

            try:
                while True:
                    g.execute_char(CHARS_BY_COMMAND[Action.se][0])
            except game.GameEnded as e:
                eq_(e.power_score, 0)
            else:
                assert False
        assert 'ei!' in interfaces.POWER_PHRASES



class PyGameTests(unittest.TestCase, CommonGameTests):
    def make_game(self, json_data, seed):
        return game.Game(json_data, seed)


class StepGameAdapterTests(unittest.TestCase, CommonGameTests):
    def make_game(self, json_data, seed):
        return big_step_game.StepGameAdapter(json_data, seed)


def test_lcg():
    eq_(list(itertools.islice(game.lcg(17), 10)),
        [0,24107,16552,12125,9427,13152,21440,3383,6873,16117])


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
