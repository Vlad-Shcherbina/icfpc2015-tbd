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
            game, moves = beam_phase_one(game)
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


def evaluated_moves(bsg):
    filled = bsg.filled
    line_has = bronze.how_much_collapse(bsg, filled)
    return [(bronze.score_placement_v2(p, bsg, filled, line_has), p)
            for p in bronze.get_possible_placements(bsg)]


def beam_phase_one(initial_bsg, beam_width=5):
    best_score = -1000000
    best_sol = None

    current_level = [(0, initial_bsg, None)]

    while current_level:
        next_level = []
        for score, bsg, sol in current_level:
            if bsg.game_ended:
                if bsg.move_score > best_score:
                    best_score = bsg.move_score
                    best_sol = sol
                continue
            for delta_score, placement in evaluated_moves(bsg):
                next_level.append((score + delta_score, bsg, sol, placement))

        next_level.sort(key=lambda t: -t[0])
        del next_level[beam_width:]

        current_level = []
        for score, bsg, sol, placement in next_level:
            new_bsg = bsg.lock_unit(placement)
            new_sol = placement, sol
            current_level.append((score, new_bsg, new_sol))

    result = []
    while sol is not None:
        result.append(sol[0])
        sol = sol[1]
    result.reverse()

    bsg = initial_bsg
    for placement in result:
        bsg = bsg.lock_unit(placement)
    return bsg, result


def main():
    res = []
    imporant_test = [5, 6, 7, 20, 14, 22]
    #imporant_test = range(25)
    for problem_id in imporant_test[:1]:
        print('Testing problem %d' % problem_id)
        t = test_problem(problem_id)
        res.append((problem_id, t))
        print(t)

    print('*' * 50)
    print('%-17s - %-25s - %-25s' % ('Result', 'Candidate', 'Production'))
    print('*' * 50)
    for problem_id, (r, (a, b), (c, d)) in res:
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
