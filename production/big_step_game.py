import itertools
import os
import json
import pprint
import collections
import logging
import time

from production import utils
from production import game
from production.interfaces import GameEnded, Action
from production.cpp.placement import Graph


# Order should be in sync with enum Command in placements.h!
INDEXED_ACTIONS = [
    Action.w, Action.e,
    Action.sw, Action.se,
    Action.cw, Action.ccw]


class BigStepGame(object):
    '''
    Simulator interface optimized for two-phase solvers.
    Incompatible with IGame.
    '''

    def __init__(self, json_data, seed):
        # This is an attribute we add by hand so we have to make sure it
        # exists.
        self.problem_id = json_data['problemId'] \
            if 'problemId' in json_data else -1

        self.width = json_data['width']
        self.height = json_data['height']

        # (x, y) of all filled cells
        self.filled = set()

        for pt in json_data['filled']:
            x, y = xy = pt['x'], pt['y']
            assert 0 <= x < self.width, x
            assert 0 <= y < self.height, y
            assert xy not in self.filled
            self.filled.add(xy)

        self.units = list(map(game.Unit, json_data['units']))
        self.remaining_units = json_data['sourceLength']

        self.seed = seed
        self.lcg = list(
            itertools.islice(game.lcg(seed), 0, self.remaining_units))

        self._move_score = 0

        self.current_unit = None
        self.initial_placement = None
        self.pick_next_unit()
        # self.game_ended = None

    def __str__(self):
        def cell_fn(x, y):
            if (x, y) in self.filled:
                return '*'
            else:
                return '.'
        return game.render_hex_grid(self.width, self.height, cell_fn) + \
            'Current unit:\n' + str(self.current_unit)

    def pick_next_unit(self):
        if self.remaining_units == 0:
            self._end_game(
                move_score=self._move_score,
                power_score=self.power_score(),
                reason="no more units")
        self.remaining_units -= 1

        x = self.lcg.pop(0)
        self.current_unit = self.units[x % len(self.units)]
        self.initial_placement = \
            self.current_unit.get_inital_placement(self.width)
        if not self.can_place(self.initial_placement):
            self._end_game(
                move_score=self._move_score,
                power_score=self.power_score(),
                reason="can't spawn new unit")

    def can_place(self, placement):
        for x, y in placement.get_members():
            if not 0 <= x < self.width:
                return False
            if not 0 <= y < self.height:
                return False
            if (x, y) in self.filled:
                return False
        return True

    def _end_game(self, *args):
        raise NotImplementedError()

    def get_placement_graph(self):
        num_placements = 1
        # <placement>: placement index
        placements = {self.initial_placement : 0}

        worklist = [self.initial_placement]

        transitions = {}

        while worklist:
            p = worklist.pop()
            assert p in placements

            for a_idx, a in enumerate(INDEXED_ACTIONS):
                new_p = p.apply_command(a)

                if self.can_place(new_p):
                    if new_p not in placements:
                        placements[new_p] = num_placements
                        num_placements += 1
                        worklist.append(new_p)
                    logging.debug('  {} --{}({})--> {}'.format(
                        placements[p], a, a_idx, placements[new_p]))
                    transitions[placements[p], a_idx] = placements[new_p]
                else:
                    logging.debug('  {} --{}({})--> {}'.format(
                        placements[p], a, a_idx, Graph.LOCKED))
                    transitions[placements[p], a_idx] = Graph.LOCKED
                    continue

        logging.debug('{} nodes in a graph'.format(num_placements))

        result = Graph(num_placements)
        for (from_index, action_index), to_index in transitions.items():
            result.SetNext(from_index, action_index, to_index)

        for p, idx in placements.items():
            result.SetNodeMeaning(idx, p.pivot_x, p.pivot_y, p.angle)

        return result

    def get_placement_by_node_index(self, placement_graph, index):
        return game.Placement(
            unit=self.current_unit,
            pivot_x=placement_graph.GetNodeMeaningX(index),
            pivot_y=placement_graph.GetNodeMeaningY(index),
            angle=placement_graph.GetNodeMeaningAngle(index))


def main():
    logging.basicConfig(level=logging.DEBUG)

    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_0.json')
    with open(path) as fin:
        data = json.load(fin)

    seeds = data['sourceSeeds']
    bsg = BigStepGame(data, seeds[0])
    print(bsg)

    graph = bsg.get_placement_graph()
    print(bsg.get_placement_by_node_index(graph, 0))


if __name__ == '__main__':
    main()
