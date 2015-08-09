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



def get_possible_placements(bsg):
    graph = bsg.get_placement_graph()
    return [bsg.get_placement_by_node_index(graph, node)
            for node in graph.GetLockedNodes()]

def choice_placement(placements):
    assert(len(placements) > 0)
    result = None
    max_y = -1;
    for p in placements:
        y = min([y for x, y in p.get_members()])
        if y > max_y:
            max_y = y
            result = p
    return result

def play_game(game):
    result = []
    while not game.game_ended:
        placements = get_possible_placements(game)

        placement = choice_placement(placements)
        #print(placement.get_members())

        result.append(placement)
        game = game.lock_unit(placement)
    return result, game


def print_game_result(problem_id, seed, game, comment=''):
    file_name = '%02d_%d.txt' % (problem_id, seed)
    path = os.path.join('/tmp/', 'phase_one_solver', file_name)
    with open(path, 'a+') as f:
        result = '%10d - %-100s\n' % (game.move_score, comment)
        f.write(result)


def read_json(filename):
    path = os.path.join(utils.get_data_dir(), 'golden_tests', filename)
    with open(path) as f:
        return json.load(f)


def main():
    problem_id = 3
    problem_file_name = 'problem_%d.json' % problem_id
    path = os.path.join(utils.get_data_dir(), 'qualifier', problem_file_name)
    game_data = read_json(path)
    seeds = game_data['sourceSeeds']
    for seed in seeds:
        game = big_step_game.BigStepGame.from_json(game_data, seed)
        moves, game = play_game(game)
        print_game_result(problem_id, seed, game, 'deepest min-max per figure')
        print(game)

if __name__ == '__main__':
    main()
