'''
Written by Daniel Kats
March 4, 2013
'''

from Tkinter import LEFT, Frame
from ship_model import Ship


class PlayerController(object):
    '''Controller for this player's grid.
    Take care of all methods for the grid'''
    
    def __init__(self, f):
        '''Create a new controller for the PlayerGridFrame in f.'''
        
        self._f = f
        
    def get_selected_placement_ship(self):
        '''Return the ship selected to be placed.
        Return the short name of the ship.'''
        
        return self._f.ship_panel.get_current_ship()

class PlayerGridFrame(Frame):
    '''The UI manager for all of the player's possible actions with their grid.
    '''

    def __init__(self, master):
        Frame.__init__(self, master)
        
    def _create_ui(self):
        '''Add the items to the UI.'''
        
        for item in [self._ship_panel, self._grid, self._staging_panel]:
            if item is not None:
                item.pack(side=LEFT)
                
    def _bind_staging_events(self):
        '''Bind all the staging events.'''
        
        for s in Ship.SHORT_NAMES:
            self._ship_panel.bind_event(s, self.stage_current_ship)
            
    def _bind_placing_events(self):
        '''Bind all ship placing events.'''
        
        for x, y in self._grid.get_tiles():
            self._bind_placing_event(x, y)
            
    def _bind_placing_event(self, x, y):
        f = lambda: self.add_staged_ship(x, y)
        self._grid.bind_tile(x, y, f)
        
    def stage_current_ship(self):
        '''Stage the currently selected ship in the staging area.
        If no ship selected, do nothing.'''
        
        ship = self._get_current_ship()
        if ship is not None:
            self._staging_panel.stage_ship(Ship(0, 0, ship, True))
        
    def _get_current_ship(self):
        '''Return the currently selected ship.
        If nothing currently selected, return None'''
        
        return self._ship_panel.get_current_ship()
        
    def add_staged_ship(self, x, y):
        '''Add the ship in the staging area to the grid.
        (x, y) refer to location on the grid where to add.
        If no ship staged, do nothing.'''
        
        ship = self._staging_panel.get_staged_ship()
        if ship is not None:
            if self._grid.add_ship(x, y, ship.get_short_name(), ship.is_vertical()):
                self._ship_panel.set_placed(ship.get_short_name())
                
                if self._grid.all_placed():
                    #TODO notify observers
                    #print "Everything is placed"
                    pass
