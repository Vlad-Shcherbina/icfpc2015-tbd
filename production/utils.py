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
