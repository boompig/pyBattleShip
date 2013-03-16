'''
Written by Daniel Kats
March 4, 2013
'''

from Tkinter import *
from ship_model import Ship, ShipLoader
import time
from grid_model import GridModel
from ship_ai import ShipAI
from ship_placement_panel import ShipPlacementPanel
from ship_grid import ShipGrid
from ship_war_panel import ShipWarPanel
from ship_panel import ShipPanel
from player_controller import PlayerController, PlayerGridFrame
import battleship

class Game(Frame):
    '''Top-level Frame managing top-level events. Interact directly with user.'''

    ############ geometry ###############
    X_PADDING = 25
    Y_PADDING = 25
    SHIP_PANEL_WIDTH = 150
    BUTTON_PANEL_HEIGHT = 50
    BUTTON_PADDING = 5
    WARNING_BAR_HEIGHT = 40
    #####################################

    ########### states ##################
    PLACING = 0
    PLAYING = 1
    GAME_OVER = 2
    #####################################    

    ############ colors #################
    BACKGROUND_COLOR = "white"
    WARNING_BACKGROUND = "khaki1"
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
        
    def show_warning(self, msg, title=None):
        '''Show a warning msg that a certain action is illegal.
        Allows user to understand what's going on (i.e. why their action failed.
        '''
        
        if title is None:
            title = "Warning"
        
        self._show_popup(title, msg)
        
    def _create_ui(self):
        '''Create all UI elements for the game.'''
        
        self._create_menu()
        self._add_grids()
        self._addstaging_panel()
        self._addship_panels()
        self._make_buttons()
        
        self.config(height=self.Y_PADDING * 3 + self._my_grid.size + self.BUTTON_PANEL_HEIGHT + self.WARNING_BAR_HEIGHT)
        self.set_all_bgs(self.BACKGROUND_COLOR, self)
        
    def _show_popup(self, title, text):
        '''Show a popup with the given text as the content.'''
        
        self._popup = Toplevel(self)
        self._popup.title(title)
        
        f = Frame(self._popup, width=300) # a bit arbitrary
        f.pack(expand=True, fill=BOTH)
        
        msg = Message(f, text=text, width=f.winfo_reqwidth() - 10)
        msg.pack(expand=True, fill=BOTH)
        f.bind("<Configure>", lambda e: msg.config(width=e.width-10))
        
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
        
    def show_keyboard_shortcuts(self):
        '''Show a dialog box with the keyboard shortcuts.'''
        
        # load the keyboard shortcuts page
        ks_page_location = "help/keyboard_shortcuts.txt"
        f = open(ks_page_location, "r")
        lines = f.read()
        f.close()
        self._show_popup("Keyboard Shortcuts", lines)
        
    def _create_menu(self):
        '''Create the menu in the GUI.'''
    
        menubar = Menu(self)
        self.menus = {}
        
        count = 0
        self.file_menu = Menu(menubar, tearoff=0)
        self.file_menu.add_command(label="New Game")#, command=self.reset)
        self.menus["file_new_game"] = count
        count += 1
        self.file_menu.add_command(label="Exit")#, command=self.master.destroy)
        self.menus["file_exit"] = count
        count += 1
        menubar.add_cascade(label="File", menu=self.file_menu)
        
        if battleship.GameController.DEV_FLAG:
            count = 0
            self.dev_menu = Menu(menubar, tearoff=0)
            self.dev_menu.add_command(label="Auto Place")
            self.menus["dev_auto_place"] = count
            count += 1
            menubar.add_cascade(label="Dev", menu=self.dev_menu)
        
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="Rules", command=self._show_rules)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_keyboard_shortcuts)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menubar)

    def _addstaging_panel(self):
        '''Create the placement/ship staging panel.'''
    
        self.my_grid_frame.staging_panel = ShipPlacementPanel(self)
        self.my_grid_frame.staging_panel.place(
            x=self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH + self._my_grid.size,
            y=self.Y_PADDING
        )
            
    def set_all_bgs(self, color, parent):
        '''Set all the backgrounds of the child widgets to a certain color.'''
    
        parent.config(background=color)
    
        for child in parent.winfo_children():
            self.set_all_bgs(color, child)
        
    def _addship_panels(self):
        '''Add a list of ships to select from, for adding.
        Note that staging area must be added FIRST'''
        
        ############################## ShipPanel ########################
        self.my_grid_frame.ship_panel = ShipPanel(self)
        self.my_grid_frame.ship_panel.place(x=self.X_PADDING, y=self.Y_PADDING * 4)
        
        self.unselect_ship()
        ##################################################################
        
        ###################### ShipWarPanel ##############################
        self.my_grid_frame._ship_war_panel = ShipWarPanel(self)
        self.my_grid_frame._ship_war_panel.place(x=self.X_PADDING, y=self.Y_PADDING * 2)
        ##################################################################
        
        ###################### ShipWarPanel for Adversary ################
        self.their_grid_frame.ship_panel = ShipPanel(self)
        self.their_grid_frame.ship_panel.place(x=self._my_grid.size * 2 + self.X_PADDING * 3 + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING * 4)
        ##################################################################
            
    def unselect_ship(self):
        '''Deselect all ships in the placement and staging GUIs.'''
    
        self.my_grid_frame.ship_panel._ship_var.set(10)
        self.my_grid_frame.staging_panel.reset()
        
    def _hide_frame(self, frame):
        '''Since you can't hide a frame per se, 'unpack' the frame's child widgets.
        WARNING: this removes all packing directions for children'''

        frame.lower()
        
        for child in frame.winfo_children():
            child.pack_forget()
            
    def show_game_over_popup(self):
        '''Show a popup with a dialog saying the game is over, and showing the winning player.'''
        
        msg = {
            battleship.GameController. HUMAN_PLAYER : self.GAME_OVER_WIN_MSG,
            battleship.GameController.AI_PLAYER : self.GAME_OVER_LOSE_MSG
        } [self._winner]
            
        self._show_popup(self.GAME_OVER_POPUP_TITLE, msg)
        
    def process_placing_state(self):
        '''Basic stuff to do during placing state.'''
        
        self.config(width=self.X_PADDING * 3 + self._my_grid.size + self.SHIP_PANEL_WIDTH + self.my_grid_frame.staging_panel.CANVAS_WIDTH)
        
        # show staging panel
        self.my_grid_frame.staging_panel.pack_ui()
        self.my_grid_frame.staging_panel.lift(aboveThis=self.their_grid_frame)
    
        self.play_game_button.config(state=DISABLED)
        self._hide_frame(self.their_grid_frame)
        
        self._hide_frame(self.my_grid_frame._ship_war_panel)
        self.my_grid_frame.ship_panel.lift(aboveThis=self.my_grid_frame._ship_war_panel)
        
        # allow the AI to place ships
        self.ai.place_ships()
        
    def process_playing_state(self):
        '''Basic stuff to do during playing state.'''
        
        self.config(width=self.X_PADDING * 4 + self._my_grid.size * 2 + self.SHIP_PANEL_WIDTH * 3)
        self._my_grid._model.finalize()
        self._their_grid._model.finalize()
        self._hide_frame(self.my_grid_frame.staging_panel)
        
        self._their_grid.config(state=NORMAL)
        self._their_grid.enable()
        
        for ship in Ship.SHORT_NAMES:
            self.their_grid_frame.ship_panel.set_placed(ship)
        
        self.play_game_button.config(state=DISABLED)
        
        self.unselect_ship()
        
        self.my_grid_frame._ship_war_panel.pack_ui()
        self.my_grid_frame._ship_war_panel.lift(aboveThis=self.my_grid_frame.ship_panel)
        
        # show opponent's grid
        self.their_grid_frame.lift(aboveThis=self.my_grid_frame.staging_panel)
        self._their_grid_label.pack()
        self._their_grid.pack(side=LEFT, pady=20)
        
    def process_game_over_state(self):
        # disable everything except for the reset button
        self._their_grid.disable()
        self.master.title(self.WINDOW_TITLE_GAME_OVER)
        self.show_game_over_popup()
        
    def process_state(self):
        '''Simple state controller to enable and disable certain widgets depending on the state.'''
    
        if self._state == self.PLACING:
            self.process_placing_state()
        elif self._state == self.PLAYING:
            self.process_playing_state()
        elif self._state == self.GAME_OVER:
            self.process_game_over_state()
            
    def get_winning_player(self):
        '''Return textual representation of winning player.'''
        
        return {
            battleship.GameController. HUMAN_PLAYER: "human",
            battleship.GameController.AI_PLAYER : "ai"
        } [self._winner]
        
    def _process_ai_shot(self):
        '''Get the shot from the AI.
        Process the given shot by the AI.
        Return the result of the shot'''
    
        start = time.time()
        shot = self.ai.get_shot()
        tag_id = self._my_grid._get_tile_name(*shot)
        id = self._my_grid.find_withtag(tag_id)[0]
        result = self._my_grid.process_shot(id)
        
        if result == Ship.HIT or result == Ship.SUNK:
            self._set_ship_hit(self._my_grid._model.get_ship_at(*shot))
            
        if result == Ship.SUNK:
            self._set_ship_sunk(self._my_grid._model.get_sunk_ship(*shot).get_short_name())
        
            if self._my_grid._model.all_sunk():
                self._winner = battleship.GameController.AI_PLAYER
                
        # update the AI with the shot's result
        self.ai.set_shot_result(result)
        
        end = time.time()
        #TODO need to implement delay here somehow
        #while end-start < battleship.GameController.AI_SHOT_DELAY:
        #    end = time.time()
                
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
            self.their_grid_frame.ship_panel.set_sunk(ship.get_short_name())
        
            if self._their_grid._model.all_sunk():
                self._winner = battleship.GameController.HUMAN_PLAYER
                
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
    
        self.my_grid_frame = PlayerGridFrame(self)
        self.my_grid_frame.place(x=self.X_PADDING + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING)
        l1 = Label(self.my_grid_frame, text="Your Grid")
        l1.pack()
        self._my_grid = ShipGrid(self.my_grid_frame, True)
        self._my_grid.pack(side=LEFT, pady=20)
        
        self.their_grid_frame = PlayerGridFrame(self)
        self.their_grid_frame.place(x=self._my_grid.size + self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING)
        self._their_grid_label = Label(self.their_grid_frame, text="Opponent's Grid")
        self._their_grid_label.pack()
        self._their_grid = ShipGrid(self.their_grid_frame, False)
        self._their_grid.pack(side=LEFT, pady=20)
        
        self._add_grid_events()
        
    def reset(self):
        '''New game!'''
        
        self.master.title(self.WINDOW_TITLE_NORMAL)
        
        # reset selected ship
        self.unselect_ship()
        
        # reset staging area
        self.my_grid_frame.staging_panel.reset()
        
        # reset indicators on ships in panels
        self.my_grid_frame._ship_war_panel.reset()
        for ship, button in self.my_grid_frame.ship_panel.ship_buttons.iteritems():
            button.config(foreground="black")
        
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
    
        s = self.my_grid_frame.staging_panel.get_staged_ship()
        
        if s is not None:
            self._my_grid.add_ship(x, y, s.get_short_name(), s.is_vertical(), callback)
        
    def get_add_ship_callback(self):
        '''Return the callback function for adding a ship.'''
    
        return lambda: self.ship_set(self.my_grid_frame.ship_panel.get_current_ship())
        
    def _set_ship_sunk(self, ship):
        '''This is a callback, to be called when a ship has been sunk.
        TODO for now only called when one of MY ships is sunk.
        UI shows that the given ship has been sunk.'''
        
        self.my_grid_frame.ship_panel.set_sunk(ship)
        
    def _set_ship_hit(self, ship):
        '''This is a callback, to be called when a ship has been hit.
        TODO for now only called when one of MY ships is hit.
        UI shows that the given ship has been hit.'''
        
        self.my_grid_frame._ship_war_panel.update(ship)
        
    def ship_set(self, ship):
        '''This is a callback, to be called when a ship has been placed.
        UI shows that the given ship has been placed.'''
    
        self._set_ships[ship] = True
        self.my_grid_frame.ship_panel.set_placed(ship)
        
        if all(self._set_ships.values()):
            self.play_game_button.config(state=NORMAL)
        
    def _make_buttons(self):
        '''Create action buttons at the bottom.'''
    
        button_row = self._my_grid.size + self.Y_PADDING + (self.BUTTON_PANEL_HEIGHT - 2 * self.BUTTON_PADDING)
        button_frame = Frame(self)
        button_frame.place(x=self._my_grid.size - self.X_PADDING, y=button_row)
        
        self.play_game_button = Button(button_frame, text="Play")
        self.play_game_button.pack(side=LEFT, padx=self.BUTTON_PADDING, pady=self.BUTTON_PADDING)
        
def hide(w):
    w.config(state=HIDDEN)
        
if __name__ == "__main__":
    app = Tk()
    
    game_frame = Game(app)
    game_frame.pack(fill=BOTH, expand=1)
    game_frame.grab_set()
    game_frame.focus_set()
    
    game_frame.show_warning("cannot place ship there")
    
    app.mainloop()
    