import hashlib
import json
import os


_project_root = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def get_project_root():
    return _project_root


def get_data_dir():
    return os.path.join(_project_root, 'data')


def count_substrings(s, ss):
    '''
    Counts overlapping occurrences as well.

    >>> count_substrings('ababa', 'aba')
    2
    >>> count_substrings('ababa', 'zz')
    0
    >>> count_substrings('aaqqaa', 'a')
    4
    '''
    assert ss

    result = 0
    i = 0
    while True:
        j = s.find(ss, i)
        if j == -1:
            break

        result += 1
        i = j + 1

    return result


# TODO: just call gen_output_raw
def gen_output(game, game_ended_excp):
    '''
    [ { "problemId": number   /* The `id` of the game configuration */
      , "seed":      number   /* The seed for the particular game */
      , "tag":       string   /* A tag for this solution. */
      , "solution":  Commands
      }
    ]

    The tag field is meant to allow teams to associate scores on the
    leaderboards with specific submitted solutions. If no tag field is
    supplied, a tag will be generated from the submission time.
    '''

    assert game.problem_id >= 0, 'Missing problem id'
    solution = "".join(game.history)
    tag = str((game.problem_id, game.seed, solution))
    tag = hashlib.md5(tag.encode('utf-8')).hexdigest()
    tag += ' %d:%d:%d' % (
        game_ended_excp.move_score, game_ended_excp.power_score,
        game_ended_excp.total_score)
    return {
      'problemId': game.problem_id,
      'seed': game.seed,
      'solution': solution,
      'tag': tag
    }


def gen_output_raw(id, seed, commands, move_score, power_score, tag_prefix=''):
    '''
    [ { "problemId": number   /* The `id` of the game configuration */
      , "seed":      number   /* The seed for the particular game */
      , "tag":       string   /* A tag for this solution. */
      , "solution":  Commands
      }
    ]

    The tag field is meant to allow teams to associate scores on the
    leaderboards with specific submitted solutions. If no tag field is
    supplied, a tag will be generated from the submission time.
    '''

    assert id >= 0, 'Missing problem id'
    tag = str((id, seed, commands))
    tag = hashlib.md5(tag.encode('utf-8')).hexdigest()
    tag += ' %d:%d:%d' % (
        move_score, power_score,
        move_score + power_score)
    return {
      'problemId': id,
      'seed': seed,
      'solution': commands,
      'tag': tag_prefix + tag
    }
