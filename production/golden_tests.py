import os
import json
import sys
import itertools

import nose
from nose.tools import eq_

from production import game
from production import utils
from production import interfaces


def read_json(filename):
    path = os.path.join(utils.get_data_dir(), filename)
    with open(path) as f:
        return json.load(f)


def extract_score(tag):
    pass


def run_test(test_filename):
    data = read_json('golden_tests/%s' % test_filename)[0]
    exppected_score = extract_score(data['tag']);
    solution = data['solution']
    problem_id = data['problemId']
    seed = data['seed']

    problem = read_json('qualifier/problem_%d.json' % problem_id)
    g = game.Game(problem, seed)
    try:
        g.execute_string(solution)
    except interfaces.GameEnded as e:
        pass
    eq_(g.score, exppected_score)


def test_something():
    run_test('a.json')


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=FATAL'
    ])
