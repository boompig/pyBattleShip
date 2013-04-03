import tkFileDialog
from Tkinter import *
from collections import OrderedDict
import uuid
import time
import random
import json
import os

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

    ############ JSON/saving ############
    PLAYERS = ["human", "ai"]
    SAVE_DIR = "saves"
    AUTOSAVE_DIR = os.path.join(SAVE_DIR, "autosaves")
    DEFAULT_SAVE_FILE = "battleship.json"
    #####################################
    
    ########## Key Game Files ###########
    CONF_DIR = "config"
    ID_FILE = "game_id.txt"
    #####################################

    def _set_cwd(self):
        '''Set correct working directory. Done for compatibility with gVim on Windows, and running this from outside the base directory.'''

        p = os.path.realpath(__file__)
        head, tail = os.path.split(p)
        if head != os.getcwd():
            os.chdir(head)
            
    def _game_files_setup(self):
        '''Create initial game files, if not already present.
        Keep them up to date.'''
        
        if not os.path.exists(GameController.CONF_DIR):
            os.makedirs(GameController.CONF_DIR)
        fname = os.path.join(GameController.CONF_DIR, GameController.ID_FILE)
        if not os.path.exists(fname):
            fp = open(fname, "w")
            fp.close()
    
    def _create_game_id(self):
        '''Create a unique game ID for this game. Update relevant file.'''
        
        fname = os.path.join(GameController.CONF_DIR, GameController.ID_FILE)
        fp = open(fname, "r")
        self._game_id = int("0" + fp.read().strip()) + 1 # leading 0 makes game_id = 0 when file is empty
        fp.close()
        
        fp = open(fname, "w")
        fp.write(str(self._game_id))
        fp.close()

    def __init__(self): 
        '''Create a main controller for the game.
        Create the GUI. Run the game.'''
        
        self._set_cwd()
        self._game_files_setup()
        self._saved = False

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
        
    def exit_callback(self, event=None):
        '''Quit the game by closing the parent window.'''
        
        self.game_frame.master.destroy()
        
    def _create_keyboard_shortcuts(self):
        '''Create the game's keyboard shortcuts.'''
        
        d = {
            "P" : self.autoplace_ships_callback,
            "<space>" : self.play_callback,
            "<Control-w>" : self.exit_callback, #typical functionality
            "N" : self.new_game_callback,
            "?" : lambda event: self.game_frame.show_keyboard_shortcuts(),
            "F" : self.random_shot_callback,
            "<Control-s>" : self.save_callback,
            "<Control-o>" : self.load_callback
        }

        # enable special controls for dev to fast-navigate the app
        if GameController.DEV_FLAG:
            d["X"] = self.exit_callback
        
        for key_binding, fn in d.iteritems():
            self.game_frame.master.bind(key_binding, fn) # has to be master
            if GameController.DEV_FLAG:
                print "{} <-- {}".format(key_binding, fn.__name__)
        
    def save_callback(self, event=None, fname=None):
        '''Write the game configuration to a JSON file.
        Cannot save the game before both AI and human player have placed ships.
        fname is the file name'''

        grids = [self.game_frame.my_grid._model, self.game_frame.their_grid._model]
        
        if all([g.has_all_ships() for g in grids]):
            while fname is None or isinstance(fname, list): 
                fname = tkFileDialog.asksaveasfilename(defaultextension="json", 
                        initialdir=os.path.join(os.getcwd(), self.SAVE_DIR),
                        filetypes=[("Battleship Games", "*.json")])
                
                if isinstance(fname, list):
                    self.game_frame.show_warning("Select one file only")
                    
            if len(fname) == 0:
                # user pressed cancel. abort
                return
            
            if not self._saved:
                self._create_game_id()
            
            obj = OrderedDict()
            obj["game_id"] = self._game_id
            
            # write ship placement
            for grid, player in zip(grids, GameController.PLAYERS):
                obj[player] = {}
                obj[player]["ships"] = grid.get_ship_placement()
                obj[player]["shots"] = grid.get_shots()
            
            main_obj = {"battleship" : obj} # bind all data to a root element
            fp = open(fname, "w")
            if GameController.DEV_FLAG:
                json.dump(main_obj, fp, indent=4, separators=(',', ': '))
            else:
                json.dump(main_obj, fp, separators=(',', ':'))
            fp.close()
            
            self._saved = True
        else:
            self.game_frame.show_warning("You cannot save the game before you place your ships and start playing.")

    def autosave_callback(self, event=None):
        '''Auto-save the state of the game in some file. Do this occasionally.'''

        self.save_callback(event, os.path.join(GameController.AUTOSAVE_DIR, str(uuid.uuid4()) + ".json"))

    def load_callback(self, event=None, fname=None):
        '''Read the JSON game configuration from file called <code>fname</code>.
        Return a dictionary representing the parsed JSON. All the strings are Unicode.
        
        error_check should be True, turn to False to disable strict error checking for debugging.
        
        May raise KeyError if JSON is not in the expected format (see battleship.json for example).
        May raise ValueError if fails to parse file
        May raise IOError if fails to find file'''

        if fname is None:
            fname = tkFileDialog.askopenfilename(defaultextension="json", 
                    initialdir=os.path.join(os.getcwd(), self.SAVE_DIR),
                    filetypes=[("Battleship Games", "*.json")])
            #error-check user input
            assert not isinstance(fname, list) and len(fname) > 0

        fp = open(os.path.join(GameController.SAVE_DIR, fname), "r")
        obj = json.load(fp)["battleship"] # do this so we don't have to reference ["battleship"] every time
        fp.close()

        #TODO just for now, to see if it works
        print obj
        return
        
        grids = [GridModel(), GridModel()]
        
        # placing ships
        for grid, player in zip(grids, PLAYERS):
            for ship_name, coords in obj[player]["ships"].iteritems():
                s = Ship(type=str(ship_name),  x=coords[0], y=coords[1], vertical=coords[2])
                success = grid.add(s)
                
                if error_check:
                    assert success
            
            grid.finalize(error_check=False)
            
        # firing shots
        for grid, player in zip(grids, PLAYERS):
            for shot in obj[player]["shots"]:
                grid.process_shot(*shot)
                
        return grids

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
        
        # every time something is shot.. 
        self.game_frame.their_grid.tag_bind("tile", "<Button-1>", self.shot_square_callback)
        
        # add callback events to the frame's buttons
        self.game_frame.play_game_button.config(command=self.play_callback)
        
        # menus
        self.game_frame.file_menu.entryconfig(self.game_frame.menus["file_new_game"], command=self.new_game_callback)
        self.game_frame.file_menu.entryconfig(self.game_frame.menus["file_exit"], command=self.exit_callback)
        
        if GameController.DEV_FLAG:
            self.game_frame.dev_menu.entryconfig(self.game_frame.menus["dev_auto_place"], command=self.autoplace_ships_callback)
            self.game_frame.dev_menu.entryconfig(self.game_frame.menus["dev_random_shot"], command=self.random_shot_callback)
    
    def read_game_state(self, fname):
        '''Read game state from the given file. fname is the file name.'''
        
        fp = open(fname, "r")
        fp.close()
        
        pass
    
    def autoplace_ships_callback(self, event=None):
        '''Respond to the `dev` event of auto-placing all the ships.
        Do nothing if DEV_FLAG is False
        '''
    
        if GameController.DEV_FLAG:
            ships = ShipLoader.read("sample_configurations/sample_ship_config.txt")
            
            for ship in ships:
                self.game_frame.my_grid_frame.ship_panel.ship_buttons[ship._type].invoke()
                self.game_frame.my_grid.add_ship(*ship.coords(), ship=ship._type, vertical=ship._vertical=="v", callback=self.game_frame.get_add_ship_callback())
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
        if self.game_frame.my_grid._model.has_all_ships():
            #   update view
            self.game_frame._state = self.game_frame.PLAYING
            self.game_frame.process_state()
            self.autosave_callback()
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
    
    def random_shot_callback(self, event=None):
        '''Shoot at a random unshot square.
        Will only execute in play state.'''
        
        if self.game_frame._state == mock1.Game.PLAYING:
            grid = self.game_frame.their_grid._model
            l2 = grid.get_null_squares()
            shot = random.choice(tuple(l2))
            self.shot_square(shot)
        elif self.game_frame._state == mock1.Game.GAME_OVER:
            self.game_frame.show_warning("Cannot shoot after the game is over")
        elif self.game_frame._state == mock1.Game.PLACING:
            self.game_frame.show_warning("Cannot shoot until after all your ships have been placed")
    
    def shot_square(self, shot):
        '''Call this method when a human has made a shot.
        The shot is the coordinate in the grid system of the shot.'''
        
        result = self.process_human_shot(shot)
        
        if result == Ship.MISS:
            # disable opponent's grid during their turn
            result = Ship.NULL
            self.game_frame.their_grid.disable()
            while result != Ship.MISS and self._winner is None:
                result = self.process_ai_shot()
                
            # re-enable their grid
            self.game_frame.their_grid.enable()
        
        if self._winner is not None:
            self.game_over_callback()

    def shot_square_callback(self, event=None):
        '''Respond to a shooting event.'''

        # pos = get_tile_from_mouse_position
        # if tile is NULL (has never been fired on)
        #   result = model.fire_on_pos(pos)
        #   view.update_with_shot_result(result, pos)
        # else
        #   display warning on view
        id = self.game_frame.their_grid.find_withtag(CURRENT)[0]
        shot = self.game_frame.their_grid.get_tile_coords(id)
        self.shot_square(shot)
            
    def process_human_shot(self, shot):
        '''Given the shot from the human player, react to it.
        Return the result of the shot - HIT, MISS, SUNK.'''
        
        id = self.game_frame.their_grid.get_tile_id(*shot)
        result = self.game_frame.their_grid.process_shot(id)
        # disable square regardless of result
        self.game_frame.their_grid.itemconfig(id, state=DISABLED)
        
        if result == Ship.SUNK:
            ship = self.game_frame.their_grid._model.get_sunk_ship(*shot)
            self.game_frame.their_grid_frame.ship_panel.set_sunk(ship.get_short_name())
        
            if self.game_frame.their_grid._model.all_sunk():
                self._winner = GameController.HUMAN_PLAYER
                
        return result
    
    def process_ai_shot(self):
        '''Get the shot from the AI.
        Process the given shot by the AI.
        Return the result of the shot'''
    
        start = time.time()
        shot = self.game_frame.ai.get_shot()
        tag_id = self.game_frame.my_grid._get_tile_name(*shot)
        id = self.game_frame.my_grid.find_withtag(tag_id)[0]
        result = self.game_frame.my_grid.process_shot(id)
        
        if result == Ship.HIT or result == Ship.SUNK:
            self.game_frame._set_ship_hit(self.game_frame.my_grid._model.get_ship_at(*shot))
            
        if result == Ship.SUNK:
            self.game_frame._set_ship_sunk(self.game_frame.my_grid._model.get_sunk_ship(*shot).get_short_name())
        
            if self.game_frame.my_grid._model.all_sunk():
                self._winner = GameController.AI_PLAYER
                
        # update the AI with the shot's result
        self.game_frame.ai.set_shot_result(result)
        
        end = time.time()
        #TODO need to implement delay here somehow
        #while end-start < mock1.GameController.AI_SHOT_DELAY:
        #    end = time.time()
                
        return result
    
    def game_over_callback(self, event=None):
        '''Call this when the game is over (one of the players has won).
        Initiate appropriate events in model and view.'''
        
        self.autosave_callback()
        self.game_frame._state = mock1.Game.GAME_OVER
        self.game_frame.process_state()
        self.game_frame.show_game_over_popup(self._winner)
        
    def new_game_callback(self, event=None):
        '''Start a new game.
        This method can be called at any time.'''
        
        self.game_frame._winner = None
        self.game_frame._set_ships = {ship : False for ship in Ship.SIZES.keys()}
        
        # reset the model
        self.game_frame.my_grid.reset()
        self.game_frame.their_grid.reset()
        
        # reset AI
        self.game_frame.ai.reset()
        self.game_frame.ai.read_stat_model("ai/stat")
        
        # reset the view
        self.game_frame.reset()
        
        self._winner = None
        
if __name__ == "__main__":
    g = GameController()
