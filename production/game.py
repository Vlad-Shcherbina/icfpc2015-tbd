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

        self.units = list(map(Unit, json_data['units']))

    def __str__(self):
        def cell_fn(x, y):
            if (x, y) in self.filled:
                return '*'
            else:
                return '.'

        result = '{} units:\n'.format(len(self.units))
        for unit in self.units:
            result += str(unit)
            result += '---\n'
        result += render_hex_grid(self.width, self.height, cell_fn)
        return result


def render_hex_grid(width, height, cell_fn):
    result = []
    for y in range(height):
        # To ensure that every cell is surrounded by spaces,
        # used for '(*)' rendering.
        result.append(' ')
        if y % 2:
            result.append(' ')
        for x in range(width):
            c = cell_fn(x, y)
            assert isinstance(c, str) and len(c) == 1, c
            result.append(c + ' ')
        result.append('\n')
    return ''.join(result)


class Shape(object):
    '''
    Shape is a unit in a specific orientation and specific row parity.
    '''

    def __init__(self, pivot_x, pivot_y, members):
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.members = tuple(members)
        self._canonicalize()

    def _canonicalize(self):
        dx = -self.pivot_x
        dy = -(self.pivot_y // 2 * 2)

        self.pivot_x += dx
        self.pivot_y += dy
        self.members = tuple((x + dx, y + dy) for x, y in self.members)

        assert self.pivot_x == 0
        assert self.pivot_y in [0, 1]

    def __str__(self):
        # TODO: is odd rows case handled properly?

        extended_members = self.members + ((self.pivot_x, self.pivot_y),)
        min_x = min(x for x, y in extended_members)
        min_y = min(y for x, y in extended_members)
        max_x = max(x for x, y in extended_members)
        max_y = max(y for x, y in extended_members)

        if min_y % 2:
            min_y -= 1

        def cell_fn(x, y):
            x += min_x
            y += min_y
            if (x, y) == (self.pivot_x, self.pivot_y):
                if (x, y) in self.members:
                    return '!'
                else:
                    return ','
            else:
                if (x, y) in self.members:
                    return '*'
                else:
                    return '.'

        result = render_hex_grid(max_x - min_x + 1, max_y - min_y + 1, cell_fn)
        return result.replace(' , ', '(.)').replace(' ! ', '(*)')

    def __eq__(self, other):
        return \
            (self.pivot_x, self.pivot_y, set(self.members)) == \
            (other.pivot_x, other.pivot_y, set(other.members))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.pivot_x, self.pivot_y, set(self.members)))

    def flipped_row_parity(self):
        return Shape(
            pivot_x=self.pivot_x + self.pivot_y%2, pivot_y=self.pivot_y + 1,
            members=((x + y%2, y + 1) for x, y in self.members))

    def rotated_cw(self):
        px, py = origin_based_rotate_cw(self.pivot_x, self.pivot_y)
        return Shape(
            pivot_x=px, pivot_y=py,
            members=(origin_based_rotate_cw(*pt) for pt in self.members))


def origin_based_rotate_cw(x, y):
    # 0----> skewed_x
    #  \
    #   \
    #    \ skewed_y

    skewed_y = y
    skewed_x = x - y // 2

    new_skewed_y = skewed_x + skewed_y
    new_skewed_x = -skewed_y

    new_y = new_skewed_y
    new_x = new_skewed_x + new_skewed_y // 2

    return new_x, new_y


class Unit(object):

    def __init__(self, json_data):
        base_shape = Shape(
            json_data['pivot']['x'], json_data['pivot']['y'],
            ((pt['x'], pt['y']) for pt in json_data['members']))

        self.even_shapes = build_shape_cycle(base_shape)
        self.odd_shapes = build_shape_cycle(base_shape.flipped_row_parity())

        assert len(self.even_shapes) == len(self.odd_shapes)

    def __str__(self):
        return str(self.even_shapes[0])

    def all_shapes(self):
        result = 'Even:\n'
        for shape in self.even_shapes:
            result += str(shape) + '---\n'
        result += 'Odd:\n'
        for shape in self.odd_shapes:
            result += str(shape) + '---\n'
        return result


def build_shape_cycle(start_shape):
    result = [start_shape]
    while True:
        s = result[-1].rotated_cw()
        if s == result[0]:
            break
        result.append(s)

    assert len(result) in [1, 2, 3, 6]
    return result


def lcg(seed):
    x = seed
    while True:
        yield (x >> 16) % 2**15
        x *= 1103515245
        x += 12345
        x %= 2**32


def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_4.json')
    with open(path) as fin:
        data = json.load(fin)

    pprint.pprint(data)
    g = Game(data)
    print(g)


if __name__ == '__main__':
    main()
