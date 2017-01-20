from six.moves.tkinter import Tk, W, LEFT, Label, Frame

from ship_model import Ship

class EnemyShipPanel(Frame):
    '''The ship panel as seen by the enemy'''
    
    ############## colors ##############
    SHIP_SUNK = "red"
    SHIP_ALIVE = "forest green"
    ####################################
    
    def __init__(self, master):
        Frame.__init__(self, master)
        
        self._create_ui()
        
    def _create_ui(self):
        '''Create the UI elements.'''
        
        self.ship_labels = {}
        i = 0
        
        for short_name, full_name in Ship.NAMES.items():
            self.ship_labels[short_name] = Label(
                self, 
                text=full_name.title(), 
                fg=self.SHIP_ALIVE,
                justify=LEFT,
            )
            self.ship_labels[short_name].grid(row=i, column=0, sticky=W, ipady=5)
            i += 1
            
    def redraw(self, model):
        '''Redraw the panel based on GridModel.
        <model> is an instance of GridModel.'''
        
        for name, ship in model.get_ships().items():
            if ship.is_sunk():
                self.set_sunk(name)
        
    def set_sunk(self, ship_name):
        '''Given the short name for the ship, set it to sunk.
        <ship_name> is the short name for the ship'''
        
        self.ship_labels[ship_name].config(fg=self.SHIP_SUNK)
    
if __name__ == "__main__":
    app = Tk()
    
    f = EnemyShipPanel(app)
    f.pack()
    
    app.mainloop()
