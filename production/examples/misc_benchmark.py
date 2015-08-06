import timeit

from production.examples.naive_misc import NaiveMisc
from production.examples.cpp_misc.cpp_misc import CppMisc


def main():
    for Machine in NaiveMisc, CppMisc:
        nm = Machine(16)
        for i in range(2**nm.word_size):
            nm.set_word(i, (i * 117) % 2**nm.word_size)

        start = timeit.default_timer()

        nm.simulate(10**7)

        print(nm.get_ip())

        print(Machine.__name__, 'took', timeit.default_timer() - start, 's')


if __name__ == '__main__':
    main()
