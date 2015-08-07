import collections
import json
import logging
import os
import sys
import re
import termios
import tty
import time

from production import utils
from production import game

ARROWS = {
    # W
    'a': 'p',
    # E
    's': 'b',
    # SW
    'd': 'a',
    # SE
    'f': 'l',
    # CW
    'g': 'd',
    # CCW
    'h': 'k',
}


def gamepad(phrase_mode=False):
  fd = sys.stdin.fileno()
  old_attr = termios.tcgetattr(fd)
  tty.setcbreak(sys.stdin.fileno())
  try:
    while True:
      ch = sys.stdin.read(1)
      if phrase_mode:
        yield ch
      else:
        if ch in ARROWS:
          yield ARROWS[ch]
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)


def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_7.json')
    with open(path) as fin:
        data = json.load(fin)
        m = re.match('.*/problem_(\\d+)\\.json', path)
        assert m
        problem_id = m.group(1)

    seed = data['sourceSeeds'][0]
    g = game.Game(data, seed)

    try:
      moves = gamepad()
      sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
      sys.stdout.write(g.render_grid())
      for ch in moves:
        g.execute_char(ch)
        sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
        sys.stdout.write(g.render_grid())
    except game.GameEnded as e:
      print(e)
      print(utils.gen_output(problem_id, seed, g.history))


if __name__ == '__main__':
    main()
