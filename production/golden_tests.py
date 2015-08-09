import os
import json
import sys
import itertools
import logging
import re

import nose
from nose.tools import eq_

from production import game
from production import big_step_game
from production import utils
from production import interfaces

logger = logging.getLogger(__name__)

def read_json(filename):
    path = os.path.join(utils.get_data_dir(), filename)
    with open(path) as f:
        return json.load(f)


def extract_score(tag):
    # Example tag value: 8a4330144e5c06c3cf5d905e4c6f5d6e 602:0:602
    m = re.match('.* (\d+):(\d+):(\d+)', tag)
    assert(m)
    return int(m.group(3))



def validate_solution(make_game, test_file):
    data = read_json('golden_tests/%s' % test_file)[0]
    exppected_score = extract_score(data['tag']);
    solution = data['solution']
    problem_id = data['problemId']
    seed = data['seed']

    problem = read_json('qualifier/problem_%d.json' % problem_id)
    g = make_game(problem, seed)
    try:
        g.execute_string(solution)
    except interfaces.GameEnded as e:
        pass
    eq_(g.score, exppected_score)



def make_py_game(json_data, seed):
    return game.Game(json_data, seed)


def make_step_adapter_game(json_data, seed):
    return big_step_game.StepGameAdapter(json_data, seed)


def test_all_solution():
    files = os.listdir(os.path.join(utils.get_data_dir(), 'golden_tests'))
    for make_game in [make_py_game, make_step_adapter_game]:
        for f in files:
            yield validate_solution, make_game, f


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
