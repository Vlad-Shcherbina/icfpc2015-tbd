import itertools
import os
import json
import pprint
import collections
import logging
import time
import copy
import random
import glob
import requests

from production import big_step_game
from production import utils
from production import interfaces
from production.golden import goldcfg
from production.golden import api
#from production.interfaces import GameEnded, Action
#from production.cpp.placement import Graph


def dummy_phase_one(initial_bsg):
    '''
    Return list of Placements nodes, where to lock units.
    '''

    result = []

    bsg = initial_bsg
    while not bsg.game_ended:
        graph = bsg.get_placement_graph()
        placement = bsg.get_placement_by_node_index(
            graph, random.choice(graph.GetLockedNodes()))

        result.append(placement)
        bsg = bsg.lock_unit(placement)

    return result


def dummy_phase_two(initial_bsg, locking_placements):
    '''
    Returns pair (end_bsg, solution string).
    '''
    result = []

    bsg = initial_bsg
    for placement in locking_placements:
        graph = bsg.get_placement_graph()
        dst_node = graph.FindNodeByMeaning(
            placement.pivot_x, placement.pivot_y, placement.angle)
        print(dst_node)

        path = path_in_graph(graph, graph.GetStartNode(), dst_node)

        # Add final locking move.
        for cmd in range(6):
            if graph.GetNext(dst_node, cmd) == graph.COLLISION:
                break
        else:
            assert False, 'locking move not found'
        path.append(cmd)

        print(path)
        for cmd in path:
            cmd = big_step_game.INDEXED_ACTIONS[cmd]
            result.append(random.choice(interfaces.CHARS_BY_COMMAND[cmd]))

        bsg = bsg.lock_unit(placement)

    print(bsg)

    assert bsg.game_ended
    return bsg, ''.join(result)


def path_in_graph(graph, start, finish):
    assert 0 <= start < graph.GetSize()
    prev = {start: None}
    worklist = [start]
    while True:
        v = worklist.pop()
        if v == finish:
            break

        for cmd in range(6):
            w = graph.GetNext(v, cmd)
            if w == graph.COLLISION:
                continue
            assert 0 <= w < graph.GetSize()
            if w not in prev:
                prev[w] = v, cmd
                worklist.append(w)

    result = []
    while prev[v] is not None:
        v, cmd = prev[v]
        result.append(cmd)

    result = result[::-1]
    v = start
    for cmd in result:
        v = graph.GetNext(v, cmd)
    assert v == finish
    return result


ProblemInstance = collections.namedtuple('ProblemInstance', 'json_data seed')

def get_all_problem_instances():
    paths = glob.glob(os.path.join(utils.get_data_dir(), 'qualifier/*.json'))
    for path in paths:
        with open(path) as fin:
            data = json.load(fin)
        for seed in data['sourceSeeds']:
            yield ProblemInstance(data, seed)


def solve(problem_instance):
    bsg = big_step_game.BigStepGame.from_json(
        problem_instance.json_data, problem_instance.seed)
    print(bsg)

    locking_placements = dummy_phase_one(bsg)
    print(locking_placements)

    end_bsg, commands = dummy_phase_two(bsg, locking_placements)

    return utils.gen_output_raw(
        id=problem_instance.json_data['id'],
        seed=problem_instance.seed,
        commands=commands,
        move_score=end_bsg.move_score,
        power_score=interfaces.compute_power_score(commands))


def fucking_send(solution):
    # TODO: either using Tournament API which is yet to be written
    #       or some less-generic approach (like getting both score
    #       and powerScore) instead of using api.httpSubmit(name, soln)
    #       use api.httpSubmitOwn(name, result, soln)
    ok = api.httpSubmit("Vlad's solver", solution)
    if (200, 'Thanks!') == (ok.status_code, ok.text):
        print("Submission accepted")
    else:
        print("Submission rejected")


def main():
    random.seed(42)

    all_instances = list(get_all_problem_instances())
    print(len(all_instances), 'problem instances total')

    solutions = list(map(solve, all_instances[10:20]))

    print(solutions)

    fucking_send(solutions)


if __name__ == '__main__':
    main()
