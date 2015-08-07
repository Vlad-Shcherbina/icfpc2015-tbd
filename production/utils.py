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


def gen_output(problem_id, seed, history):
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

    return json.dumps([{
      'problemId': problem_id,
      'seed': seed,
      'solution': "".join(history)
    }])
