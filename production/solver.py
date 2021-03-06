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
from production import bronze
#from production.interfaces import GameEnded, Action
from production.cpp import placement as cpp_placement


def dummy_phase_one(initial_bsg):
    '''
    Return pair (end_bsg, list of Placements nodes to where to lock units).
    '''

    result = []

    bsg = initial_bsg
    while not bsg.game_ended:
        graph = bsg.get_placement_graph()
        placement = bsg.get_placement_by_node_index(
            graph, random.choice(graph.GetLockedNodes()))

        result.append(placement)
        bsg = bsg.lock_unit(placement)

    return bsg, result


def dummy_phase_two(initial_bsg, locking_placements):
    '''
    Returns pair (end_bsg, solution string).
    '''
    result = []

    novelty_mask = 0

    bsg = initial_bsg
    #print('---')
    for placement in locking_placements:
        #print(bin(novelty_mask))
        graph = bsg.get_placement_graph()

        dst_node = graph.FindNodeByMeaning(
            placement.pivot_x, placement.pivot_y, placement.angle)
#         print(dst_node)

        exit_node = graph.AddNewNode()

        found = False
        for cmd in range(6):
            if graph.GetNext(dst_node, cmd) == graph.COLLISION:
                graph.SetNext(dst_node, cmd, exit_node)
                found = True
        assert found, 'locking move not found'

        assert exit_node == graph.GetSize() - 1

        tmp = []

        path = bsg.dfa.FindBestPath(graph, exit_node, novelty_mask)  # novelty_mask
        for char_code in path:
            tmp.append(big_step_game.ALPHABET[char_code])

        tmp = ''.join(tmp)

        for zzzzz, phrase in enumerate(interfaces.POWER_PHRASES):
            if phrase in tmp:
                novelty_mask |= 2 ** zzzzz;

        result.append(tmp)
        bsg = bsg.lock_unit(placement)

    assert bsg.game_ended

    return None, ''.join(result)


def total_phase_two(initial_bsg, locking_placements):
    '''
    Returns pair (end_bsg, solution string).
    '''
    result = []

    total_graph = cpp_placement.Graph()

    bsg = initial_bsg
    for placement in locking_placements:
        graph = bsg.get_placement_graph()

        dst_node = graph.FindNodeByMeaning(
            placement.pivot_x, placement.pivot_y, placement.angle)

        exit_node = graph.AddNewNode()

        found = False
        for cmd in range(6):
            if graph.GetNext(dst_node, cmd) == graph.COLLISION:
                graph.SetNext(dst_node, cmd, exit_node)
                found = True
        assert found, 'locking move not found'

        assert exit_node == graph.GetSize() - 1
        total_graph.Append(graph)

        bsg = bsg.lock_unit(placement)

    assert bsg.game_ended


    total_path = bsg.dfa.FindBestPath(total_graph, total_graph.GetSize() - 1)
    total_result = []
    for char_code in total_path:
        total_result.append(big_step_game.ALPHABET[char_code])
    #print('total result: ', ''.join(total_result))

    return None, ''.join(total_result)


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


def solve(problem_instance, tag_prefix='NOVELTY2 '):
    bsg = big_step_game.BigStepGame.from_json(
        problem_instance.json_data, problem_instance.seed)
#     print(bsg)

    end_bsg, locking_placements = bronze.phase_one(bsg)
#     print(locking_placements)

    _, commands = dummy_phase_two(bsg, locking_placements)
    print(end_bsg)

    for phrase in interfaces.POWER_PHRASES:
        if phrase in commands:
            print('{:>5} {}'.format(
                utils.count_substrings(commands, phrase), phrase))

    return utils.gen_output_raw(
        id=problem_instance.json_data['id'],
        seed=problem_instance.seed,
        commands=commands,
        move_score=end_bsg.move_score,
        power_score=interfaces.compute_power_score(commands),
        tag_prefix=tag_prefix)


def fucking_send(solution):
    # manpages, hands off!
    # at least this piece works
    s = json.dumps(solution)
    hdr = {'content-type': 'application/json'}
    r   = requests.post(
        goldcfg.url(), auth=('', goldcfg.token()), data=s, headers=hdr)
    assert r.text == 'created'
    print('sent')


def main():
    random.seed(42)

    all_instances = list(get_all_problem_instances())
    print(len(all_instances), 'problem instances total')

    instances = [i for i in all_instances if i.json_data['id'] in range(0, 100)]
    print(len(instances), 'instances to solve')

    solutions = list(map(solve, instances))

    print(solutions)

    fucking_send(solutions)


if __name__ == '__main__':
    main()
