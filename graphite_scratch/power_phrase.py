import json
import logging
import sys

logger = logging.getLogger(__name__)


OPPOSITE_MOVES = [('W', 'E'), ('C', 'CC')]
MOVES = json.loads(open('../data/moves.json').read())
IMPOSSIBLE_PAIRS = set(sum(
    [
        [''.join([c1, c2]) for c1 in MOVES[m1] for c2 in MOVES[m2]] for (m1, m2) in OPPOSITE_MOVES
    ],
    []
))
CHARACTERS = set(sum(MOVES.values(), []))


def is_valid_phrase(phrase):
    phrase = phrase.lower()
    # Start with an invalid character, so joined with normal one it is not
    # listed in impossible pairs.
    pair = '\xff'
    for c in phrase:
        if c not in CHARACTERS:
            return False
        pair = pair[-1] + c
        if pair in IMPOSSIBLE_PAIRS:
            return False
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python power_phrase.py power_phrase1 power_phrase2 ...")
        return
    for p_phrase in sys.argv[1:]:
        print("{}: {}".format(p_phrase, "valid" if is_valid_phrase(p_phrase) else "invalid"))

if __name__ == '__main__':
    main()
