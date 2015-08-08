"""
Controls:

  turn ccw     turn cw
           W E
    west  A   D  east
           Z X
south-west     south-east

Undo: `
"""

import argparse
import copy
import json
import itertools
import logging
import os
import sys
import re
import time
import random
from contextlib import contextmanager

from production import utils
from production import game

parser = argparse.ArgumentParser()
parser.add_argument('--problem', nargs='?', default='qualifier/problem_4.json', help='Problem to play')
parser.add_argument('--tracedir', nargs='?', help='Directory where to store the execution traces')
parser.add_argument('--moves', nargs='?', help='Moves to replay')


CONTROLS = {
    'w': game.TURN_CCW,
    'e': game.TURN_CW,

    'a': game.MOVE_W,
    'd': game.MOVE_E,

    'z': game.MOVE_SW,
    'x': game.MOVE_SE,

    # alternative keymap
    'k': game.MOVE_W,
    'l': game.MOVE_E,

    'm': game.MOVE_SW,
    '.': game.MOVE_SE,
}
UNDO = '`'


@contextmanager
def intercept_cbreak(fd):
    # mainly so that it still somewhat works on Windows
    try:
        import termios, tty
    except ImportError:
        try:
            yield
        except KeyboardInterrupt:
            pass
        return

    old_attr = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    try:
        yield
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)


def gamepad(phrase_mode=False):
    with intercept_cbreak(sys.stdin.fileno()):
        while True:
            ch = sys.stdin.read(1)
            if phrase_mode:
                yield ch
            else:
                if ch == UNDO:
                    yield ch
                elif ch in CONTROLS:
                    yield random.choice(game.CHARS_BY_COMMAND[CONTROLS[ch]])


def trace(game):
    '''Trace the state of the game and record it.'''

    state = {
        'problemId': game.problem_id,
        'seed': game.seed,
        'boardState': game.render_grid(),
        'history': game.history[:],
        'gameEnded': game.game_ended,
        }
    game.trace.append(state)


def dump_trace(game, tracedir):
    if not os.path.exists(tracedir):
        os.mkdir(tracedir)
    path = os.path.join(
        tracedir, 'play_%08d-%08d-%d.json' % (
            game.problem_id, game.seed, time.time()))
    with open(path, "w") as f:
        json.dump(game.trace, f)


def main():
    random.seed(42)
    args = parser.parse_args()

    path = os.path.join(utils.get_data_dir(), args.problem)
    with open(path) as fin:
        data = json.load(fin)
        m = re.match('.*/problem_(\\d+)\\.json', path)
        assert m
        data['problemId'] = int(m.group(1))

    g = game.Game(data, data['sourceSeeds'][0])

    if args.moves:
        delay = 0.05
    else:
        delay = 0

    moves = itertools.chain(args.moves, gamepad())

    try:
        sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
        sys.stdout.write(g.render_grid())
        sys.stdout.write('\nCurrent move score: {}\n'.format(g.move_score))
        sys.stdout.write('Current unit:\n')
        sys.stdout.write(str(g.current_unit))

        g.trace = []
        trace(g)
        prev_states = [copy.deepcopy(g)]

        for ch in moves:
            if ch == UNDO:
                if len(prev_states) > 1:
                    g = prev_states[-1]
                    prev_states.pop()
            else:
                prev_states.append(copy.deepcopy(g))
                g.execute_char(ch)
                trace(g)

            sys.stdout.write("\x1b\x5b\x48\x1b\x5b\x4a")
            sys.stdout.write(g.render_grid())
            sys.stdout.write('\nCurrent move score {}:\n'.format(g.move_score))
            sys.stdout.write('Current unit:\n')
            sys.stdout.write(str(g.current_unit))

            if delay:
                time.sleep(delay)
    except game.GameEnded as e:
        print(e)
        print(utils.gen_output(g, e))
        if args.tracedir:
            dump_trace(g, args.tracedir)


if __name__ == '__main__':
    main()
