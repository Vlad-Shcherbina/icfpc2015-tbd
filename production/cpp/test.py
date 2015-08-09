import json
import os
import sys
import unittest

import nose
from nose.tools import eq_

from production import utils
from production.testing_utils import isolate_process_failures
from production import game
from production.cpp import placement


W   = placement.Graph.W
E   = placement.Graph.E
SW  = placement.Graph.SW
SE  = placement.Graph.SE
CW  = placement.Graph.CW
CCW = placement.Graph.CCW


def CreateGraphBuilder(json_data):
  board_width = json_data['width']
  board_height = json_data['height']

  graph_builder = placement.GraphBuilder(board_width, board_height)

  for pt in json_data['filled']:
    graph_builder.FillCell(pt['x'], pt['y'])

  return graph_builder


def CreateUnits(json_data):
  board_width = json_data['width']
  board_height = json_data['height']

  units = []
  for unit in map(game.Unit, json_data['units']):
    unit_builder = placement.UnitBuilder()
    for shapes in [unit.even_shapes, unit.odd_shapes]:
      for angle, shape in enumerate(shapes):
        for cell_x, cell_y in shape.members:
          unit_builder.SetCell(
              shape.pivot_x, shape.pivot_y, angle,
              shape.min_x, shape.min_y,
              shape.max_x, shape.max_y,
              cell_x, cell_y)
    units.append(unit_builder.Build(board_width, board_height))

  return units


def test_stuff():
  graph = placement.Graph(10)
  graph.SetNext(3, W, 2)
  eq_(graph.GetNext(3, W), 2)


class GraphBuilderTest(unittest.TestCase):

  @isolate_process_failures()
  def test_is_valid_placement(self):
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_3.json')
    with open(path) as fin:
      data = json.load(fin)

    units = CreateUnits(data)
    graph_builder = CreateGraphBuilder(data)
    g = game.Game(data, seed=0)

    eq_(len(units), len(g.units))

    for index, unit in enumerate(units):
      graph_builder.SetCurrentUnit(unit)
      graph_builder.ComputeValidPlacements()

      u = g.units[index]

      for angle, _ in enumerate(u.even_shapes):
        for pivot_x in range(-g.width, 2 * g.width):
          for pivot_y in range(-g.height, 2 * g.height):
            can_place = graph_builder.IsValidPlacement(pivot_x, pivot_y, angle)
            p = game.Placement(u, pivot_x, pivot_y, angle)
            eq_(g.can_place(p), can_place)


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
