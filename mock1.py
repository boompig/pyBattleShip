'''
Written by Daniel Kats
March 4, 2013
'''

#################
#	IMPORTS		#
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

#################
#	MAIN CLASS	#
#################

class Game(Frame):
	'''Top-level Frame managing top-level events. Interact directly with user.'''

	############ geometry ###############
	X_PADDING = 25
	Y_PADDING = 25
	SHIP_PANEL_WIDTH = 150
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
	
	def __init__(self, master):
		'''Create the UI for a game of battleship.'''
	
		Frame.__init__(self, master)
		
		self._create_ui()
		
		# these are 'controller' elements that should really be in another class
		self.ai = ShipAI(self._their_grid._model, self._my_grid._model)
		self.reset()
		
	def _create_ui(self):
		'''Create all UI elements for the game.'''
		
		self._add_grids()
		self._add_staging_panel()
		self._add_ship_panels()
		self._make_buttons()
		
		# here 50 is an estimate for the size of the button
		self.config(height=self.Y_PADDING * 3 + self._my_grid.size + 50)
		self.set_all_bgs("white", self)
		
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
			self.master.title("Battleship (Game Over)")
			self.show_game_over_popup()
			print "GAME OVER"
			print "The %s player won" % self.get_winning_player()
			
	def show_game_over_popup(self):
		'''Show a popup with a dialog saying the game is over, and showing the winning player.'''
	
		popup = Toplevel(self)
		popup.title("Game Over")
		f = Frame(popup, width=500)
		#f.pack_propagate(0)
		f.pack()
		
		if self._winner == self.HUMAN_PLAYER:
			msg = Message(f, text="You win!")
		else:
			msg = Message(f, text="Game over. You lose.")
		msg.pack()
		b = Button(f, text="OK", command=popup.destroy)
		b.pack()
		
			
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
			
	def _shot(self, event):
		'''Process a shooting event.
		event should be the Tkinter event triggered by tag_bind
		This is a callback function.'''
	
		id = self._their_grid.find_withtag(CURRENT)[0]
		# here we can safely process the shot
		result = self._their_grid.process_shot(id)
		# disable square regardless of result=
		self._their_grid.itemconfig(id, state=DISABLED)
		shot = self._their_grid._tiles[id]
		
		if result == Ship.SUNK:
			ship = self._their_grid._model.get_sunk_ship(*shot)
			self._their_grid_frame._ship_panel.set_sunk(ship.get_short_name())
		
			if self._their_grid._model.all_sunk():
				self._winner = self.HUMAN_PLAYER
		
		if result != Ship.HIT and result != Ship.SUNK:
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
		
		self.master.title("Battleship")
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
		
		self.ai.read_stat_model("stat")
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
		
	def play_game(self):
		'''Process the event to stop placement and start playing the game.
		'''
		
		#TODO sanity check
	
		self._state = self.PLAYING
		self.process_state()
		
	def auto_place(self):
		'''Automatically place the ships according to a preset configuration.
		This should only be enabled in debugging mode.'''
	
		ships = ShipLoader.read("sample_ship_config.txt")
		
		for ship in ships:
			self._my_grid_frame._ship_panel._ship_buttons[ship._type].invoke()
			self._my_grid.add_ship(*ship.coords(), ship=ship._type, vertical=ship._vertical=="v", callback=self.get_add_ship_callback())
		self.unselect_ship()
		
	def _make_buttons(self):
		'''Create action buttons at the bottom.'''
	
		button_row = self._my_grid.size + self.Y_PADDING + 40
		button_frame = Frame(self)
		button_frame.place(x=self._my_grid.size - self.X_PADDING, y=button_row)
	
		reset_button = Button(button_frame, text="Reset", command=self.reset)
		reset_button.pack(side=LEFT, padx=5, pady=5)
		
		self._play_game_button = Button(button_frame, text="Play", command=self.play_game)
		self._play_game_button.pack(side=LEFT, padx=5, pady=5)
		
		self._my_grid_frame._autoplace_button = Button(button_frame, text="Auto-place ships", command=self.auto_place)
		self._my_grid_frame._autoplace_button.pack(side=LEFT, padx=5, pady=5)
		
		
if __name__ == "__main__":
	app = Tk()
	app.title("Battleship")
	
	game = Game(app)
	#game.lift(aboveThis=root)
	#game.pack()
	game.pack(fill=BOTH, expand=1)
	
	app.mainloop()
	pass
	