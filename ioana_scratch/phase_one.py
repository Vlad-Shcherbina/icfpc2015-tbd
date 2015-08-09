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
clr = "\x1b\x5b\x48\x1b\x5b\x32\x4a"


def get_possible_placements(bsg):
    graph = bsg.get_placement_graph()
    return [bsg.get_placement_by_node_index(graph, node)
            for node in  graph.GetLockedNodes()]

def get_pair(member):
    return member[0]

def get_y(member):
    return get_pair(member)[1]

def get_x(member):
    return get_pair(member)[0]

def get_depthest_cell(placements):
    if len(placements) == 0:
        return placements
    result = []
    max_y = get_y(placements[0].get_members())
    for position in placements:
        y = get_y(position.get_members()) 
        if y > max_y:
            max_y = y
            result = []
        if y == max_y:
            result.append(position)
    return result

def get_most_left_cell(placements):
    if len(placements) == 0:
        return placements
    result = []
    min_x = get_x(placements[0].get_members())
    for position in placements:
        x = get_x(position.get_members()) 
        if x < min_x:
            min_x = x
            result = []
        if x == min_x:
            result.append(position)
    return result

def phase_one(initial_bsg):
    '''
    Return list of Placements nodes, where to lock units.
    '''

    result = []

    bsg = initial_bsg
    while not bsg.game_ended:
        possible_placements = get_possible_placements(bsg)
        depthest_destination_cells = get_depthest_cell(possible_placements)
        #print(bsg)
        #print(possible_placements)
        placement = random.choice(depthest_destination_cells)
        result.append(placement)
        bsg = bsg.lock_unit(placement)
        print(clr+str(bsg))
        input()

    return bsg, result

def phase_one_random(initial_bsg):
    '''
    Return list of Placements nodes, where to lock units.
    '''

    result = []

    bsg = initial_bsg
    while not bsg.game_ended:
        possible_placements = get_possible_placements(bsg)
        placement = random.choice(possible_placements)
        result.append(placement)
        bsg = bsg.lock_unit(placement)

    return bsg, result


def main():    
    for j in range(0, 25):
        output_file = 'result__' + str(j)
        with open(output_file, "w") as fout:
            fout.write('')
        input_file = 'qualifier/problem_' + str(j) + '.json'
        path = os.path.join(utils.get_data_dir(), input_file)
        with open(path) as fin:
            data = json.load(fin)

        seeds = data['sourceSeeds']
        bsg = big_step_game.BigStepGame.from_json(data, seeds[0])

        end_bsg, placments = phase_one(bsg)
        total_score_depthest += end_bsg.move_score
        print ()


if __name__ == '__main__':
    main()
