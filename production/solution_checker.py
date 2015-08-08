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

        actual_history = ''.join(g.history)
        supplied_history = solution['solution']
        if actual_history != supplied_history:
            print('it seems game ended prematurely')
            print('moves that happened:      {!r} ({})'.format(
                actual_history, len(actual_history)))
            print('moves that were supplied: {!r} ({})'.format(
                supplied_history, len(supplied_history)))
    else:
        print(g)
        print('Game have not ended yet')


if __name__ == '__main__':
    main()
