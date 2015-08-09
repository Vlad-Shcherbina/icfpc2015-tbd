import os
import json
import sys
import itertools
import glob

from production import game
from production import utils


def main():
    paths = glob.glob(os.path.join(utils.get_data_dir(), 'qualifier/*.json'))
    print(paths)

    for path in paths:
        print()
        print('*' * 50)
        print(path)

        with open(path) as fin:
            data = json.load(fin)

        g = game.Game(data, data['sourceSeeds'][0])

        print('Seeds (%d): %s' % (
            len(data['sourceSeeds']),
            " ".join([str(seed) for seed in data['sourceSeeds']])))
        print(g.show_units())
        print(g)


if __name__ == '__main__':
    main()
