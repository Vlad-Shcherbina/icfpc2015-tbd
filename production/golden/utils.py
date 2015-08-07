import sys
sys.path.append('.')

import calendar
import time
import json
from random import randrange, choice

def unixTime():
    return calendar.timegm(time.gmtime())

def mUnixTime():
    return time.time()

def moves():
    return json.loads("""
    {
    "W": ["p", "'", "!", ".", "0", "3"],
    "E": ["b", "c", "e", "f", "y", "2"],
    "SW": ["a", "g", "h", "i", "j", "4"],
    "SE": ["l", "m", "n", "o", " ", "5"],
    "C": ["d", "q", "r", "v", "z", "1"],
    "CC": ["k", "s", "t", "u", "w", "x"]
    }
    """)

def randomSolution(n=None):
    solution = ""
    ms = moves()
    if n == None:
        n = randrange(0, 100)
    for i in range(n):
        solution += choice( ms[ choice(list(ms)) ] )
    return solution
