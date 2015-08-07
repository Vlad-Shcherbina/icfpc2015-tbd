import collections
import json
import logging
import os
import sys
import termios
import tty

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

    g = game.Game(data, data['sourceSeeds'][0])

    try:
      print "\x1b\x5b\x48\x1b\x5b\x4a" + g.render_grid()
      for ch in gamepad():
        g.execute_char(ch)
        print "\x1b\x5b\x48\x1b\x5b\x4a" + g.render_grid()
    except game.GameEnded as e:
      print(e)


if __name__ == '__main__':
    main()
