from production.interfaces import IGame, Action       

import math
import tkinter
from tkinter import Tk, Text, Frame, Label, Button, Canvas
from tkinter.font import Font
import logging
log = logging.getLogger(__name__)


class GameMock(IGame):
    @property
    def width(self): return 10
    @property
    def height(self): return 15
    @property
    def score(self): return 666
    @property
    def turn(self): return 42
    # methods
    def get_filled(self):
        return [(0, 0), (1, 0), (0, 1), 
                (0, self.height - 1), (1, self.height - 1), (0, self.height - 2),  
                (self.width - 1, self.height - 1), (self.width - 2, self.height - 1), (self.width - 1, self.height - 2),  
                (self.width - 1, 0), (self.width - 2, 0), (self.width - 1, 1)]
    def get_current_figure_cells(self):
        return [(4, 0), (4, 1), (4, 2), (5, 2)]
    def get_current_figure_pivot(self):
        return (5, 1)


class Gui(object):
    CELL_SIZE = 32 # you can globally customize it for your display.
    DEFAULT_STATS = [
            ('Score', lambda game: game.score),
            ('Turn', lambda game: game.turn),
            ]
    
    DEFAULT_BUTTONS_CONTINUE=[
            ('Continue', '<space>', 'continue'),
            ]
    
    DEFAULT_BUTTONS_INTERACTIVE=[
            ('Turn CCW', 'w', Action.ccw),
            ('Turn CW', 'e', Action.cw),
            ('Move west', 'a', Action.w),
            ('Move east', 'd', Action.e),
            ('Move south-west', 'z', Action.sw),
            ('Move south-east', 'x', Action.se),
            ]
    
    def __init__(self, game, stats=DEFAULT_STATS, buttons=DEFAULT_BUTTONS_CONTINUE):
        self.action = None
        self.root = root = Tk()
        root.title('Iä! Shub-Niggurath! The Black Goat of the Woods with a Thousand Young!')
        root.protocol("WM_DELETE_WINDOW", self.close)
        
        root.pack_propagate(True)
        
        self.grid_canvas = Canvas(root, bd=5, relief=tkinter.SUNKEN)
        self.grid_canvas.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        
        button_frame = Frame(root)
        button_frame.pack(fill=tkinter.BOTH, side=tkinter.LEFT)
        
        stat_frame = Frame(button_frame, bd=1)
        stat_frame.pack(fill=tkinter.BOTH)
        stat_frame.columnconfigure(1, weight=1)
        self.stat_textboxes = stat_textboxes = []
        for row, (text, callback) in enumerate(stats):
            label = Label(stat_frame, text=text + ':', anchor='e')
            label.grid(row=row, column=0, sticky='wens')
            textbox = Label(stat_frame, bd=1, relief=tkinter.SUNKEN)
            textbox.callback = callback # for our own use.
            textbox.grid(row=row, column=1, sticky='wens')
            stat_textboxes.append(textbox)

        for name, bindings, action in buttons:
            def callback(event, action=action):
                if self.action is not None:
                    log.error('Action already set: %r when processing %r', self.action, action)
                self.action = action
                root.quit()
            text = name + (' ({})'.format(bindings) if bindings else '')            
            button = Button(button_frame, text=text, command=lambda:callback(None))
            button.pack()
            for it in bindings.split():
                root.bind(it, callback)
        
        if game is not None:
            self.update(game)
    
    
    def update(self, game):
        tri_step_x = self.CELL_SIZE * 0.5
        tri_step_y = self.CELL_SIZE * 0.5 * math.tan(math.pi / 6) 
        def tri(x, y):
            return tri_step_x * x, tri_step_y * y
        def hex_center(x, y):
            tri_x = 1 + 2 * x + (y & 1) 
            tri_y = 2 + 3 * y
            return tri_x, tri_y
        def hexagon(x, y):
            cx, cy = hex_center(x, y)
            r = []
            r.extend(tri(cx - 1, cy - 1))
            r.extend(tri(cx    , cy - 2))
            r.extend(tri(cx + 1, cy - 1))
            r.extend(tri(cx + 1, cy + 1))
            r.extend(tri(cx    , cy + 2))
            r.extend(tri(cx - 1, cy + 1))
            return r
        def circle_bb(x, y, r):
            cx, cy = tri(*hex_center(x, y))
            r = r / 2
            return ((cx - r, cy - r),
                    (cx + r, cy + r))
            
        filled = set(game.get_filled())
        figure_cells = set(game.get_current_figure_cells())
        pivot = game.get_current_figure_pivot()
        default_bg = self.root.cget('bg')
        c = self.grid_canvas
        c.delete(tkinter.ALL)
        for y in range(game.height):
            for x in range(game.width):
                cell = (x, y)
                assert not ((cell in filled) and (cell in figure_cells))  
                bg_color = (
                        '#4040A0' if cell in filled else 
                        '#40A040' if cell in figure_cells else 
                        default_bg)
                c.create_polygon(*hexagon(x, y), fill=bg_color, outline='#000000', width=1)
        c.create_oval(*circle_bb(*pivot, r=self.CELL_SIZE * 0.5), fill='#FF0000', outline='#FFFFFF', width=2)
        c_bbox = c.bbox(tkinter.ALL)
        c.config(scrollregion=c_bbox, width=c_bbox[2] - c_bbox[0], height=c_bbox[3] - c_bbox[1])
        
                
        for textbox in self.stat_textboxes:
            textbox.config(text=textbox.callback(game))

    
    def wait_for_action(self):
        self.action = None
        self.root.mainloop()
        return self.action

    
    def close(self):
        if self.root:
            self.root.destroy()
            self.root = None


def main(game=None):
    if game is None: game = GameMock()
    gui = Gui(game)
    while True:
        cmd = gui.wait_for_action()
        print('{!r}'.format(cmd))
        if cmd is None:
            print('done')
            break


if __name__ == '__main__':
    main()
