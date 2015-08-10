from production.interfaces import COMMAND_BY_CHAR
from production.tkgui import Gui
from production.game import Game 

s = 'R1 O0 P1 Q1 P1 O0 N0 N0 P1 R1 Q1 P1 O0 P1 Q1 R1 P1 N0 N0 Q1 S1 N1 T1 S1 R1 P1 R1 Q1 P1 O0 O0 P1 Q1 R1 P1 N0 N0'

def print_seq():
    for it in s.split():
        c, b = it
        c = c.lower()
        cc = ord(c) - ord('n')
        #print(cc, b)
        print(c, cc, COMMAND_BY_CHAR[c], b)

print_seq()
print()

json = {'width': 20, 'height':20, 'filled': [], 'sourceLength':1, 'units': [{
        'pivot': {'x': 0, 'y': 1}, 'members':[{'x': 0, 'y': 0}]}
        ]}
marks = []
g = Game(json, 0)
ui = Gui(g)
for it in s.split():
    c, b = it
    print(it, COMMAND_BY_CHAR[c.lower()])
    if b == '1':
        marks.append(next(iter(g.get_current_figure_cells())))
    ui.update(g, marks)
    action = ui.wait_for_action()
    if action is None:
        break
    g.execute_char(c)
