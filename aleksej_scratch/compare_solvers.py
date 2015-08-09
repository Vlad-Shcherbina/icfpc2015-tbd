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
from aleksej_scratch import phase_one as aleksej_scratch
from peluche_scratch import phase_one as peluche_scratch



def read_json(filename):
    path = os.path.join(utils.get_data_dir(), 'golden_tests', filename)
    with open(path) as f:
        return json.load(f)


def main():
    problem_id = 8
    problem_file_name = 'problem_%d.json' % problem_id
    path = os.path.join(utils.get_data_dir(), 'qualifier', problem_file_name)
    game_data = read_json(path)

    def play_dist1_games():
        while True:
            seed = random.randint(0, 100000)
            print('playing game 1 with seed %d' % seed)
            seed = random.randint(0, 100000)
            game = big_step_game.BigStepGame.from_json(game_data, seed)
            game, moves = aleksej_scratch.phase_one(game)
            print(game)
            yield game.move_score

    def play_dist2_games():
        while True:
            seed = random.randint(0, 100000)
            print('playing game 2 with seed %d' % seed)
            game = big_step_game.BigStepGame.from_json(game_data, seed)
            game, moves = peluche_scratch.phase_one(game)
            print(game)
            yield game.move_score

    result = solved_cmp.compare_solver(play_dist1_games(), play_dist2_games())
    print(result)


if __name__ == '__main__':
    main()
