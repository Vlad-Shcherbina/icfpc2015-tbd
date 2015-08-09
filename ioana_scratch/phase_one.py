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
        output_file = 'result_' + str(j)
        with open(output_file, "w") as fout:
            fout.write('')
        input_file = 'qualifier/problem_' + str(j) + '.json'
        path = os.path.join(utils.get_data_dir(), input_file)
        with open(path) as fin:
            data = json.load(fin)

        seeds = data['sourceSeeds']
        bsg = big_step_game.BigStepGame.from_json(data, seeds[0])
        print(bsg)

        total_score_random = 0.0
        total_score_depthest = 0.0
        total_games = 10

        for i in range(total_games):
            message = "Now playing game " + str(i) + "\n"
            end_bsg, placments = phase_one(bsg)
            total_score_depthest += end_bsg.move_score
            message += 'Final score depthest:' + str(end_bsg.move_score) + '\n'
            message += str(end_bsg) + '\n'
            message += '============================= vs ==============================\n'
            end_bsg, placments = phase_one_random(bsg)
            total_score_random += end_bsg.move_score
            message += 'Final score random:' + str(end_bsg.move_score) + '\n'
            message += str(end_bsg) + '\n\n'
            with open(output_file, "a") as fout:
                fout.write(message)
        depthest_avg = total_score_depthest / total_games;
        random_avg = total_score_random / total_games;
        with open(output_file, "a") as fout:
                fout.write("depthest avg = " + str(depthest_avg) + "\nrandom avg = " + str(random_avg));


if __name__ == '__main__':
    main()
