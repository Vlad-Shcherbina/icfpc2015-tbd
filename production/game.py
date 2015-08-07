import os
import json
import pprint

from production import utils


class Game(object):

    # TODO: reduce initialization to primitive operations, so that C++
    # implementation does not have to deal with json.
    def __init__(self, json_data):
        self.width = json_data['width']
        self.height = json_data['height']

        # (x, y) of all filled cells
        self.filled = set()

        for pt in json_data['filled']:
            x, y = xy = pt['x'], pt['y']
            assert 0 <= x < self.width, x
            assert 0 <= y < self.height, y
            assert xy not in self.filled
            self.filled.add(xy)

    def __str__(self):
        result = []
        for y in range(self.height):
            if y % 2:
                result.append(' ')
            for x in range(self.width):
                if (x, y) in self.filled:
                    result.append('* ')
                else:
                    result.append('. ')
            result.append('\n')
        return ''.join(result)


def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_1.json')
    with open(path) as fin:
        data = json.load(fin)

    pprint.pprint(data)
    g = Game(data)
    print(g)


if __name__ == '__main__':
    main()
