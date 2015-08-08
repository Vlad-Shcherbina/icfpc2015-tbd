#import itertools
import os
import json
import pprint
import collections
import logging
import time

from production import utils
from production.interfaces import CHARS_BY_COMMAND, COMMAND_BY_CHAR, COMMAND_CHARS, POWER_PHRASES
from production.interfaces import GameEnded, Action, IGame 


class Game(IGame):
    def __init__(self, board, units):
        self.board = board
        self.current_unit

    def process(commands):
        for c in commands:
            process_command(c)

    def process_command(c):
        if not can_move(c):
            board.lock(self.x, self.y, self.current_unit)
            self.current_unit = []
            self.x = 
        else:
            move(c)



class Board:
    def __init__(self, width, height, full):
        self.width = width
        self.height = height
        self.full = set(full)

    def is_filled(x, y):
      return (x, y) in self.full

    def lock(x, y, unit):
      for px, py in unit.cells:
        xx = x + px
        yy = y + py
        assert (xx, yy) not in self.full 
        self.full.add((xx, yy))



Unit = collections.namedtuple(
    'Unit', 'pivot_x pivot_y cells')

# class Unit:
#     def __init__(self, x, y, cells):
#       self.pivot_x = x
#       self.pivot_y = y
#       self.cells = cells


def parse(filename):
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_4.json')
    with open(path) as f:
        return json.load(f)

def main():
    json = parse('qualifier/problem_4.json')
    b = Board(json['width'], json['height'], json['filled'])

    convert_members = lambda u: [(p['x'], p['y']) for p in u['members']]
    units = [
        Unit(u['pivot']['x'], u['pivot']['y'], convert_members(u))
        for u in json['units']
    ]

    print(units)
    #assert(False)
    #print(json)
    #print (b.width)
    print('Hello!')

if __name__ == '__main__':
    main()
