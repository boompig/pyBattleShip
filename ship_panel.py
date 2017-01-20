'''
Written by Daniel Kats
March 4, 2013
'''

#################
#    IMPORTS    #
#################

from ship_model import Ship
from six.moves.tkinter import N, E, S, W, Tk, Frame, Radiobutton, IntVar

####################
#    MAIN CLASS    #
####################

class ShipPanel(Frame):
    '''
    Panel that keeps track of your ships as they get placed onto the board.
    '''

    ########### geometry ##########
    WIDTH = 150
    ###############################
    
    ########### states ############
    UNPLACED = 0
    PLACED = 1
    SUNK = 2 # <-- should be unused
    ###############################
    
    ########### colors ############
    UNPLACED_COLOR = "black"
    PLACED_COLOR = "forest green"
    SUNK_COLOR = "red" #<-- should be unused
    ###############################

    def __init__(self, master):
        '''Create a new ship panel.
        <master> is the parent TKinter element.'''
        
        Frame.__init__(self, master)
        self._create_ui()
        #self.reset()
        
    def _create_ui(self):
        '''Create the UI for this panel.'''
        
        self._ship_var = IntVar()
        self.ship_buttons = {}
        
        for i, ship in enumerate(Ship.SHORT_NAMES):
            b = Radiobutton(
                self, 
                text=Ship.NAMES[ship].title(), 
                value=i, 
                variable=self._ship_var, 
                indicatoron=False
            )
            b.pack(anchor=W, pady=10)
            b.grid(sticky=N + S + E + W)
            
            # and a sort-of experimental feature...
            b.ship_state = self.UNPLACED
            
            # save it
            self.ship_buttons[ship] = b
        
    def reset(self):    
        '''Return this panel to its starting state.'''
        
        self.unselect_ship()
        for ship in Ship.SIZES.keys():
            self.set_state(ship, self.UNPLACED)
        
    @staticmethod
    def get_state_color(state):
        '''Return the color based on the state.'''
    
        return {
            ShipPanel.UNPLACED : ShipPanel.UNPLACED_COLOR,
            ShipPanel.PLACED : ShipPanel.PLACED_COLOR,
            ShipPanel.SUNK : ShipPanel.SUNK_COLOR
        } [state]
        
    def redraw(self, model):
        '''Redraw the entire panel based on the model.
        <model> is the ship grid.'''
        
        for ship_name in model.get_ship_placement().keys():
            self.set_placed(ship_name)
        
    def click(self, ship):
        '''Click given button.'''
        
        self.ship_buttons[ship].invoke()
    
    def set_state(self, ship, state):
        '''Change the state of the given ship.'''
        
        self.ship_buttons[ship].ship_state = state
        self.ship_buttons[ship].config(foreground=self.get_state_color(state))
        
    def set_placed(self, ship):
        '''Set the ship as placed.'''
        
        self.set_state(ship, self.PLACED)
        
    def set_sunk(self, ship):
        '''Set the ship as sunk.'''
        
        self.set_state(ship, self.SUNK)
        
    def unselect_ship(self):
        '''Unselect all ships.'''
        
        self._ship_var.set(len(Ship.SHIPS) + 1)
        
    def get_current_ship(self):
        '''Return the ship currently selected.'''
        
        if self._ship_var.get() > len(Ship.SHIPS):
            return None
        else:
            return Ship.SHORT_NAMES[self._ship_var.get()]
        
def a(panel):
    panel.set_sunk("a")
    
def b(panel):
    panel.set_placed("b")
        
if __name__ == "__main__":
    root = Tk()
    
    f = ShipPanel(root)
    f.pack()
    
    f1 = lambda: a(f)
    f2 = lambda: b(f)
    f.bind_event("a", f1)
    f.bind_event("b", f2)
    
    root.mainloop()
        
    
        
