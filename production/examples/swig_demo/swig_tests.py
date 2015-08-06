from nose.tools import eq_

from production.examples.swig_demo import sample


def test_stuff():
    eq_(sample.N, 42)
    eq_(sample.square_float(2), 4)
    eq_(sample.reverse([1, 2, 3]), (3, 2, 1))
