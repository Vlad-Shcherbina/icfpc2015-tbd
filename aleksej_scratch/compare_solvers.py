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
from aleksej_scratch import phase_one as candidate_solver
from production import bronze


def read_json(filename):
    path = os.path.join(utils.get_data_dir(), 'golden_tests', filename)
    with open(path) as f:
        return json.load(f)


def test_problem(problem_id):
    problem_id = problem_id
    problem_file_name = 'problem_%d.json' % problem_id
    path = os.path.join(utils.get_data_dir(), 'qualifier', problem_file_name)
    game_data = read_json(path)

    def play_dist1_games():
        while True:
            seed = random.randint(0, 10 ** 9)
            game = big_step_game.BigStepGame.from_json(game_data, seed)
            game, moves = candidate_solver.phase_one(game)
            print('played candidate game %d with seed %d scored %d' % (problem_id, seed, game.move_score))
            yield game.move_score

    def play_dist2_games():
        while True:
            seed = random.randint(0, 10 ** 9)
            game = big_step_game.BigStepGame.from_json(game_data, seed)
            game, moves = bronze.phase_one(game)
            print('played production game %d with seed %d scored %d' % (problem_id, seed, game.move_score))
            yield game.move_score

    return solved_cmp.compare_solver(play_dist1_games(), play_dist2_games())


def main():
    res = []
    for problem_id in range(0, 24):
        print('Testing problem %d' % problem_id)
        t = test_problem(problem_id)
        res.append(t)
        print(t)

    print('*' * 50)
    print('%-17s - %-25s - %-25s' % ('Result', 'Candidate', 'Production'))
    print('*' * 50)
    for r, (a, b), (c, d) in res:
        def desc():
            if r == 0: return 'Inconclusive'
            if r == 1: return 'Candidate'
            if r == -1: return 'Production'
        s = desc()
        candidate_desc = '(%.3f, %.3f)' % (a, b)
        prod_desc = '(%.3f, %.3f)' % (c, d)
        print('%2d (%-12s) - (%-25s) - (%-25s)' % (r, s, candidate_desc, prod_desc))



if __name__ == '__main__':
    main()
