import sys
import nose

from production.examples import example_module


def test_loading_stuff():
    assert len(example_module.load_example()) > 0


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
