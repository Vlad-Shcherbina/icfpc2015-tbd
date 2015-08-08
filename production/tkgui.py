from production.interfaces import IGame, Action       

import tkinter
from tkinter import Tk, Text, Frame, Label, Button
from tkinter.font import Font
import logging
logger = logging.getLogger(__name__)


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
        
        self.grid_frame = Frame(root, bd=5, relief=tkinter.SUNKEN)
        self.grid_width = self.grid_height = None
        self.grid = []
        
        self.grid_frame.grid_propagate(False)
        self.grid_frame.pack(expand=True, fill=tkinter.BOTH, side=tkinter.LEFT)
        
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
                    logger.error('Action already set: %r when processing %r', self.action, action)
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
        if self.grid_width != game.width or self.grid_height != game.height:
            for it in self.grid:
                it.destroy()
            self.grid = []
            self.grid_width = game.width
            self.grid_height = game.height
            for y in range(self.grid_height):
                column_offset = y % 2
                for x in range(self.grid_width):
                    label = Label(self.grid_frame, bd=2, relief=tkinter.RAISED, width=1)
                    label.grid(row=y, column=x * 2 + column_offset, columnspan=2, sticky='wens')
                    self.grid.append(label)
                label = Label(self.grid_frame, bd=2, relief=tkinter.RAISED, width=0)
                if column_offset:
                    label.grid(row=y, column=0, columnspan=1, sticky='wens')
                else:
                    label.grid(row=y, column=self.grid_width * 2, columnspan=1, sticky='wens')
                
            for x in range(self.grid_width * 2 + 1):
                self.grid_frame.columnconfigure(x, weight=1)
            for y in range(self.grid_height):
                self.grid_frame.rowconfigure(y, weight=1)
                
            self.grid_frame.config(
                    width=self.CELL_SIZE * (self.grid_width * 2 + 1) // 2,
                    height=self.CELL_SIZE * self.grid_height)
        
        filled = set(game.get_filled())
        figure_cells = set(game.get_current_figure_cells())
        pivot = game.get_current_figure_pivot()
        default_bg = self.root.cget('bg')
        label_iter = iter(self.grid)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                label = next(label_iter)
                cell = (x, y)
                assert not ((cell in filled) and (cell in figure_cells))  
                bg_color = (
                        '#4040A0' if cell in filled else 
                        '#40A040' if cell in figure_cells else 
                        default_bg)
                text = 'X' if cell == pivot else ''                
                label.config(bg=bg_color, text=text)
                
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
