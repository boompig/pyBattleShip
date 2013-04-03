'''
Written by Daniel Kats
March 4, 2013
'''

#################
#    IMPORTS    #
#################

from ship_model import Ship
from Tkinter import *

####################
#    MAIN CLASS    #
####################

class ShipPlacementPanel(Frame):
    '''A frame which contains visualizations for placing ships.'''
    
    # the size of a single tile
    SHIP_TILE_SIZE = 20
    SHIP_TILE_COLOR = "steel blue"
    TAG = "staging_ship"
    CANVAS_WIDTH = 150

    def __init__(self, master):
        '''Create a new panel with the given parent.'''
    
        Frame.__init__(self, master)
        self._ship_name = StringVar()
        self._create_ui()
        self.reset()
        
    def reset(self):
        '''Alias for unstage_all'''
        
        self.unstage_all()
    
    def _create_ui(self):
        '''Create all UI objects.'''
    
        #self._tl = Label(self, text="Staged Ship", f)
        self._sl = Label(self, textvariable=self._ship_name)
        self._c = Canvas(self)
        self._c.config(width=self.CANVAS_WIDTH)
        self._rb = Button(self, text="Rotate", command=self.rotate_current_ship)
        
        self.pack_ui()
        
    def pack_ui(self):
        '''(re) pack the UI.
        Created mostly to counter hiding by unpacking.'''
    
        #self._tl.pack()
        #self._tl.grid(row=0)
        self._sl.pack()
        self._sl.grid(row=1, pady=10)
        self._c.pack()
        self._c.grid(row=2, pady=15)
        self._rb.pack()
        self._rb.grid(row=3)
        
    def unstage_all(self):
        '''Remove all ships from staging area.
        Clear all staging preferences.'''
        
        self._staged_ship = None
        self._clear_staging_grid()
        self._ship_name.set("")
        self._disable_rotate_button()
        
    def _clear_staging_grid(self):
        '''Remove previously staged ships from staging grid.'''
    
        for item in self._c.find_withtag(self.TAG):
            self._c.delete(item)
        
    def _draw_staged_ship(self):
        '''Draw the currently staged ship.'''
        
        # remove prior drawings
        self._clear_staging_grid()
        
        if self._staged_ship.is_vertical():
            x = 0
            x_pad = (self._c.winfo_width() - self.SHIP_TILE_SIZE) / 2.0
            y_pad = (self._c.winfo_height() - self.SHIP_TILE_SIZE * self._staged_ship.get_size()) / 2.0
        
            for y in range(self._staged_ship.get_size()):
                self._draw_ship_tile(
                    x_pad + x * self.SHIP_TILE_SIZE, 
                    y_pad + y * self.SHIP_TILE_SIZE)
        else:
            y = 0
            x_pad = (self._c.winfo_width() - self.SHIP_TILE_SIZE * self._staged_ship.get_size()) / 2.0
            y_pad = (self._c.winfo_height() - self.SHIP_TILE_SIZE) / 2.0
            
            for x in range(self._staged_ship.get_size()):
                self._draw_ship_tile(
                    x_pad + x * self.SHIP_TILE_SIZE, 
                    y_pad + y * self.SHIP_TILE_SIZE)
        
    def add_ship(self, s):
        '''Alias for stage ship.'''
        
        self.stage_ship(s)
        
    def _disable_rotate_button(self):
        '''Disable / hide the rotate button.'''
        
        self._rb.grid_forget()
        
    def _enable_rotate_button(self):
        '''Enable / show the rotate button.'''
        
        self._rb.grid(row=3)
        
    def stage_ship(self, s):
        '''Add a ship to the staging area. 
        Display what it would look like on the grid.
        Create support for accidentally adding ship that isn't ready'''
        
        if s is not None:
            self._staged_ship = s
            self._ship_name.set(s.get_full_name().title())
            self._draw_staged_ship()
            
            self._enable_rotate_button()
        else:
            self._disable_rotate_button()
        
    def _draw_ship_tile(self, x, y):
        '''Draw a single tile for the ship at given coordinates.'''
        
        self._c.create_rectangle(
            x,
            y,
            x + self.SHIP_TILE_SIZE,
            y + self.SHIP_TILE_SIZE,
            fill=self.SHIP_TILE_COLOR,
            outline="black",
            tag=self.TAG
        )
        
    def get_staged_ship(self):
        '''Return the currently staged ship.'''
        
        return self._staged_ship
        
    def rotate_current_ship(self):
        '''Rotate the currently staged ship.'''
        
        if self._staged_ship is not None:
            self._staged_ship.rotate()
            self._draw_staged_ship()
        
        