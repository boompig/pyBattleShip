'''
Written by Daniel Kats
March 4, 2013
'''

#################
#    IMPORTS    #
#################

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

class GameController(object):
    '''
    This class is only used as a middle-man for communication with the model.
    When the GUI does not need the model, it processes its own events.
    '''

    def __init__(self): 
        '''Create a main controller for the game.'''
        
        # create and run the game
        app = Tk()
    
        self._game_frame = Game(app)
        self._game_frame.pack(fill=BOTH, expand=1)
        self._game_frame.grab_set()
        self._game_frame.focus_set()
        
        self.create_hooks()
        
        app.mainloop()
        
        # create the GUI
        # create the hooks
        pass
        
    def _create_keyboard_shortcuts(self):
        '''Create the game's keyboard shortcuts.'''
        
        d = {
            "P" : self._game_frame.auto_place,
            "<space>" : self._game_frame.play_game
        }
        
        for key_binding, fn in d.iteritems():
            print "{} <-- {}".format(key_binding, fn.__name__)
            self._game_frame.bind(key_binding, fn)
        
    def create_hooks(self):
        '''Create listeners (hooks) to the GUI for relevant items.'''
        
        self._create_keyboard_shortcuts()
        # add listener for a 'place' event
        # respond to the 'place' event by figuring out what it means and relaying info back to the model
        pass
       
    def autoplace_ships_callback(self, event=None):
        '''Respond to the `dev` event of auto-placing all the ships.
        '''
        
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
    
        # if ships are all placed
        #   update model
        #   update view
        # else
        #   display warning on view
        pass
        
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
        
    def new_game_callback(self):
        '''Start a new game.'''
        
        # reset the model
        # reset the view
        pass
        
####################
#    MAIN CLASS    #
####################

class Game(Frame):
    '''Top-level Frame managing top-level events. Interact directly with user.'''
    
    ############ flags ##################
    ''' set this to True if you want to see the dev menu
        The dev menu has these and other features:
            - skip parts of the game so you can "join" at a certain point"
            - simulate events
        '''
    DEV_FLAG = True
    #####################################

    ############ geometry ###############
    X_PADDING = 25
    Y_PADDING = 25
    SHIP_PANEL_WIDTH = 150
    BUTTON_PANEL_HEIGHT = 50
    BUTTON_PADDING = 5
    #####################################

    ########### states ##################
    PLACING = 0
    PLAYING = 1
    GAME_OVER = 2
    #####################################

    ############ players ################
    AI_PLAYER = 0
    HUMAN_PLAYER = 1
    #####################################

    ############ colors #################
    BACKGROUND_COLOR = "white"
    #####################################

    ###### window titles and messages ################
    GAME_OVER_POPUP_TITLE = "Game Over"
    GAME_OVER_WIN_MSG = "You win!"
    GAME_OVER_LOSE_MSG = "Game over. You lose."
    WINDOW_TITLE_GAME_OVER = "Battleship (Game Over)"
    WINDOW_TITLE_NORMAL = "Battleship"
    ##################################################

    def __init__(self, master):
        '''Create the UI for a game of battleship.'''
    
        Frame.__init__(self, master)
        
        self._create_ui()
        
        # these are 'controller' elements that should really be in another class
        self.ai = ShipAI(self._their_grid._model, self._my_grid._model)
        self.reset()
        
    def show_warning(self, msg):
        '''Show a warning msg that a certain action is illegal.
        Allows user to understand what's going on (i.e. why their action failed.
        '''
        
        pass
        
    def _create_ui(self):
        '''Create all UI elements for the game.'''
        
        self._create_menu()
        self._add_grids()
        self._add_staging_panel()
        self._add_ship_panels()
        self._make_buttons()
        
        self.config(height=self.Y_PADDING * 3 + self._my_grid.size + self.BUTTON_PANEL_HEIGHT)
        self.set_all_bgs(self.BACKGROUND_COLOR, self)
        
    def _show_popup(self, title, text):
        '''Show a popup with the given text as the content.'''
        
        self._popup = Toplevel(self)
        self._popup.title(title)
        f = Frame(self._popup, width=500) # a bit arbitrary
        f.pack()
        
        msg = Message(f, text=text)
        msg.pack()
        
        b = Button(f, text="OK", command=self._destroy_popup)
        b.pack()
        
        self._popup.bind("<Return>", self._destroy_popup)
        self._popup.grab_set()
        self._popup.focus_set()
        self.master.wait_window(self._popup)
        
    def _destroy_popup(self, event=None):
        '''Process removal of the popup.'''
    
        self.master.focus_set()
        self._popup.grab_release()
        self._popup.destroy()
        
    def _show_rules(self):
        '''Show the help dialog in a new window.'''
        
        # load the help page
        help_page_location = "help/rules.txt"
        f = open(help_page_location, "r")
        lines = f.read()
        f.close()
        self._show_popup("Rules", lines)
        
    def _create_menu(self):
        '''Create the menu in the GUI.'''
    
        menubar = Menu(self)
        
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Game", command=self.reset)
        menubar.add_cascade(label="File", menu=file_menu)
        
        if self.DEV_FLAG:
            dev_menu = Menu(menubar, tearoff=0)
            dev_menu.add_command(label="Auto-place ships", command=self.auto_place)
            menubar.add_cascade(label="Dev", menu=dev_menu)
        
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Rules", command=self._show_rules)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menubar)
        
    def _add_staging_panel(self):
        '''Create the placement/ship staging panel.'''
    
        self._my_grid_frame._staging_panel = ShipPlacementPanel(self)
        self._my_grid_frame._staging_panel.place(
            x=self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH + self._my_grid.size,
            y=self.Y_PADDING
        )
            
    def set_all_bgs(self, color, parent):
        '''Set all the backgrounds of the child widgets to a certain color.'''
    
        parent.config(background=color)
    
        for child in parent.winfo_children():
            self.set_all_bgs(color, child)
        
    def _add_ship_panels(self):
        '''Add a list of ships to select from, for adding.
        Note that staging area must be added FIRST'''
        
        ############################## ShipPanel ########################
        self._my_grid_frame._ship_panel = ShipPanel(self)
        self._my_grid_frame._ship_panel.place(x=self.X_PADDING, y=self.Y_PADDING * 4)
        
        for ship in Ship.SHORT_NAMES:
            self._my_grid_frame._ship_panel._ship_buttons[ship].config(command=self._stage_current_ship)
            
        self.unselect_ship()
        ##################################################################
        
        ###################### ShipWarPanel ##############################
        self._my_grid_frame._ship_war_panel = ShipWarPanel(self)
        self._my_grid_frame._ship_war_panel.place(x=self.X_PADDING, y=self.Y_PADDING * 2)
        ##################################################################
        
        ###################### ShipWarPanel for Adversary ################
        self._their_grid_frame._ship_panel = ShipPanel(self)
        self._their_grid_frame._ship_panel.place(x=self._my_grid.size * 2 + self.X_PADDING * 3 + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING * 4)
        ##################################################################
            
    def unselect_ship(self):
        '''Deselect all ships in the placement and staging GUIs.'''
    
        self._my_grid_frame._ship_panel._ship_var.set(10)
        self._my_grid_frame._staging_panel.reset()
        
    def _stage_current_ship(self):
        '''Stage the currently selected ship.'''
        
        if self.get_current_ship() is not None:
            # the x and y coordinates don't matter in this case
            # stage the ship vertically by default
            s = Ship(0, 0, self.get_current_ship(), True)
            self._my_grid_frame._staging_panel.add_ship(s)
        
    def _hide_frame(self, frame):
        '''Since you can't hide a frame per se, 'unpack' the frame's child widgets.
        WARNING: this removes all packing directions for children'''

        frame.lower()
        
        for child in frame.winfo_children():
            child.pack_forget()
            
    def show_game_over_popup(self):
        '''Show a popup with a dialog saying the game is over, and showing the winning player.'''
        
        msg = {
            self.HUMAN_PLAYER : self.GAME_OVER_WIN_MSG,
            self.AI_PLAYER : self.GAME_OVER_LOSE_MSG
        } [self._winner]
            
        self._show_popup(self.GAME_OVER_POPUP_TITLE, msg)
        
    def process_state(self):
        '''Simple state controller to enable and disable certain widgets depending on the state.
        For now, there are 2 states:
            - 0: ship placement
            - 1: playing battleship with opponent
        '''
    
        if self._state == self.PLACING:
            self.config(width=self.X_PADDING * 3 + self._my_grid.size + self.SHIP_PANEL_WIDTH + self._my_grid_frame._staging_panel.CANVAS_WIDTH)
            # show staging panel
            self._my_grid_frame._staging_panel.pack_ui()
            self._my_grid_frame._staging_panel.lift(aboveThis=self._their_grid_frame)
            
            # enable placement
            self._my_grid_frame._autoplace_button.config(state=NORMAL)
        
            self._play_game_button.config(state=DISABLED)
            self._hide_frame(self._their_grid_frame)
            
            self._hide_frame(self._my_grid_frame._ship_war_panel)
            self._my_grid_frame._ship_panel.lift(aboveThis=self._my_grid_frame._ship_war_panel)
            
            # allow the AI to place ships
            self.ai.place_ships()
        elif self._state == self.PLAYING:
            self.config(width=self.X_PADDING * 4 + self._my_grid.size * 2 + self.SHIP_PANEL_WIDTH * 3)
            self._my_grid._model.finalize()
            self._their_grid._model.finalize()
            self._hide_frame(self._my_grid_frame._staging_panel)
            
            self._their_grid.config(state=NORMAL)
            self._their_grid.enable()
            
            for ship in Ship.SHORT_NAMES:
                self._their_grid_frame._ship_panel.set_placed(ship)
            
            self._play_game_button.config(state=DISABLED)
            
            # disable placement
            self._my_grid_frame._autoplace_button.config(state=DISABLED)
            
            self.unselect_ship()
            
            self._my_grid_frame._ship_war_panel.pack_ui()
            self._my_grid_frame._ship_war_panel.lift(aboveThis=self._my_grid_frame._ship_panel)
            
            # show opponent's grid
            self._their_grid_frame.lift(aboveThis=self._my_grid_frame._staging_panel)
            self._their_grid_label.pack()
            self._their_grid.pack(side=LEFT, pady=20)
        elif self._state == self.GAME_OVER:
            # disable everything except for the reset button
            self._their_grid.disable()
            self.master.title(self.WINDOW_TITLE_GAME_OVER)
            self.show_game_over_popup()
            
    def get_winning_player(self):
        '''Return textual representation of winning player.'''
        
        return {
            self.HUMAN_PLAYER: "human",
            self.AI_PLAYER : "ai"
        } [self._winner]
        
    def _process_ai_shot(self):
        '''Get the shot from the AI.
        Process the given shot by the AI.
        Return the result of the shot'''
    
        shot = self.ai.get_shot()
        tag_id = self._my_grid._get_tile_name(*shot)
        id = self._my_grid.find_withtag(tag_id)[0]
        result = self._my_grid.process_shot(id)
        
        if result == Ship.HIT or result == Ship.SUNK:
            self._set_ship_hit(self._my_grid._model.get_ship_at(*shot))
            
        if result == Ship.SUNK:
            self._set_ship_sunk(self._my_grid._model.get_sunk_ship(*shot).get_short_name())
        
            if self._my_grid._model.all_sunk():
                self._winner = self.AI_PLAYER
                
        # update the AI with the shot's result
        self.ai.set_shot_result(result)
                
        return result
        
    def _process_human_shot(self, id):
        '''Given the shot from the human player, react to it.
        Return the result.'''
        
        result = self._their_grid.process_shot(id)
        # disable square regardless of result
        self._their_grid.itemconfig(id, state=DISABLED)
        shot = self._their_grid._tiles[id]
        
        if result == Ship.SUNK:
            ship = self._their_grid._model.get_sunk_ship(*shot)
            self._their_grid_frame._ship_panel.set_sunk(ship.get_short_name())
        
            if self._their_grid._model.all_sunk():
                self._winner = self.HUMAN_PLAYER
                
        return result
            
    def _shot(self, event):
        '''Process a shooting event.
        event should be the Tkinter event triggered by tag_bind
        This is a callback function.'''
    
        id = self._their_grid.find_withtag(CURRENT)[0]
        result = self._process_human_shot(id)
        
        if result == Ship.MISS:
            # disable opponent's grid during their turn
            result = Ship.NULL
            self._their_grid.disable()
            while result != Ship.MISS and self._winner is None:
                result = self._process_ai_shot()
                
            # re-enable their grid
            self._their_grid.enable()
        
        if self._winner is not None:
            self._state = self.GAME_OVER
            self.process_state()
            
    def _add_grid_events(self):
        '''Add events to the grids.'''
        
        self._their_grid.tag_bind("tile", "<Button-1>", self._shot)
            
    def _add_grids(self):
        '''Create UI containers for the player grids.'''
    
        self._my_grid_frame = PlayerController(self)
        self._my_grid_frame.place(x=self.X_PADDING + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING)
        l1 = Label(self._my_grid_frame, text="Your Grid")
        l1.pack()
        self._my_grid = ShipGrid(self._my_grid_frame, True)
        self._my_grid.pack(side=LEFT, pady=20)
        
        self._their_grid_frame = PlayerController(self)
        self._their_grid_frame.place(x=self._my_grid.size + self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING)
        self._their_grid_label = Label(self._their_grid_frame, text="Opponent's Grid")
        self._their_grid_label.pack()
        self._their_grid = ShipGrid(self._their_grid_frame, False)
        self._their_grid.pack(side=LEFT, pady=20)
        
        self._add_grid_events()
        
    def reset(self):
        '''New game!'''
        
        self.master.title(self.WINDOW_TITLE_NORMAL)
        self._winner = None
        
        # reset both grids
        self._my_grid.reset()
        self._their_grid.reset()
        
        # reset selected ship
        self.unselect_ship()
        
        # reset staging area
        self._my_grid_frame._staging_panel.reset()
        
        # reset AI
        self.ai.reset()
        
        # reset indicators on ships in panels
        self._my_grid_frame._ship_war_panel.reset()
        for ship, button in self._my_grid_frame._ship_panel._ship_buttons.iteritems():
            button.config(foreground="black")
        
        self.ai.read_stat_model("ai/stat")
        self._set_ships = {ship : False for ship in Ship.SIZES.keys()}
        
        for x, y in self._my_grid.get_tiles():
            self.reset_closure(x, y)
            
        self._state = self.PLACING
        self.process_state()
            
    def reset_closure(self, x, y):
        '''Add a placement event to the given tile.
        TODO this is badly named'''
    
        tag_id = self._my_grid._get_tile_name(x, y)
        c = self.get_add_ship_callback()
        f = lambda event: self.add_staged_ship(x, y, c)
        self._my_grid.tag_bind(tag_id, "<Button-1>", f)
        
    def add_staged_ship(self, x, y, callback):
        '''Take the stage from the staging area, and place it on the board at position (x, y).
        After ship has been placed, execute the function <callback>.'''
    
        s = self._my_grid_frame._staging_panel.get_staged_ship()
        
        if s is not None:
            self._my_grid.add_ship(x, y, s.get_short_name(), s.is_vertical(), callback)
        
    def get_add_ship_callback(self):
        '''Return the callback function for adding a ship.'''
    
        return lambda: self.ship_set(self.get_current_ship())
        
    def _set_ship_sunk(self, ship):
        '''This is a callback, to be called when a ship has been sunk.
        TODO for now only called when one of MY ships is sunk.
        UI shows that the given ship has been sunk.'''
        
        self._my_grid_frame._ship_panel.set_sunk(ship)
        
    def _set_ship_hit(self, ship):
        '''This is a callback, to be called when a ship has been hit.
        TODO for now only called when one of MY ships is hit.
        UI shows that the given ship has been hit.'''
        
        self._my_grid_frame._ship_war_panel.update(ship)
        
    def ship_set(self, ship):
        '''This is a callback, to be called when a ship has been placed.
        UI shows that the given ship has been placed.'''
    
        self._set_ships[ship] = True
        self._my_grid_frame._ship_panel.set_placed(ship)
        
        if all(self._set_ships.values()):
            self._play_game_button.config(state=NORMAL)
        
    def get_current_ship(self):
        '''Return the current ship.'''
        
        return self._my_grid_frame._ship_panel.get_current_ship()
        
    def play_game(self, event=None):
        '''Process the event to stop placement and start playing the game.
        '''
        
        #TODO sanity check
    
        self._state = self.PLAYING
        self.process_state()
        
    def auto_place(self, event=None):
        '''Automatically place the ships according to a preset configuration.
        This should only be enabled in debugging mode.'''
    
        ships = ShipLoader.read("sample_configurations/sample_ship_config.txt")
        
        for ship in ships:
            self._my_grid_frame._ship_panel._ship_buttons[ship._type].invoke()
            self._my_grid.add_ship(*ship.coords(), ship=ship._type, vertical=ship._vertical=="v", callback=self.get_add_ship_callback())
        self.unselect_ship()
        
    def _make_buttons(self):
        '''Create action buttons at the bottom.'''
    
        button_row = self._my_grid.size + self.Y_PADDING + (self.BUTTON_PANEL_HEIGHT - 2 * self.BUTTON_PADDING)
        button_frame = Frame(self)
        button_frame.place(x=self._my_grid.size - self.X_PADDING, y=button_row)
    
        reset_button = Button(button_frame, text="Reset", command=self.reset)
        reset_button.pack(side=LEFT, padx=self.BUTTON_PADDING, pady=self.BUTTON_PADDING)
        
        self._play_game_button = Button(button_frame, text="Play", command=self.play_game)
        self._play_game_button.pack(side=LEFT, padx=self.BUTTON_PADDING, pady=self.BUTTON_PADDING)
        
        self._my_grid_frame._autoplace_button = Button(button_frame, text="Auto-place ships", command=self.auto_place)
        self._my_grid_frame._autoplace_button.pack(side=LEFT, padx=self.BUTTON_PADDING, pady=self.BUTTON_PADDING)
        
        
if __name__ == "__main__":
    g = GameController()