from Tkinter import *
from ship_model import Ship, ShipLoader
import time
from grid_model import GridModel
from ship_ai import ShipAI
from ship_placement_panel import ShipPlacementPanel
from ship_grid import ShipGrid
from ship_war_panel import ShipWarPanel
from ship_panel import ShipPanel
from player_controller import PlayerController
import mock1

class GameController(object):
    '''
    This class is only used as a middle-man for communication with the model.
    When the GUI does not need the model, it processes its own events.
    '''
    
    ############ flags ##################
    ''' set this to True if you want to see the dev menu
        The dev menu has these and other features:
            - skip parts of the game so you can "join" at a certain point"
            - simulate events
        '''
    DEV_FLAG = True
    #####################################

    def __init__(self): 
        '''Create a main controller for the game.
        Create the GUI. Run the game.'''
        
        # create the UI
        app = Tk()
    
        self._game_frame = mock1.Game(app)
        self._game_frame.pack(fill=BOTH, expand=1)
        self._game_frame.grab_set()
        self._game_frame.focus_set()
        
        # set initial variables
        self.new_game_callback()

        # add events
        self.create_hooks()
        
        # run the game
        app.mainloop()
        
    def _hi(self, event=None):
        '''Small and convenient debugging method.'''
    
        print "hi"
        
    def exit_callback(self, event=None):
        '''Quit the game by closing the parent window.'''
        
        self._game_frame.master.destroy()
        
    def _create_keyboard_shortcuts(self):
        '''Create the game's keyboard shortcuts.'''
        
        d = {
            "P" : self.autoplace_ships_callback,
            "<space>" : self.play_callback,
            "X" : self.exit_callback,
            "N" : self.new_game_callback,
            "?" : lambda event: self._game_frame.show_keyboard_shortcuts()
        }
        
        for key_binding, fn in d.iteritems():
            print "{} <-- {}".format(key_binding, fn.__name__)
            self._game_frame.master.bind(key_binding, fn) # has to be master
        
    def warn_hi(self):
        self._game_frame.show_warning("hi")
        
    def create_hooks(self):
        '''Create listeners (hooks) to the GUI for relevant items.'''
        
        self._create_keyboard_shortcuts()
        # add listener for a 'place' event
        # respond to the 'place' event by figuring out what it means and relaying info back to the model
        
        # add callback events to the frame's buttons
        self._game_frame.play_game_button.config(command=self.play_callback)
        
        # menus
        self._game_frame.file_menu.entryconfig(self._game_frame.menus["file_new_game"], command=self.new_game_callback)
        self._game_frame.file_menu.entryconfig(self._game_frame.menus["file_exit"], command=self.exit_callback)
        
        if GameController.DEV_FLAG:
            self._game_frame.dev_menu.entryconfig(self._game_frame.menus["dev_auto_place"], command=self.autoplace_ships_callback)
    
    def autoplace_ships_callback(self, event=None):
        '''Respond to the `dev` event of auto-placing all the ships.
        Do nothing if DEV_FLAG is False
        '''
    
        if GameController.DEV_FLAG:
            ships = ShipLoader.read("sample_configurations/sample_ship_config.txt")
            
            for ship in ships:
                self._game_frame._my_grid_frame._ship_panel._ship_buttons[ship._type].invoke()
                self._game_frame._my_grid.add_ship(*ship.coords(), ship=ship._type, vertical=ship._vertical=="v", callback=self._game_frame.get_add_ship_callback())
            self._game_frame.unselect_ship()
        
        # ships = read_ship_configuration(autoplace_config_file)
        # if model.check_ship_config(ships) <-- make sure everything is kosher
        #   model.set_ship_config(ships)
        #   update the view based on the model
        # else
        #   display warning on view
        pass
    
    def play_callback(self, event=None):
        '''Prepare the UI and model to actually shoot at the other player.
        If some error occurs, abort the operation and display warning in the UI.'''
    
        #TODO sanity check before transition
    
        # if ships are all placed
        #   update model
        #   update view
        # else
        #   display warning on view
        self._game_frame._state = self._game_frame.PLAYING
        self._game_frame.process_state()
        
    def place_ship_callback(self, event=None):
        '''Respond to a place event.'''
        
        # pos = get_tile_from_mouse_position
        # if ship can be placed at current pos
        #   update model
        #   update view
        # else
        #   display warning on view
        pass

    def shot_square_callback(self):
        '''Respond to a shooting event.'''

        # pos = get_tile_from_mouse_position
        # if tile is NULL (has never been fired on)
        #   result = model.fire_on_pos(pos)
        #   view.update_with_shot_result(result, pos)
        # else
        #   display warning on view
        pass
        
    def new_game_callback(self, event=None):
        '''Start a new game.
        This method can be called at any time.'''
        
        self._game_frame._winner = None
        self._game_frame._set_ships = {ship : False for ship in Ship.SIZES.keys()}
        
        # reset the model
        self._game_frame._my_grid.reset()
        self._game_frame._their_grid.reset()
        
        # reset AI
        self._game_frame.ai.reset()
        self._game_frame.ai.read_stat_model("ai/stat")
        
        # reset the view
        self._game_frame.reset()
        
if __name__ == "__main__":
    g = GameController()