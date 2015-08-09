import re
import os
import json
import sys
import itertools
import unittest
import random

import nose
from nose.tools import eq_

from production import solver
from production import game
from production import interfaces


def smoke_test():
    random.seed(42)

    all_instances = list(solver.get_all_problem_instances())
    print(len(all_instances), 'problem instances total')

    for instance in all_instances[::17]:
        solution = solver.solve(instance)
        total_score_estimated_by_solver = int(solution['tag'].split(':')[-1])

        g = game.Game(instance.json_data, instance.seed)
        try:
            g.execute_string(solution['solution'])
        except interfaces.GameEnded as e:
            eq_(total_score_estimated_by_solver, e.total_score)
        else:
            assert False


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
