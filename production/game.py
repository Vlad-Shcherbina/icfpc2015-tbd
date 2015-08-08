import itertools
import os
import json
import pprint
import collections
import logging
import time

from production import utils
from production.interfaces import CHARS_BY_COMMAND, COMMAND_BY_CHAR, COMMAND_CHARS, POWER_PHRASES
from production.interfaces import GameEnded, Action, IGame 


logger = logging.getLogger(__name__)


# backward compatibility
MOVE_W   = Action.w
MOVE_E   = Action.e
MOVE_SW  = Action.sw
MOVE_SE  = Action.se
TURN_CW  = Action.cw
TURN_CCW = Action.ccw


class Game(object):

    # TODO: reduce initialization to primitive operations, so that C++
    # implementation does not have to deal with json.
    def __init__(self, json_data, seed):
        # This is an attribute we add by hand so we have to make sure it
        # exists.
        self.problem_id = json_data['problemId'] \
            if 'problemId' in json_data else -1

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
        self.remaining_units = json_data['sourceLength']

        self.seed = seed
        self.lcg = list(itertools.islice(lcg(seed), 0, self.remaining_units))

        # list of chars (not a single string to avoid quadratic string
        # building behavior)
        self.history = []

        self.move_score = 0
        self.ls_old = 0

        self.current_unit = None
        self.current_placement = None
        self.used_placements = None
        self.pick_next_unit()
        self.game_ended = None

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
            self._end_game(
                move_score=self.move_score,
                power_score=self.power_score(),
                reason="no more units")
        self.remaining_units -= 1

        x = self.lcg[0]
        self.lcg.pop(0)
        self.current_unit = self.units[x % len(self.units)]
        self.current_placement = \
            self.current_unit.get_inital_placement(self.width)
        self.visited_placements = {self.current_placement}
        if not self.can_place(self.current_placement):
            self._end_game(
                move_score=self.move_score,
                power_score=self.power_score(),
                reason="can't spawn new unit")

    def lock_unit(self):
        logger.info('locking unit in place:\n' + str(self))
        assert self.can_place(self.current_placement)
        for x, y in self.current_placement.get_members():
            self.filled.add((x, y))

        ls = self.collapse_rows()

        size = len(self.current_placement.get_shape().members)
        points = size + 100 * (1 + ls) * ls // 2
        if self.ls_old > 1:
            line_bouns = (self.ls_old - 1) * points // 10
        else:
            line_bouns = 0
        self.move_score += points + line_bouns
        self.ls_old = ls

        self.pick_next_unit()

    def collapse_rows(self):
        cnt_in_row = [0] * self.height
        for x, y in self.filled:
            cnt_in_row[y] += 1

        updated_y = {}
        y1 = self.height - 1
        for y in reversed(range(self.height)):
            if cnt_in_row[y] != self.width:
                assert y1 >= 0
                updated_y[y] = y1
                y1 -= 1

        new_filled = set()
        for x, y in self.filled:
            if y in updated_y:
                new_filled.add((x, updated_y[y]))

        cells_destroyed = len(self.filled) - len(new_filled)
        assert cells_destroyed >= 0
        assert cells_destroyed % self.width == 0

        rows_collapsed = cells_destroyed // self.width
        logging.info('collapsing {} rows'.format(rows_collapsed))

        self.filled = new_filled
        return rows_collapsed

    def _end_game(self, move_score, power_score, reason):
        self.game_ended = GameEnded(
            move_score=move_score, power_score=power_score, reason=reason)
        raise self.game_ended

    def _execute_command(self, command):
        # not a public interface, because it does not keep track of
        # phrases of power
        logging.info('execute_command {}'.format(command))
        new_placement = self.current_placement.apply_command(command)
        if self.can_place(new_placement):
            self.current_placement = new_placement

            if new_placement in self.visited_placements:
                self._end_game(
                    move_score=0, power_score=0,
                    reason='placement repeated')
            self.visited_placements.add(new_placement)
        else:
            self.lock_unit()

    def execute_char(self, c):
        c = c.lower()
        self.history.append(c)
        command = COMMAND_BY_CHAR[c]
        if command is not None:
            self._execute_command(command)

    def execute_string(self, s):
        for c in s:
            self.execute_char(c)

    def power_score(self):
        s = ''.join(self.history)
        assert s.lower() == s, s

        result = 0
        for p in POWER_PHRASES:
            reps = utils.count_substrings(s, p)
            power_bonus = 300 if reps > 0 else 0
            result += 2 * len(p) * reps + power_bonus

        return result

    def render_cell(self, x, y):
        current_members = set(self.current_placement.get_members())
        if (x, y) in current_members:
            assert (x, y) not in self.filled
            return '?'
        if (x, y) in self.filled:
            return '*'
        else:
            return '.'

    def render_grid(self):
        return render_hex_grid(self.width, self.height, self.render_cell)

    def __str__(self):
        return self.render_grid()

    def show_units(self):
        result = '{} units:\n'.format(len(self.units))
        for unit in self.units:
            result += str(unit)
            result += '---\n'
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
            angle=(self.angle + 1) % len(self.unit.even_shapes))

    def turn_ccw(self):
        return Placement(
            unit=self.unit,
            pivot_x=self.pivot_x,
            pivot_y=self.pivot_y,
            angle=(self.angle - 1) % len(self.unit.even_shapes))

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
        self.min_x = min(x for x, y in self.members)  # @UnusedVariable
        self.min_y = min(y for x, y in self.members)
        self.max_x = max(x for x, y in self.members)
        self.max_y = max(y for x, y in self.members)

    def __str__(self):
        extended_members = self.members + ((self.pivot_x, self.pivot_y),)
        min_x = min(x for x, y in extended_members)  # @UnusedVariable
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
        g.execute_string('i5' * 100)
    except GameEnded as e:
        print(e)


if __name__ == '__main__':
    main()
