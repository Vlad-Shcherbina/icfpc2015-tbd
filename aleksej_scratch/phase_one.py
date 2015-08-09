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

from aleksej_scratch import solved_cmp
from peluche_scratch import phase_one as peluche_scratch



LOOK_DISTANCE = 1

def get_possible_placements(bsg):
    graph = bsg.get_placement_graph()
    return [bsg.get_placement_by_node_index(graph, node)
            for node in graph.GetLockedNodes()]


def score_game_pos(game, last_move):
    if game.ls_old:
        return 10*9
    heigh_score = min([y for x, y in last_move.get_members()])

    if LOOK_DISTANCE == 0:
        return heigh_score

    density_score = 0
    density_check = 0
    for x, y in last_move.get_members():
        xx = [x + i for i in range(-LOOK_DISTANCE, LOOK_DISTANCE)]
        yy = [y + i for i in range(-LOOK_DISTANCE, LOOK_DISTANCE)]
        has_neibour = [(a, b) in game.filled for a in xx for b in yy]
        density_check += len(has_neibour)
        density_score += sum(has_neibour)

    return heigh_score + 3 * density_score / density_check


def find_next_placement(game):
    placements = get_possible_placements(game)
    assert(len(placements) > 0)

    result = None
    max_score = -10 ** 9;
    for p in placements:
        moved_game = game.lock_unit(p)
        score = score_game_pos(moved_game, p)
        if score > max_score:
            max_score = score
            result = p

    assert(result)
    return result


def phase_one(game):
    time_left_func = lambda: 1000
    result = []
    while not game.game_ended:
        placement = find_next_placement(game)
        result.append(placement)
        game = game.lock_unit(placement)
        if time_left_func() < 0:
            break
    return game, result


def print_game_result(problem_id, games, comment=''):
    file_name = '%02d.txt' % problem_id
    path = os.path.join('/tmp/', 'phase_one_solver', file_name)
    with open(path, 'a+') as f:
        for seed in sorted(games.keys()):
            result = '%10d - %10d - %-100s\n' % (
                seed, games[seed].move_score, comment)
            f.write(result)


def read_json(filename):
    path = os.path.join(utils.get_data_dir(), 'golden_tests', filename)
    with open(path) as f:
        return json.load(f)


def main():
    problem_id = 7
    problem_file_name = 'problem_%d.json' % problem_id
    path = os.path.join(utils.get_data_dir(), 'qualifier', problem_file_name)
    game_data = read_json(path)

    d = {}
    for seed in game_data['sourceSeeds']:
        game = big_step_game.BigStepGame.from_json(game_data, seed)
        game, moves = phase_one(game)
        d[seed] = game
        print(game)
   #print_game_result(problem_id, d, 'random_run')


if __name__ == '__main__':
    main()
