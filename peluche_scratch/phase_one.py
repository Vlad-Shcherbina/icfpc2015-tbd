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

# def total_depth(bsg):
#     '''we want to maximize'''
#     depth = sum([y for x, y in bsg.filled])

#     max_depth = sum([y for y in range(bsg.height) for x in range(bsg.height)])
#     normalized_depth = depth / max_depth
#     return normalized_depth

# def get_highest_cols(bsg):
#     highest_cols = defaultdict(lambda: bsg.height)
#     for x, y in bsg.filled:
#         highest_cols[x] = min(highest_cols[x], y)
#     return highest_cols

# def total_bumps(bsg):
#     '''we want to minimize'''
#     highest_cols = get_highest_cols(bsg)
#     bumpiness = 0
#     for xx in range(1, bsg.width):
#         bumpiness += abs(highest_cols[xx - 1] - highest_cols[xx])

#     max_bumpiness = (bsg.width - 1) * bsg.height
#     normalized_bumpiness = bumpiness / max_bumpiness # apply logarithm scale ?
#     return - normalized_bumpiness # return as negative cause we want to minimize this

# # def total_hollow(bsg):
# #     '''we strongly want to minimize this'''
# #     highest_cols = get_highest_cols(bsg)
# #     for x, y in bsg.filled

# def total_collapsed(bsg):
#     '''we want to maximize'''
#     return bsg.ls_old

# def total_score(bsg):
#     '''we want to maximize'''
#     return bsg.move_score

# def score_placement(placement, current_bsg, scoring_func_coef):
#     '''compute the score for a placement using the weighted sum of scoring functions'''
#     bsg = current_bsg.lock_unit(placement)
#     score = 0
#     for func, coeff in scoring_func_coef:
#         score += coeff * func(bsg)
#     return score

# scoring_func_coef = [
#     (total_depth, 50),
#     (total_bumps, 10),
#     (total_collapsed, 100),
# #     (total_score, 1),
#     ]

# def chose_move(bsg):
#     return max(get_possible_placements(bsg),
#                key=lambda placement: score_placement(placement, bsg, scoring_func_coef))


# def phase_one_v1(initial_bsg):
#     '''
#     Return list of Placements nodes, where to lock units.
#     '''
#     result = []

#     bsg = initial_bsg
#     while not bsg.game_ended:
#         placement = chose_move(bsg)
#         result.append(placement)
#         bsg = bsg.lock_unit(placement)
#         print(clr + str(bsg))
# #         print(bsg)
# #         k = input()
# #         if k == "d":
# #             import IPython
# #             IPython.embed()
#     return bsg, result

# --- v2 ----

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
            if (x - 1, y - 1): contacts += 1
            if (x - 1, y + 1): contacts += 1
        else: # odd rows
            if x == bsg.width - 1: contacts += 2 # right border
            if (x + 1, y - 1): contacts += 1
            if (x + 1, y + 1): contacts += 1
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
    return (1 * sum_height +
            3 * nb_contacts +
            8 * nb_collapse)

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
        #print(clr + str(bsg))
    return bsg, result


def main():
    results = []
    for j in range(8,9):
        output_file = 'result__' + str(j)
        with open(output_file, "w") as fout:
            fout.write('')
        input_file = 'qualifier/problem_' + str(j) + '.json'
        path = os.path.join(utils.get_data_dir(), input_file)
        with open(path) as fin:
            data = json.load(fin)

        seeds = data['sourceSeeds']
        for seed in [31314]: #seeds:
            bsg = big_step_game.BigStepGame.from_json(data, seed)
            end_bsg, placments = phase_one(bsg)
            results.append((input_file, seed, end_bsg.move_score))

    for result in sorted(results):
        print("{} - {} : {}".format(*result))


if __name__ == '__main__':
    main()
