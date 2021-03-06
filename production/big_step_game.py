import itertools
import os
import json
import pprint
import collections
import logging
import time
import copy
import random

from production import utils
from production import game
from production import interfaces
from production.interfaces import GameEnded, Action
from production.cpp.placement import Graph
from production.cpp import placement as cpp_placement
from production.dfa import FullDfa


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

    @staticmethod
    def from_json(json_data, seed):
        bsg = BigStepGame()

        #bsg.dfa = cpp_placement.DFA()
        bsg.dfa = translate_dfa(interfaces.POWER_PHRASES)

        bsg.problem_id = json_data['problemId'] \
            if 'problemId' in json_data else -1
        bsg.remaining_units = json_data['sourceLength']
        bsg.seed = seed
        bsg.lcg = list(
            itertools.islice(game.lcg(seed), 0, bsg.remaining_units))


        bsg.width = json_data['width']
        bsg.height = json_data['height']

        # (x, y) of all filled cells
        bsg.filled = set()

        for pt in json_data['filled']:
            x, y = xy = pt['x'], pt['y']
            assert 0 <= x < bsg.width, x
            assert 0 <= y < bsg.height, y
            assert xy not in bsg.filled
            bsg.filled.add(xy)

        bsg.units = list(map(game.Unit, json_data['units']))

        bsg.cpp_units = []
        for unit in bsg.units:
          unit_builder = cpp_placement.UnitBuilder()
          for shapes in [unit.even_shapes, unit.odd_shapes]:
            for angle, shape in enumerate(shapes):
              for cell_x, cell_y in shape.members:
                unit_builder.SetCell(
                    shape.pivot_x, shape.pivot_y, angle,
                    shape.min_x, shape.min_y,
                    shape.max_x, shape.max_y,
                    cell_x, cell_y)
          bsg.cpp_units.append(unit_builder.Build(bsg.width, bsg.height))

        bsg.move_score = 0
        bsg.ls_old = 0
        bsg.game_ended = False
        bsg.reason = None

        bsg.current_unit = None
        bsg.current_cpp_unit = None
        bsg.initial_placement = None

        bsg.pick_next_unit()

        return bsg

    def lock_unit(self, locked_placement):
        assert not self.game_ended
        #logger.info('locking unit in place:\n' + str(self))
        assert self.can_place(locked_placement)

        bsg = BigStepGame()
        bsg.dfa = self.dfa

        bsg.problem_id = self.problem_id
        bsg.remaining_units = self.remaining_units
        bsg.seed = self.seed
        bsg.lcg = copy.copy(self.lcg)

        bsg.width = self.width
        bsg.height = self.height

        bsg.filled = copy.copy(self.filled)

        # no need in deep copy because they don't change
        bsg.units = self.units
        bsg.cpp_units = self.cpp_units

        bsg.move_score = self.move_score
        bsg.ls_old = self.ls_old
        bsg.game_ended = self.game_ended
        bsg.reason = self.reason

        bsg.current_unit = self.current_unit
        bsg.initial_placement = self.initial_placement

        # From now on it's ok to modify in place, because we do it on
        # a copy. Consider it part of the construction process.

        for x, y in locked_placement.get_members():
            bsg.filled.add((x, y))

        ls = bsg.collapse_rows()

        size = len(locked_placement.get_shape().members)
        points = size + 100 * (1 + ls) * ls // 2
        if bsg.ls_old > 1:
            line_bouns = (bsg.ls_old - 1) * points // 10
        else:
            line_bouns = 0
        bsg.move_score += points + line_bouns
        bsg.ls_old = ls

        bsg.pick_next_unit()
        return bsg

    def __str__(self):
        def cell_fn(x, y):
            if (x, y) in self.filled:
                return '*'
            else:
                return '.'
        result = game.render_hex_grid(self.width, self.height, cell_fn)
        if self.game_ended:
            result += 'Game ended ({}), move_score = {}'.format(
                self.reason, self.move_score)
        else:
            result += 'Current unit:\n' + str(self.current_unit)
        return result


    def pick_next_unit(self):
        if self.remaining_units == 0:
            self.game_ended = True
            self.reason = "no more units"
            return

        self.remaining_units -= 1

        x = self.lcg.pop(0)
        assert len(self.units) == len(self.cpp_units)
        self.current_unit = self.units[x % len(self.units)]
        self.current_cpp_unit = self.cpp_units[x % len(self.cpp_units)]
        self.initial_placement = \
            self.current_unit.get_inital_placement(self.width)
        if not self.can_place(self.initial_placement):
            self.game_ended = True
            self.reason = "can't spawn new unit"

    def collapse_rows(self):
        cnt_in_row = [0] * self.height
        for x, y in self.filled:
            cnt_in_row[y] += 1

        updated_y = {}
        y1 = self.height - 1
        for y in reversed(range(self.height)):
            if cnt_in_row[y] != self.width:
                assert y1 >= 0
                updated_y[y] = y1
                y1 -= 1

        new_filled = set()
        for x, y in self.filled:
            if y in updated_y:
                new_filled.add((x, updated_y[y]))

        cells_destroyed = len(self.filled) - len(new_filled)
        assert cells_destroyed >= 0
        assert cells_destroyed % self.width == 0

        rows_collapsed = cells_destroyed // self.width
        #logging.info('collapsing {} rows'.format(rows_collapsed))

        self.filled = new_filled
        return rows_collapsed

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
      return self.get_placement_graph_cpp()

    def get_placement_graph_twice(self):
      cpp_graph = self.get_placement_graph_cpp()
      py_graph = self.get_placement_graph_py()
      assert cpp_placement.IsIdentical(cpp_graph, py_graph)
      return py_graph

    def get_placement_graph_py(self):
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
                    #logging.debug('  {} --{}({})--> {}'.format(
                    #    placements[p], a, a_idx, placements[new_p]))
                    transitions[placements[p], a_idx] = placements[new_p]
                else:
                    #logging.debug('  {} --{}({})--> {}'.format(
                    #    placements[p], a, a_idx, Graph.COLLISION))
                    transitions[placements[p], a_idx] = Graph.COLLISION
                    continue

        logging.debug('{} nodes in a graph'.format(num_placements))

        result = Graph(num_placements)
        for (from_index, action_index), to_index in transitions.items():
            result.SetNext(from_index, action_index, to_index)

        for p, idx in placements.items():
            result.SetNodeMeaning(idx, p.pivot_x, p.pivot_y, p.angle)

        result.SetStartNode(placements[self.initial_placement])

        return result

    def get_placement_graph_cpp(self):
      graph_builder = cpp_placement.GraphBuilder(self.width, self.height)

      for x, y in self.filled:
        graph_builder.FillCell(x, y)

      graph_builder.SetCurrentUnit(self.current_cpp_unit)
      graph_builder.ComputeValidPlacements()

      p = self.initial_placement
      result = graph_builder.Build(p.pivot_x, p.pivot_y, p.angle)

      return result


    def get_placement_by_node_index(self, placement_graph, index):
        return game.Placement(
            unit=self.current_unit,
            pivot_x=placement_graph.GetNodeMeaningX(index),
            pivot_y=placement_graph.GetNodeMeaningY(index),
            angle=placement_graph.GetNodeMeaningAngle(index))


class StepGameAdapter(interfaces.IGame):

    def __init__(self, json_data, seed):
        self.history = []
        self._update_bsg(BigStepGame.from_json(json_data, seed))

    def _update_bsg(self, new_bsg):
        self.bsg = new_bsg
        if self.bsg.game_ended:
            raise interfaces.GameEnded(
                move_score=self.bsg.move_score,
                power_score=self.power_score(),
                reason=self.bsg.reason)
        self.graph = self.bsg.get_placement_graph()
        self.current_node = self.graph.GetStartNode()

        self._sanity_check_scc(self.graph)

    def _sanity_check_scc(self, graph):
        scc = cpp_placement.StronglyConnectedComponents(graph)
        assert sum(map(len, scc)) == graph.GetSize()
        xs = sum(scc, ())
        assert len(xs) == len(set(xs))

        scc_by_node = {}
        for i, cc in enumerate(scc):
            ys = set(graph.GetNodeMeaningY(node) for node in cc)
            if len(ys) > 1:
                print(self.bsg.current_unit)
                assert len(ys) == 1, ys

            for node in cc:
                assert node not in scc_by_node
                scc_by_node[node] = i

        for v in range(graph.GetSize()):
            for c in range(6):
                w = graph.GetNext(v, c)
                if w == graph.COLLISION:
                    continue
                assert scc_by_node[v] <= scc_by_node[w], (
                    "SCCs should be topologically sorted")

    @property
    def filled(self):
        return frozenset(self.bsg.filled)

    @property
    def move_score(self):
        return self.bsg.move_score

    @property
    def score(self):
        return self.move_score + self.power_score()

    @property
    def remaining_units(self):
        return self.bsg.remaining_units

    def execute_string(self, s):
        for c in s:
            self.execute_char(c)

    def execute_char(self, c):
        c = c.lower()
        self.history.append(c)

        command = interfaces.COMMAND_BY_CHAR[c]
        assert command is not None
        command_index = INDEXED_ACTIONS.index(command)

        new_node = self.graph.GetNext(self.current_node, command_index)
        if new_node != self.graph.COLLISION:
            self.current_node = new_node
            return

        placement = self.bsg.get_placement_by_node_index(
            self.graph, self.current_node)

        self._update_bsg(self.bsg.lock_unit(placement))

    def power_score(self):
        s = ''.join(self.history)
        assert s.lower() == s, s
        return interfaces.compute_power_score(s)


ALPHABET = ''
for action in INDEXED_ACTIONS:
    chars = interfaces.CHARS_BY_COMMAND[action]
    assert len(chars) == 6
    ALPHABET += chars


def translate_dfa(phrases):
    dfa = FullDfa(phrases, ALPHABET)
    logging.info('DFA has {} states'.format(len(dfa._dfa)))

    state_code = {}
    for state, _ in dfa._dfa.items():
        assert state not in state_code
        state_code[state] = len(state_code)

    #pprint.pprint(state_code)

    initial = state_code[dfa._current_state]
    logging.info('initial state: {}'.format(initial))

    transitions = [[] for _ in state_code]
    for state, ts in dfa._dfa.items():
        for c in ALPHABET:
            transitions[state_code[state]].append(state_code[ts[c]])
            #print(ts)

    for row in transitions:
        logging.info(row)

    mask_increments = [0] * len(state_code)
    for state, _ in dfa._dfa.items():
        for word in dfa._end_state_lookup.get(state, []):
            mask_increments[state_code[state]] |= 2 ** phrases.index(word)

    logging.info('mask_increments {}'.format(mask_increments))

    word_lengths = list(map(len, phrases))
    logging.info('world lenghts {}'.format(word_lengths))

    return cpp_placement.DFA(initial, transitions, mask_increments, word_lengths)



def main():
    random.seed(42)
    logging.basicConfig(level=logging.DEBUG)


    print(translate_dfa(interfaces.POWER_PHRASES[:2]))

    return

    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_0.json')
    with open(path) as fin:
        data = json.load(fin)

    seeds = data['sourceSeeds']
    bsg = BigStepGame.from_json(data, seeds[0])
    print(bsg)

    while not bsg.game_ended:
        graph = bsg.get_placement_graph()
        print('locked nodes:', graph.GetLockedNodes())
        placement = bsg.get_placement_by_node_index(
            graph, random.choice(graph.GetLockedNodes()))
        print(placement)
        bsg = bsg.lock_unit(placement)
        print(bsg)


if __name__ == '__main__':
    main()
