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
total_score_random = 0;
total_score_depthest = 0;


def get_possible_placements(bsg):
    graph = bsg.get_placement_graph()
    return [bsg.get_placement_by_node_index(graph, node)
            for node in  graph.GetLockedNodes()]

def get_pair(member):
    return member[0]

def get_y(member):
    return get_pair(member)[1]

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

    return bsg, result


def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_0.json')
    with open(path) as fin:
        data = json.load(fin)

    seeds = data['sourceSeeds']
    bsg = big_step_game.BigStepGame.from_json(data, seeds[0])
    print(bsg)


    end_bsg, placments = phase_one(bsg)

    print('Final score:', end_bsg.move_score)


if __name__ == '__main__':
    main()
