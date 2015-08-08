import argparse
import copy
import json
import logging
import os
import glob
import sys
import re
import time
import random
from contextlib import contextmanager

from production import utils
from production import game

parser = argparse.ArgumentParser()
parser.add_argument('--traces', nargs='?', help='Path of the traces')
parser.add_argument('--problems', nargs='?', default='qualifier/problem_%d.json', help='Path of the problems')

def main():
    args = parser.parse_args()
    for trace in glob.glob(args.traces):
      with open(trace) as f:
        trace = json.load(f)
      data = os.path.join(utils.get_data_dir(), args.problems % trace[0]['problemId'])
      with open(data) as f:
        data = json.load(f)
        data['problemId'] = trace[0]['problemId']

      g = game.Game(data, trace[0]['seed'])

      i = 0
      for move in trace[1:]:
        g.execute_char(move['history'][i])
        sys.stdout.write('\x1b\x5b\x48\x1b\x5b\x4a')
        sys.stdout.write(move['boardState'])
        sys.stdout.write('\n\n')
        try:
          sys.stdout.write(g.render_grid())
        except game.GameEnded:
          pass

        assert move['boardState'] == g.render_grid()
        assert g.game_ended == move['gameEnded']
        if g.game_ended is not None:
          break

        time.sleep(0.01)
        i += 1


if __name__ == '__main__':
    main()
