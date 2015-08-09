import os
import json
import sys
import itertools
import unittest
import random

import nose
from nose.tools import eq_

from production import solver


def smoke_test():
    random.seed(42)

    all_instances = list(solver.get_all_problem_instances())
    print(len(all_instances), 'problem instances total')

    solutions = list(map(solver.solve, all_instances[::17]))


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
