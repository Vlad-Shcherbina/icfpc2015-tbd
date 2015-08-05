import sys, os

import nose

from production import testing_utils


if __name__ == '__main__':
    # TODO: "adventurous" mode
    testing_utils.make_hypothesis_reproducible()

    argv = sys.argv + [
        'production',
        '--verbose', '--with-doctest',
        '--logging-level=DEBUG',
        ]
    nose.main(argv=argv)
