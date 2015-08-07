import os
import json
import pprint
import collections
import logging

from production import utils


logger = logging.getLogger(__name__)


MOVE_W = 'move_w'
MOVE_E = 'move_e'
MOVE_SW = 'move_sw'
MOVE_SE = 'move_se'
ROTATE_CW = 'rotate_cw'
ROTATE_CCW = 'rotate_ccw'

COMMAND_CHARS =[
    ("p'!.03", MOVE_W),
    ('bcefy2', MOVE_E),
    ('aghij4', MOVE_SW),
    ('lmno 5', MOVE_SE),
    ('dqrvz1', ROTATE_CW),
    ('kstuwx', ROTATE_CCW),
    ('\t\n\r', None),
]
COMMAND_BY_CHAR = {char: cmd for chars, cmd in COMMAND_CHARS for char in chars}


class GameEnded(Exception):
    def __init__(self, score, reason):
        self.score = score
        self.reason = reason

    def __str__(self):
        return 'GameEnded(score={}, reason={!r})'.format(
            self.score, self.reason)


class Game(object):

    # TODO: reduce initialization to primitive operations, so that C++
    # implementation does not have to deal with json.
    def __init__(self, json_data, seed):
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

        self.lcg = iter(lcg(seed))

        self.remaining_units = json_data['sourceLength']

        self.score = 0

        self.current_unit = None
        self.current_placement = None
        self.used_placements = None
        self.pick_next_unit()

    def can_place(self, placement):
        for x, y in placement.get_members():
            if not 0 <= x < self.width:
                return False
            if not 0 <= y < self.height:
                return False
            if (x, y) in self.filled:
                return False
        return True

    def pick_next_unit(self):
        if self.remaining_units == 0:
            raise GameEnded(score=self.score, reason="no more units")
        self.remaining_units -= 1

        x = next(self.lcg)
        self.current_unit = self.units[x % len(self.units)]
        self.current_placement = \
            self.current_unit.get_inital_placement(self.width)
        self.visited_placements = set()
        if not self.can_place(self.current_placement):
            raise GameEnded(score=self.score, reason="can't spawn new unit")

    def lock_unit(self):
        logger.info('locking unit in place:\n' + str(self))
        assert self.can_place(self.current_placement)
        for x, y in self.current_placement.get_members():
            self.filled.add((x, y))

        # TODO: collapse lines and update score

        self.pick_next_unit()

    def execute_command(self, command):
        new_placement = self.current_placement.apply_command(command)
        if self.can_place(new_placement):
            self.current_placement = new_placement

            if new_placement in self.visited_placements:
                raise GameEnded(score=0, reason='placement repeated')
            self.visited_placements.add(new_placement)
        else:
            self.lock_unit()

    def execute_string(self, s):
        for c in s.lower():
            assert c in COMMAND_BY_CHAR
            command = COMMAND_BY_CHAR[c]
            if command is not None:
                self.execute_command(command)

    def __str__(self):
        current_members = set(self.current_placement.get_members())

        def cell_fn(x, y):
            if (x, y) in current_members:
                assert (x, y) not in self.filled
                return '?'
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


Placement = collections.namedtuple(
    'Placement', 'unit pivot_x pivot_y angle')
# row parity is implicitly determined by pivot_y
# angle is index in unit.even_shapes or unit.odd_shapes
class Placement(Placement):
    def move_e(self):
        return Placement(
            unit=self.unit,
            pivot_x=self.pivot_x + 1,
            pivot_y=self.pivot_y,
            angle=self.angle)

    def move_w(self):
        return Placement(
            unit=self.unit,
            pivot_x=self.pivot_x - 1,
            pivot_y=self.pivot_y,
            angle=self.angle)

    def move_se(self):
        return Placement(
            unit=self.unit,
            pivot_x=self.pivot_x + self.pivot_y % 2,
            pivot_y=self.pivot_y + 1,
            angle=self.angle)

    def move_sw(self):
        return self.move_se().move_w()

    def turn_cw(self):
        return Placement(
            unit=self.unit,
            pivot_x=self.pivot_x,
            pivot_y=self.pivot_y,
            angle=(self.angle + 1) % len(unit.even_shapes))

    def turn_ccw(self):
        return Placement(
            unit=self.unit,
            pivot_x=self.pivot_x,
            pivot_y=self.pivot_y,
            angle=(self.angle - 1) % len(unit.even_shapes))

    def apply_command(self, command):
        return getattr(self, command)()

    def get_shape(self):
        parity = self.pivot_y % 2
        return [self.unit.even_shapes, self.unit.odd_shapes][parity][self.angle]

    def get_members(self):
        shape = self.get_shape()
        dx = self.pivot_x - shape.pivot_x
        dy = self.pivot_y - shape.pivot_y
        assert dy % 2 == 0
        return [(x + dx, y + dy) for x, y in shape.members]


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
        self._compute_bounds()

    def _canonicalize(self):
        dx = -self.pivot_x
        dy = -(self.pivot_y // 2 * 2)

        self.pivot_x += dx
        self.pivot_y += dy
        self.members = tuple((x + dx, y + dy) for x, y in self.members)

        assert self.pivot_x == 0
        assert self.pivot_y in [0, 1]

    def _compute_bounds(self):
        self.min_x = min(x for x, y in self.members)
        self.min_y = min(y for x, y in self.members)
        self.max_x = max(x for x, y in self.members)
        self.max_y = max(y for x, y in self.members)

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

        # TODO: this is shit because it does not take min_y into account
        self.initial_parity = base_shape.pivot_y % 2

        if base_shape.pivot_y % 2:
            base_shape = base_shape.flipped_row_parity()

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

    def get_inital_placement(self, board_width):
        shape = [self.even_shapes, self.odd_shapes][self.initial_parity][0]

        dy = -shape.min_y
        assert dy % 2 == 0

        shape_width = shape.max_x - shape.min_x + 1
        dx = (board_width - shape_width) // 2 - shape.min_x

        dist_to_left = shape.min_x + dx
        dist_to_right = board_width - (shape.max_x + 1 + dx)
        assert dist_to_right - dist_to_left in [0, 1]

        return Placement(
            unit=self,
            pivot_x=shape.pivot_x + dx,
            pivot_y=shape.pivot_y + dy,
            angle=0)


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
    logging.basicConfig(level=logging.DEBUG)

    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_4.json')
    with open(path) as fin:
        data = json.load(fin)
    #pprint.pprint(data)

    seeds = data['sourceSeeds']
    g = Game(data, seeds[0])

    try:
        g.execute_string('ei!' * 100)
    except GameEnded as e:
        print(e)



if __name__ == '__main__':
    main()
