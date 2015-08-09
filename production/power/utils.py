from production import game
from production import utils
from production.interfaces import GameEnded
import os
import json


def check_phrase(phrase):
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_24.json')
    with open(path) as fin:
        data = json.load(fin)
        data['problemId'] = 24
    g =  game.Game(data, data['sourceSeeds'][0])
    try:
        g.execute_string(phrase)
    except GameEnded:
        return None
    try:
        while True:
            g.execute_char('l')
    except GameEnded as e:
        return utils.gen_output(g, e)

print(check_phrase("yuggoth"))
