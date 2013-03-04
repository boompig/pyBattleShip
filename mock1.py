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

class Game(Frame):
	'''Top-level Frame managing top-level events. Interact directly with user.'''

	X_PADDING = 25
	Y_PADDING = 25
	
	SHIP_PANEL_WIDTH = 150
	
	def __init__(self, master):
		'''Create the UI for a game of battleship.'''
	
		Frame.__init__(self, master)
		
		self._create_ui()
		
		# these are 'controller' elements that should really be in another class
		self.ai = ShipAI(self._my_grid._model)
		self.reset()
		self.process_state()
		
	def _create_ui(self):
		'''Create all UI elements for the game.'''
		
		self._add_grids()
		self._add_placement_panel()
		self._add_ship_panel()
		self._make_buttons()
		
		self.config(width=self.X_PADDING * 3 + self._my_grid.size * 2 + self.SHIP_PANEL_WIDTH)
		# here 50 is an estimate for the size of the button
		self.config(height=self.Y_PADDING * 3 + self._my_grid.size + 50)
		self.set_all_bgs("white", self)
		
	def _add_placement_panel(self):
		'''Create the placement/ship staging panel.'''
	
		self._placement_panel = ShipPlacementPanel(self)
		self._placement_panel.place(
			x=self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH + self._my_grid.size,
			y=self.Y_PADDING
		)
			
	def set_all_bgs(self, color, parent):
		'''Set all the backgrounds of the child widgets to a certain color.'''
	
		parent.config(background=color)
	
		for child in parent.winfo_children():
			self.set_all_bgs(color, child)
		
	def _add_ship_panel(self):
		'''Add a list of ships in the same spot as the opponent's grid.
		Note that staging area must be added FIRST'''
		
		self._ship_panel = Frame(self)
		self._ship_panel.place(x=self.X_PADDING, y=self.Y_PADDING * 4)
		
		self._ship_var = IntVar()
		self._ship_buttons = {}
		
		for i, ship in enumerate(Ship.SHIPS):
			self._ship_buttons[ship[0]] = Radiobutton(
				self._ship_panel, 
				text=ship.title(), 
				value=i, 
				variable=self._ship_var, 
				indicatoron=False,
				command=self._stage_current_ship
			)
			self._ship_buttons[ship[0]].pack(anchor=W, pady=10)
			self._ship_buttons[ship[0]].grid(sticky=N + S + E + W)
			
		self.unselect_ship()
			
	def unselect_ship(self):
		'''Deselect all ships in the placement and staging GUIs.'''
	
		self._ship_var.set(10)
		self._placement_panel.reset()
		
	def _stage_current_ship(self):
		'''Stage the currently selected ship.'''
		
		if self.get_current_ship() is not None:
			# the x and y coordinates don't matter in this case
			# stage the ship vertically by default
			s = Ship(0, 0, self.get_current_ship(), True)
			self._placement_panel.add_ship(s)
		
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
	
		if self._state == 0:
			# show staging panel
			self._placement_panel.pack_ui()
			self._placement_panel.lift(aboveThis=self._their_grid_frame)
			
			# enable placement
			self._autoplace_button.config(state=NORMAL)
		
			self._play_game_button.config(state=DISABLED)
			self._hide_frame(self._their_grid_frame)
		else:
			self._my_grid._model.finalize()
			self._hide_frame(self._placement_panel)
			
			# disable placement
			self._autoplace_button.config(state=DISABLED)
			
			# disable ship selector radio buttons
			#for button in self._ship_buttons.itervalues():
			#	button.unbind(state=DISABLED)
			self.unselect_ship()
			
			# show opponent's grid
			self._their_grid_frame.lift(aboveThis=self._placement_panel)
			self._their_grid_label.pack()
			self._their_grid.pack(side=LEFT, pady=20)
			
	def _shot(self, event):
		id = self._their_grid.find_withtag(CURRENT)[0]
		# here we can safely process the shot
		result = self._their_grid.process_shot(id)
		
		if result == Ship.HIT or result == Ship.SUNK:
			self._their_grid.tag_unbind(CURRENT, "<Button-1>")
			print "Go again"
		else:
			print "not your turn"
			# disable opponent's grid during their turn
			result = Ship.NULL
			while result != Ship.MISS:
				self._their_grid.config(state=DISABLED)
				shot = self.ai.get_shot()
				tag_id = self._my_grid._get_tile_name(*shot)
				id = self._my_grid.find_withtag(tag_id)[0]
				result = self._my_grid.process_shot(id)
				
				if result == Ship.SUNK:
					self._set_ship_sunk(self._my_grid._model.get_sunk_ship(*shot).get_short_name())
				
				self.ai.set_shot_result(result)
			#time.sleep(10)
			self._their_grid.config(state=NORMAL)
			print "now you can go"
			
	def _add_grid_events(self):
		'''Add events to the grids.'''
		
		pass
		#f = lambda event: self._shot()
		self._their_grid.tag_bind("tile", "<Button-1>", self._shot)
			
	def _add_grids(self):
		'''Create UI containers for the player grids.'''
	
		self._my_grid_frame = Frame(self)
		self._my_grid_frame.place(x=self.X_PADDING + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING)
		l1 = Label(self._my_grid_frame, text="Your Grid")
		l1.pack()
		self._my_grid = ShipGrid(self._my_grid_frame, True)
		self._my_grid.pack(side=LEFT, pady=20)
		
		self._their_grid_frame = Frame(self)
		self._their_grid_frame.place(x=self._my_grid.size + self.X_PADDING * 2 + self.SHIP_PANEL_WIDTH, y=self.Y_PADDING)
		self._their_grid_label = Label(self._their_grid_frame, text="Opponent's Grid")
		self._their_grid_label.pack()
		self._their_grid = ShipGrid(self._their_grid_frame, False)
		self._their_grid.pack(side=LEFT, pady=20)
		
		self._add_grid_events()
		
	def reset(self):
		'''New game!'''
		
		# reset both grids
		self._my_grid.reset()
		self._their_grid.reset()
		
		# reset selected ship
		self.unselect_ship()
		
		# reset staging area
		self._placement_panel.reset()
		
		# reset AI
		self.ai.reset()
		
		self._state = 0
		self.process_state()
		
		self.ai.read_stat_model("stat")
		self._set_ships = {ship : False for ship in Ship.SIZES.keys()}
		
		for x, y in self._my_grid.get_tiles():
			self.reset_closure(x, y)
			
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
	
		s = self._placement_panel.get_staged_ship()
		
		if s is not None:
			self._my_grid.add_ship(x, y, s.get_short_name(), s.is_vertical(), callback)
		
	def get_add_ship_callback(self):
		'''Return the callback function for adding a ship.'''
	
		return lambda: self.ship_set(self.get_current_ship())
		
	def _set_ship_sunk(self, ship):
		'''This is a callback, to be called when a ship has been sunk.
		TODO for now only called when one of MY ships is sunk.
		IU shows that the given ship has been sunk.'''
		
		self._ship_buttons[ship].config(foreground="red")
		
	def ship_set(self, ship):
		'''This is a callback, to be called when a ship has been placed.
		UI shows that the given ship has been placed.'''
	
		self._set_ships[ship] = True
		self._ship_buttons[ship].config(foreground="forest green")
		
		if all(self._set_ships.values()):
			self._play_game_button.config(state=NORMAL)
		
	def get_current_ship(self):
		'''Return the current ship.'''
		
		if self._ship_var.get() >= len(Ship.SHIPS):
			return None
		else:
			return Ship.SHIPS[self._ship_var.get()][0].lower()
		
	def play_game(self):
		'''Process the event to stop placement and start playing the game.
		'''
		
		#TODO sanity check
	
		self._state = 1
		self.process_state()
		
	def auto_place(self):
		'''Automatically place the ships according to a preset configuration.
		This should only be enabled in debugging mode.'''
	
		ships = ShipLoader.read("sample_ship_config.txt")
		
		for ship in ships:
			self._ship_buttons[ship._type].invoke()
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
		
		self._autoplace_button = Button(button_frame, text="Auto-place ships", command=self.auto_place)
		self._autoplace_button.pack(side=LEFT, padx=5, pady=5)
		
		
if __name__ == "__main__":
	app = Tk()
	app.title("Battleship")
	
	game = Game(app)
	#game.lift(aboveThis=root)
	#game.pack()
	game.pack(fill=BOTH, expand=1)
	
	app.mainloop()
	pass
	