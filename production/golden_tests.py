import os
import json
import sys
import itertools
import logging
import re

import nose
from nose.tools import eq_

from production import game
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
    return int(m.group(1))


def validate_solution(test_file):
    data = read_json('golden_tests/%s' % test_file)[0]
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


def test_all_solution():
    files = os.listdir(os.path.join(utils.get_data_dir(), 'golden_tests'))
    for f in files:
        logger.info('Running test %s' % f)
        validate_solution(f)


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
