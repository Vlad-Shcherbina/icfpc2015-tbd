from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum

from production import utils


class IGame:
    'Abstract base class for Game State'
    __metaclass__ = ABCMeta
    # properties
    @abstractproperty
    def width(self):
        'The number of columns on the board'
    @abstractproperty
    def height(self):
        'The number of rows on the board'
    @abstractproperty
    def score(self):
        'Current score'
    @abstractproperty
    def turn(self):
        'Current turn'
    # methods
    @abstractmethod
    def get_filled(self):
        'Return an iterable of (x, y) tuples representing filled cells'
    @abstractmethod
    def get_current_figure_cells(self):
        'Return an iterable of (x, y) tuples representing cells of the current figure (transformed to the field coordinates)'
    @abstractmethod
    def get_current_figure_pivot(self):
        'Return an (x, y) tuple representing the pivot of the current figure (transformed to the field coordinates)'
        

class Action(str, Enum):
    w = 'move_w'
    e = 'move_e'
    sw = 'move_sw'
    se = 'move_se'
    cw = 'turn_cw'
    ccw = 'turn_ccw'


COMMAND_CHARS =[
    ("p'!.03", Action.w),
    ('bcefy2', Action.e),
    ('aghij4', Action.sw),
    ('lmno 5', Action.se),
    ('dqrvz1', Action.cw),
    ('kstuwx', Action.ccw),
    ('\t\n\r', None),
]
COMMAND_BY_CHAR = {char: cmd for chars, cmd in COMMAND_CHARS for char in chars}
CHARS_BY_COMMAND = {cmd: chars for chars, cmd in COMMAND_CHARS if cmd}

POWER_PHRASES = ["Ei!", "Ia! Ia!", "R'lyeh", "Yuggoth"]
POWER_PHRASES = [w.lower() for w in POWER_PHRASES]


class GameEnded(Exception):
    def __init__(self, move_score, power_score, reason):
        self.move_score = move_score
        self.power_score = power_score
        self.total_score = move_score + power_score
        self.reason = reason

    def __str__(self):
        return 'GameEnded(score = {} + {} = {}, reason={!r})'.format(
            self.move_score, self.power_score, self.total_score,
            self.reason)


def compute_power_score(s):
    assert s.lower() == s, s

    result = 0
    for p in POWER_PHRASES:
        reps = utils.count_substrings(s, p)
        power_bonus = 300 if reps > 0 else 0
        result += 2 * len(p) * reps + power_bonus

    return result
