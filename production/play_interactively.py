from production.interfaces import CHARS_BY_COMMAND
from production.tkgui import Gui
from production.game import Game 
from production import utils

import json, re, os, os.path

def main():
    path = os.path.join(utils.get_data_dir(), 'qualifier/problem_4.json')
    with open(path) as fin:
        data = json.load(fin)
        m = re.match('.*/problem_(\\d+)\\.json', path)
        assert m
        data['problemId'] = int(m.group(1))

    game = Game(data, data['sourceSeeds'][0])
    ui = Gui(game, buttons=Gui.DEFAULT_BUTTONS_INTERACTIVE)
    
    while True:
        cmd = ui.wait_for_action()
        print('{!r}'.format(cmd))
        if cmd is None:
            print('done')
            break
        game.execute_char(CHARS_BY_COMMAND[cmd][0])
        ui.update(game)
    

if __name__ == '__main__':
    main() 