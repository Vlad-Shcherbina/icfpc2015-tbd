import os
import json
import pprint
import collections
import logging
import time
import copy
import random
import glob

from production import big_step_game
from production import utils
from production import interfaces
from production.cpp import placement as cpp_placement


def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_24.json')
    with open(path) as fin:
        data = json.load(fin)

    seeds = data['sourceSeeds']
    bsg = big_step_game.BigStepGame.from_json(data, seeds[0])
    print(bsg)

    graph = bsg.get_placement_graph()

    #dfa = cpp_placement.DFA()
    print(bsg.dfa.FindBestPath(graph, graph.GetSize() - 1))

    print('done')


if __name__ == '__main__':
    main()
