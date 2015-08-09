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
from collections import defaultdict

from production import big_step_game
from production import utils

clr = "\x1b\x5b\x48\x1b\x5b\x32\x4a"

def get_possible_placements(bsg):
    graph = bsg.get_placement_graph()
    return [bsg.get_placement_by_node_index(graph, node)
            for node in  graph.GetLockedNodes()]
def sum_height_placement(placement):
    return sum([y for x, y in placement.get_members()])

def number_contacts(placement, bsg, filled):
    contacts = 0
    for x, y in placement.get_members():
        if (x - 1, y) in filled: contacts += 1
        if (x + 1, y) in filled: contacts += 1
        if (x, y - 1) in filled: contacts += 1
        if (x, y + 1) in filled: contacts += 1
        if y == bsg.height - 1: contacts += 2 # touch the floor
        if y % 2 == 0: # even rows
            if y == 0: contacts += 2 # left border
            if (x - 1, y - 1) in filled: contacts += 1
            if (x - 1, y + 1) in filled: contacts += 1
        else: # odd rows
            if x == bsg.width - 1: contacts += 2 # right border
            if (x + 1, y - 1) in filled: contacts += 1
            if (x + 1, y + 1) in filled: contacts += 1
    return contacts

def how_much_collapse(bsg, filled):
    line_has = defaultdict(lambda: bsg.width)
    for x, y in filled:
        line_has[y] -= 1
        assert line_has[y] >= 0
    return line_has

def count_collapse(placement, line_has):
    collapse = 0
    count_y = defaultdict(int)
    for x, y in placement.get_members():
        count_y[y] += 1
    for y, val in count_y.items():
        assert val <= line_has[y]
        if line_has[y] == val:
            collapse += 1
    return collapse

def score_placement_v2(placement, bsg, filled, line_has):
    sum_height = sum_height_placement(placement)
    nb_contacts = number_contacts(placement, bsg, filled)
    nb_collapse = count_collapse(placement, line_has)
    return (4 * sum_height +
            3 * nb_contacts +
            8 * nb_collapse ** 2)

def chose_move_v2(bsg):
    filled = bsg.filled
    line_has = how_much_collapse(bsg, filled)
    return max(get_possible_placements(bsg),
               key=lambda x: score_placement_v2(x, bsg, filled, line_has))

def phase_one(initial_bsg):
    '''
    Return list of Placements nodes, where to lock units.
    '''
    result = []

    bsg = initial_bsg
    while not bsg.game_ended:
        placement = chose_move_v2(bsg)
        result.append(placement)
        bsg = bsg.lock_unit(placement)
        print(clr + str(bsg))
    return bsg, result


def main():
    results = []
    for j in range(25):
        input_file = 'qualifier/problem_' + str(j) + '.json'
        path = os.path.join(utils.get_data_dir(), input_file)
        with open(path) as fin:
            data = json.load(fin)

        seeds = data['sourceSeeds']
        for seed in seeds: #[31314]: #seeds:
            bsg = big_step_game.BigStepGame.from_json(data, seed)
            end_bsg, placments = phase_one(bsg)
            results.append((input_file, seed, end_bsg.move_score))

    for result in sorted(results):
        print("{} - {} : {}".format(*result))


if __name__ == '__main__':
    main()
