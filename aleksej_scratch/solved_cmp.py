import itertools
import os
import json
import pprint
import collections
import logging
import time
import copy
import random
import glob
import requests
import math

from production import big_step_game
from production import utils
from production import interfaces
from production.golden import goldcfg
from production.golden import api


N = 5
MAX_GAMES = 30

def find_interval(values):
    average = 1.0 * sum(values) / len(values)
    variance = sum([(x - average) ** 2 for x in values]) / (len(values) - 1)
    stddev = math.sqrt(variance)
    interval = stddev / math.sqrt(len(values))
    return (average - 2 * interval, average + 2 * interval)


def compare_solver(gen1, gen2):
    gen1 = iter(gen1)
    gen2 = iter(gen2)
    data1 = [next(gen1) for _ in range(N)]
    data2 = [next(gen2) for _ in range(N)]

    count = 0
    while True:
        count += 1
        if count > MAX_GAMES:
            return 0, (a, b), (c, d)
        a, b = find_interval(data1)
        c, d = find_interval(data2)
        # print(max(len(data1), len(data2)), (a, b), (c, d))
        if b < c:
            return -1, (a, b), (c, d)
        if a > d:
            return 1, (a, b), (c, d)
        if b - a > d - c:
            data1.append(next(gen1))
        else:
            data2.append(next(gen2))

def main():
    random.seed(42)
    def f():
        while True:
            yield random.randint(0, 10)

    def g():
        while True:
            yield random.randint(-50, 100)

    a = compare_solver(f(), g())
    print(a)


if __name__ == '__main__':
    main()
