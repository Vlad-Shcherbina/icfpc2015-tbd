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
    'h': 'p',
    # E
    'j': 'b',
    # SW
    'b': 'a',
    # SE
    'm': 'l',
    # CW
    'i': 'd',
    # CCW
    'y': 'k',
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
  except KeyboardInterrupt:
    pass
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)


def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_4.json')
    with open(path) as fin:
        data = json.load(fin)
        m = re.match('.*/problem_(\\d+)\\.json', path)
        assert m
        data['problemId'] = m.group(1)


    g = game.Game(data, data['sourceSeeds'][0])

    moves = gamepad()
    delay = 0
    if len(sys.argv) == 2:
      delay = 0.05
      moves = sys.argv[1]

    try:
      sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
      sys.stdout.write(g.render_grid())
      for ch in moves:
        g.execute_char(ch)
        sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
        sys.stdout.write(g.render_grid())
        if delay:
          time.sleep(delay)
    except game.GameEnded as e:
      print(e)
      print(utils.gen_output(g, e))


if __name__ == '__main__':
    main()
