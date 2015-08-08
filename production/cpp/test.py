import sys

import nose
from nose.tools import eq_

from production.cpp import placement


W   = placement.Graph.W
E   = placement.Graph.E
SW  = placement.Graph.SW
SE  = placement.Graph.SE
CW  = placement.Graph.CW
CCW = placement.Graph.CCW


def test_stuff():
  graph = placement.Graph(10)
  graph.SetNext(3, W, 2)
  eq_(graph.GetNext(3, W), 2)


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
