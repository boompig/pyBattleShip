from Tkinter import *
from ship_model import Ship, ShipLoader
from grid_model import GridModel
from ship_ai import ShipAI
import mock1
from player_controller import PlayerController

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
    
    ############ delays #################
    AI_SHOT_DELAY = 1.0
    #####################################
    
    ############ players ################
    AI_PLAYER = 0
    HUMAN_PLAYER = 1
    #####################################

    def __init__(self): 
        '''Create a main controller for the game.
        Create the GUI. Run the game.'''
        
        # create the UI
        app = Tk()
    
        self.game_frame = mock1.Game(app)
        self.game_frame.pack(fill=BOTH, expand=1)
        self.game_frame.grab_set()
        self.game_frame.focus_set()
        
        # and the individual controllers
        self.my_controller = PlayerController(self.game_frame.my_grid_frame)
        self.their_controller = PlayerController(self.game_frame.their_grid_frame)
        
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
        
        self.game_frame.master.destroy()
        
    def _create_keyboard_shortcuts(self):
        '''Create the game's keyboard shortcuts.'''
        
        d = {
            "P" : self.autoplace_ships_callback,
            "<space>" : self.play_callback,
            "X" : self.exit_callback,
            "N" : self.new_game_callback,
            "?" : lambda event: self.game_frame.show_keyboard_shortcuts()
        }
        
        for key_binding, fn in d.iteritems():
            print "{} <-- {}".format(key_binding, fn.__name__)
            self.game_frame.master.bind(key_binding, fn) # has to be master
        
    def warn_hi(self):
        self.game_frame.show_warning("hi")
        
    def create_hooks(self):
        '''Create listeners (hooks) to the GUI for relevant items.'''
        
        self._create_keyboard_shortcuts()
        # add listener for a 'place' event
        # respond to the 'place' event by figuring out what it means and relaying info back to the model
        self.game_frame.my_grid_frame.ship_panel.bind("<Button-1>", self.place_ship_callback)
        for ship in Ship.SHORT_NAMES:
            self.game_frame.my_grid_frame.ship_panel.ship_buttons[ship].config(command=self.stage_ship_callback)
        
        
        # add callback events to the frame's buttons
        self.game_frame.play_game_button.config(command=self.play_callback)
        
        # menus
        self.game_frame.file_menu.entryconfig(self.game_frame.menus["file_new_game"], command=self.new_game_callback)
        self.game_frame.file_menu.entryconfig(self.game_frame.menus["file_exit"], command=self.exit_callback)
        
        if GameController.DEV_FLAG:
            self.game_frame.dev_menu.entryconfig(self.game_frame.menus["dev_auto_place"], command=self.autoplace_ships_callback)
    
    def autoplace_ships_callback(self, event=None):
        '''Respond to the `dev` event of auto-placing all the ships.
        Do nothing if DEV_FLAG is False
        '''
    
        if GameController.DEV_FLAG:
            ships = ShipLoader.read("sample_configurations/sample_ship_config.txt")
            
            for ship in ships:
                self.game_frame.my_grid_frame.ship_panel.ship_buttons[ship._type].invoke()
                self.game_frame._my_grid.add_ship(*ship.coords(), ship=ship._type, vertical=ship._vertical=="v", callback=self.game_frame.get_add_ship_callback())
            self.game_frame.unselect_ship()
        
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
        if self.game_frame._my_grid._model.has_all_ships():
            #   update view
            self.game_frame._state = self.game_frame.PLAYING
            self.game_frame.process_state()
            # TODO update model <<< FINALIZE should probably be here
        else:
            self.game_frame.show_warning("Cannot start the game: you have not placed all your ships.")
       
    def stage_ship_callback(self, event=None):
        '''Move a ship to the staging area.'''
        
        #ship = get_selected_ship()
        #move ship to staging area
        #that's about it
        
        if self.game_frame.my_grid_frame.ship_panel.get_current_ship() is not None:
            s = Ship(0, 0, self.game_frame.my_grid_frame.ship_panel.get_current_ship(), True)
            self.game_frame.my_grid_frame.staging_panel.add_ship(s)
        
        pass
        
    def place_ship_callback(self, event=None):
        '''Respond to a place event.'''
        
        print "Placed"
        
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
        
        self.game_frame._winner = None
        self.game_frame._set_ships = {ship : False for ship in Ship.SIZES.keys()}
        
        # reset the model
        self.game_frame._my_grid.reset()
        self.game_frame._their_grid.reset()
        
        # reset AI
        self.game_frame.ai.reset()
        self.game_frame.ai.read_stat_model("ai/stat")
        
        # reset the view
        self.game_frame.reset()
        
if __name__ == "__main__":
    g = GameController()