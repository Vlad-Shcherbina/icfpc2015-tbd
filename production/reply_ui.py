"""
Controls (one move per command):

  k --->
  j <---
"""

import argparse
import copy
import collections
import json
import itertools
import os
import select
import sys

from production import utils
from production import game

parser = argparse.ArgumentParser()
parser.add_argument('--delay', default=0, type=float, help='Delay between moves (0 requires keypress)')
parser.add_argument('--problems', default='qualifier/problem_%d.json', help='Path of the problems')
parser.add_argument('solution', help='Solution (in JSON)')


FWD = 'k'
BWD = 'j'


def gamepad(timeout=0.0):
  import termios, tty
  fd = sys.stdin.fileno()
  old_attr = termios.tcgetattr(fd)
  tty.setcbreak(fd)
  try:
    while True:
      if timeout <= 0 or fd in select.select([fd], [], [], timeout)[0]:
        ch = sys.stdin.read(1)
        if ch in (FWD, BWD):
          yield ch
      else:
        yield FWD
  except KeyboardInterrupt:
    pass
  finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)


def display(game):
  sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
  sys.stdout.write(game.render_grid())
  sys.stdout.write('\nCurrent move score: {}\n'.format(game.move_score))
  sys.stdout.write('Current unit:\n')
  sys.stdout.write(str(game.current_unit))


def main():
  args = parser.parse_args()

  solution = json.loads(args.solution)[0]
  problem = os.path.join(utils.get_data_dir(), args.problems % solution['problemId'])
  with open(problem) as f:
    problem = json.load(f)
    problem['problemId'] = solution['problemId']

  g = game.Game(problem, solution['seed'])

  try:
    display(g)
    prev_states = collections.deque(maxlen=10)
    prev_states.append(copy.deepcopy(g))

    i = 0
    for cmd in gamepad(args.delay):
      if cmd == FWD:
        prev_states.append(copy.deepcopy(g))
        g.execute_char(solution['solution'][i])
        i += 1
      else: # cmd == BWD
        if i > 0:
          if len(prev_states) > 1:
            g = prev_states[-1]
            prev_states.pop()
          i -= 1
      display(g)
  except game.GameEnded as e:
    print(e)


if __name__ == '__main__':
  main()
