
import argparse
import itertools
import os
import json
import pprint
import collections
import logging
import time
import random
import sys

from production import utils
from production.interfaces import CHARS_BY_COMMAND, COMMAND_BY_CHAR, COMMAND_CHARS, POWER_PHRASES
from production.interfaces import GameEnded, Action, IGame 


parser = argparse.ArgumentParser()
parser.add_argument('--out_path', nargs='?', default=None, help='')


MAX_UNIT_SIZE = 10
MAX_DIFFRENT_UNITS = 20
MAX_UNIT_COUNT = 100
MAX_BOARD_SIZE = 10
MAX_GAMES = 5

def gen_cell(max_x, max_y):
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)
    return {'x': x, 'y': y}

def gen_unit():
    size_x = random.randint(1, MAX_UNIT_SIZE)
    size_y = random.randint(1, MAX_UNIT_SIZE)
    pivot = gen_cell(size_x, size_y)
    cell_count = random.randint(1, size_x * size_y)
    cells = [gen_cell(size_x, size_y) for _ in range(cell_count)]
    return {
        'pivot': pivot,
        'members': cells
    }

def gen_game():
    id = random.randint(0, 2^31)
    size_x = random.randint(1, MAX_BOARD_SIZE)
    size_y = random.randint(1, MAX_BOARD_SIZE)
    
    units = [gen_unit() for _ in range(random.randint(1, MAX_DIFFRENT_UNITS))]
    unit_count = random.randint(1, MAX_UNIT_COUNT)
    games_seeds = [
        random.randint(0, 2^31)
        for _ in range(random.randint(1, MAX_GAMES))
    ]
    fileld_cells = [
        gen_cell(size_x, size_y)
        for _ in range(random.randint(0, size_x * size_y))
    ]

    return {
        'id': id,
        'units': units,
        'width': size_x,
        'height': size_y,
        'filled': fileld_cells,
        'sourceLength': unit_count,
        'sourceSeeds': games_seeds
    }


def main():
    args = parser.parse_args()

    game = gen_game();
    text = json.dumps(game)

    if args.out_path:
        path = os.path.join(utils.get_data_dir(), args.out_path)
        with open(path) as f:
            f.write(text)
    else:
        print(text)

if __name__ == '__main__':
    main()
