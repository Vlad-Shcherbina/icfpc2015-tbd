import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument('--problem', nargs='?', default='qualifier/problem_4.json', help='Problem to play')
parser.add_argument('--tracedir', nargs='?', help='Directory where to store the execution traces')
parser.add_argument('--moves', nargs='?', help='Moves to replay')


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


def trace(game):
    '''Trace the state of the game and record it.'''

    state = {
        'problemId': game.problem_id,
        'seed': game.seed,
        'boardState': game.render_grid(),
        'history': game.history,
        'gameEnded': game.game_ended,
        }
    game.trace.append(state)


def dump_trace(game, tracedir):
    if not os.path.exists(tracedir):
      os.mkdir(path)
    path = os.path.join(
        tracedir, 'play_%08d-%08d-%d.json' % (
            game.problem_id, game.seed, time.time()))
    with open(path, "w") as f:
      json.dump(game.trace, f)


def main():
    args = parser.parse_args()

    path = os.path.join(utils.get_data_dir(), args.problem)
    with open(path) as fin:
        data = json.load(fin)
        m = re.match('.*/problem_(\\d+)\\.json', path)
        assert m
        data['problemId'] = int(m.group(1))

    g = game.Game(data, data['sourceSeeds'][0])

    if args.moves:
      moves = args.moves
      delay = 0.05
    else:
      delay = 0
      moves = gamepad()

    g.trace = []

    try:
      sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
      sys.stdout.write(g.render_grid())
      trace(g)

      for ch in moves:
        g.execute_char(ch)
        sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
        sys.stdout.write(g.render_grid())
        trace(g)
        if delay:
          time.sleep(delay)
    except game.GameEnded as e:
      print(e)
      print(utils.gen_output(g, e))
      if args.tracedir:
        dump_trace(g, args.tracedir)


if __name__ == '__main__':
    main()
