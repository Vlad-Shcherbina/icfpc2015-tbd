
import argparse
import itertools
import os
import json
import pprint
import collections
import logging
import time
import random
import sys

from production import utils

logger = logging.getLogger(__name__)

def read_json(filename):
    path = os.path.join(utils.get_data_dir(), 'golden_tests', filename)
    with open(path) as f:
        return json.load(f)

def main():
    print('%-45s => %s' % ('Tag', 'Filename'))
    print('=' * 100)
    files = os.listdir(os.path.join(utils.get_data_dir(), 'golden_tests'))
    result = []
    for f in files:
        data = read_json(f)[0]
        result.append('%-45s => %s' % (data['tag'], f))
    for line in sorted(result):
        print(line)


if __name__ == '__main__':
    main()
