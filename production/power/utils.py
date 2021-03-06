from production import game
from production import utils
from production.interfaces import GameEnded
import os
import json


# Accepts a potential power phrase and returns None if it is impossible to build
# or tuple for httpSubmitOwn otherwise.
def get_phrase_submission(phrase, problem=24):
    phrase = phrase.lower()
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_%d.json' % problem)
    with open(path) as fin:
        data = json.load(fin)
        data['problemId'] = problem
    g =  game.Game(data, data['sourceSeeds'][0])
    c = 'm' if phrase[0] == 'l' else 'l'
    c *= 5
    try:
        g.execute_string(c + phrase)
    except (GameEnded, KeyError):
        return None
    c = 'm' if phrase[-1] == 'l' else 'l'
    try:
        while True:
            g.execute_char(c)
    except GameEnded as e:
        solution = utils.gen_output(g, e)
        result = {
            'score': e.move_score,
            'powerScore': e.power_score,
            'tag': solution['tag'],
            'problemId': solution['problemId'],
            'seed': solution['seed'],
            'solution': solution['solution']
        }
        return (solution, result)
