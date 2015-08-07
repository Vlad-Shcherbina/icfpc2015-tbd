import json
import os
import logging

from production import game
from production import utils


def main():
    logging.basicConfig(level=logging.DEBUG)

    solution = input(
        'Enter solution json:\n')
    solution = json.loads(solution)

    path = os.path.join(
        utils.get_data_dir(),
        'qualifier/problem_{}.json'.format(solution['problemId']))
    with open(path) as fin:
        data = json.load(fin)

    g = game.Game(data, solution['seed'])

    try:
        g.execute_string(solution['solution'])
    except game.GameEnded as e:
        print('*' * 50)
        print(e)
        assert ''.join(g.history) == solution['solution']
    else:
        print(g)
        print('Game have not ended yet')


if __name__ == '__main__':
    main()
