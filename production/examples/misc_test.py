import sys
import unittest
import logging

logger = logging.getLogger(__name__)

import nose
from nose.tools import eq_
import hypothesis
import hypothesis.strategies as st

from production.examples.naive_misc import NaiveMisc
from production.examples.cpp_misc.cpp_misc import CppMisc
from production import testing_utils


def canonical_str(m):
    assert m.__class__.__name__.endswith('Misc')
    return str(m).replace(m.__class__.__name__, '*Misc')


def rotate_machine(m, rot):
    n = 2**m.word_size
    m2 = m.__class__(m.word_size)
    m2.set_ip((m.get_ip() + rot) % n)
    for i in range(n):
        m2.set_word((i + rot) % n, m.get_word(i))
    return m2


class CommonMiscTests(object):

    Machine = None

    # Unnecessary for NaiveMisc, but decorating CppMisc tests conditionally
    # is messy.
    @testing_utils.isolate_process_failures()
    def test_minimal(self):
        m = self.Machine(2)
        m.set_word(0, 1)
        m.set_word(1, 0)
        m.set_word(2, 3)
        m.set_word(3, 2)
        eq_(canonical_str(m), '*Misc(ip=0, memory=[1, 0, 3, 2])')

        m.step()

        eq_(canonical_str(m), '*Misc(ip=0, memory=[1, 2, 3, 2])')

    @hypothesis.given(
        word_size=st.integers(2, 8),
        memory=st.streaming(st.integers(0, 2**8)),
        num_steps=st.integers(min_value=0, max_value=100),
        rot=st.integers(-100, 100))
    @testing_utils.isolate_process_failures()
    def test_rotation_invariance(self, word_size, memory, num_steps, rot):
        m1 = self.Machine(word_size)
        for i in range(2**word_size):
            m1.set_word(i, memory[i] % 2**word_size)

        m2 = self.Machine(word_size)
        for i in range(2**word_size):
            m2.set_word(i, memory[i] % 2**word_size)

        eq_(str(m1), str(m2))

        m1.simulate(num_steps)
        m1 = rotate_machine(m1, rot * 4)

        m2 = rotate_machine(m2, rot * 4)
        m2.simulate(num_steps)

        eq_(str(m1), str(m2))


class NaiveMiscTests(unittest.TestCase, CommonMiscTests):
    Machine = NaiveMisc


class CppMiscTests(unittest.TestCase, CommonMiscTests):
    Machine = CppMisc


class MiscEquivalenceTests(unittest.TestCase):

    @hypothesis.given(
        word_size=st.integers(2, 8),
        memory=st.streaming(st.integers(0, 2**8)),
        num_steps=st.integers(min_value=0, max_value=100))
    @testing_utils.isolate_process_failures()
    def misc_equivalence_test(self, word_size, memory, num_steps):
        m1 = NaiveMisc(word_size)
        for i in range(2**word_size):
            m1.set_word(i, memory[i] % 2**word_size)

        m2 = CppMisc(word_size)
        for i in range(2**word_size):
            m2.set_word(i, memory[i] % 2**word_size)

        logger.info('start configuration: {}'.format(canonical_str(m1)))
        eq_(canonical_str(m1), canonical_str(m2))

        logger.info('simulating {} steps'.format(num_steps))
        m1.simulate(num_steps)
        m2.simulate(num_steps)

        eq_(canonical_str(m1), canonical_str(m2))


if __name__ == '__main__':
    nose.run_exit(argv=[
        sys.argv[0], __file__,
        '--verbose', '--with-doctest', '--logging-level=DEBUG'
    ])
