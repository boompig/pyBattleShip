from Tkinter import *
from ship_model import ShipModel, ShipLoader, Ship
import time

class ShipGrid(Canvas):
	'''Fun little grid for battleship.'''

	RECT_SIZE = 30
	GRID_SIZE = 10
	GRID_X_OFFSET = 25
	GRID_Y_OFFSET = 25
	
	RECT_NULL_FILL = "slate blue"
	RECT_MISS_FILL = "grey"
	RECT_HIT_FILL = "red"
	RECT_SUNK_FILL = "powder blue"

	def __init__(self, master, home=False):
		'''Create a new grid. home determines if this is your grid or the opponent's.'''
	
		Canvas.__init__(self, master)
		
		self.size = self.GRID_SIZE * self.RECT_SIZE + 2 * max(self.GRID_X_OFFSET, self.GRID_Y_OFFSET)
		self.config(height=self.size, width=self.size)
		
		self._home = home
		
		self._model = ShipModel()
		
		self._make_grid()
		self.reset()
	
	
	def get_tile_coords(self, id):
		return self._tiles[id]
			
	def process_shot(self, id, callback=None):
		'''Shoot this tile. Return the result.'''
		
		x, y = self.get_tile_coords(id)
		
		tag_id = self._get_tile_name(x, y)
		result = self._model.shoot(x, y)
		self._set_tile_state(x, y)
		
		#if result and callback is not None:
		#callback(result)
		
		return result
		
	def reset(self):
		'''Reset the grid to starting values.'''
		
		# reset the model
		self._model.reset()
		
		# unbind all previous event
		self.unbind("<Button>")
		
		self._ships = {}
		self._orientations = {}
		
		# reset the squares
		for x, y in self._tiles.itervalues():
			self._set_tile_state(x, y)
			
	def can_add_ship(self, x, y, ship, vertical):
		squares = set(self._model.get_ship_covering_squares(x, y, ship, vertical))
		
		for other, other_sq in self._ships.iteritems():
			if ship == other:
				continue
			
			if len( set(other_sq).intersection(squares) ) > 0:
				print "fails on " + other
				return False
	
		return self._model.is_valid_ship_placement(x, y, ship, vertical)
		
	def add_ship(self, x, y, ship, vertical, callback=None):
		'''Add a ship at (x, y). Vertical is the orientation - True of False.'''
	
		if self.can_add_ship(x, y, ship, vertical):
			print "+ (%d %d) %s %d" % (x, y, ship, vertical)
		
			# erase previous only if this one is valid
			if ship in self._ships:
				for p_x, p_y in self._ships[ship]:
					self._set_tile_state(p_x, p_y, state=self._model.NULL)
		
			points = self._model.get_ship_covering_squares(x, y, ship, vertical)
			self._ships[ship] = points
			self._orientations[ship] = vertical
			for p_x, p_y in points:
				self._set_tile_state(p_x, p_y, state=self._model.SUNK)
				
			# only initiate callback on success
			if callback is not None:
				callback()
			return True
		else:
			return False
				
	def rotate_ship(self, ship):
		if ship in self._ships:
			x, y = self._ships[ship][0]
			return self.add_ship(x, y, ship, not self._orientations[ship])
		else:
			return False
		
	def _set_tile_state(self, x, y, state=None):
		'''Set the tile state at (x, y).'''
	
		#id = self._tiles[(x, y)]
		if state is None:
			state = self._model.get_state(x, y)
			#print self._model.state_to_str(state)
		tag_id = self._get_tile_name(x, y)
		id = self.find_withtag(tag_id)
		
		# set the label state
		#if state == self._model.SUNK:
		#	self.itemconfigure(id, text=self._model.get_ship(x, y))
		#else:
			#self.itemconfigure(id, text="")
			
		# set the color
		fill_colors = {
			self._model.NULL : self.RECT_NULL_FILL,
			self._model.MISS : self.RECT_MISS_FILL,
			self._model.HIT : self.RECT_HIT_FILL,
			self._model.SUNK : self.RECT_SUNK_FILL
		}
		self.itemconfigure(id, fill=fill_colors[state])
			
		# initially delete events associated with tile
		
			
		#if not self._home:
			#self.tag_unbind(tag_id, "<Button>")
		
			# set event
			#if state == self._model.NULL:
			#	f = lambda event: self.process_shot(x, y)
			#	self.tag_bind(tag_id, "<Button-1>", f)

	def _get_tile_name(self, x, y):
		x_id = chr(97 + x) # here we assume GRID_SIZE <= 26
		y_id = str(y + 1)
		return "tile%s%s" % (x_id, y_id)
	
	def _make_grid(self):
		'''Create a grid, complete with labels.'''
	
		self._tiles = {}
	
		for x in range(self.GRID_SIZE):
			x_id = chr(97 + x) # here we assume GRID_SIZE <= 26
		
			self.create_text(
				self.GRID_X_OFFSET + (x + .5) * self.RECT_SIZE, 
				10, 
				text=x_id
			)
		
			for y in range(self.GRID_SIZE):
				y_id = str(y + 1)
			
				if (x == 0):
					self.create_text(
						13, 
						self.GRID_Y_OFFSET + (y + .5) * self.RECT_SIZE, 
						text=y_id
					)
					
				t = self._get_tile_name(x, y)
			
				id = self.create_rectangle(
					self.GRID_X_OFFSET + x * self.RECT_SIZE, 
					self.GRID_Y_OFFSET + y * self.RECT_SIZE, 
					self.GRID_X_OFFSET +  (x + 1) * (self.RECT_SIZE),
					self.GRID_Y_OFFSET + (y + 1) * (self.RECT_SIZE),
					#fill=self.RECT_NULL_FILL,
					outline="black",
					tags=("tile", t) # only works if x_id is valid
				)
				
				self._tiles[id] = (x, y)
				
	def get_tiles(self):
		'''Return all coordinates.'''
	
		return self._tiles.values()
				
class GameModel(object):
	'''Model for the game, to get some kind of logic separation going.'''
	
	PLACE_STATE = 1
	PLAY_STATE = 2
	
	def __init__(self, grid_obj):
		# first, need to keep track of placed ships
		
		self._state = PLACE_STATE
	
		# stop passing objects!!!
		self._obj = grid_obj
		
	
		
	def reset(self):
		self._unplaced_ships = set(self._obj.SIZES.keys())
	
	
		pass
				
class Game(Frame):
	'''Top-level Frame managing top-level events. Interact directly with user.'''

	X_PADDING = 25
	Y_PADDING = 25
	
	SHIP_PANEL_WIDTH = 150
	
	def __init__(self, master):
		Frame.__init__(self, master)
		
		#self.config(background="white")
		
		self._add_grids()
		self._add_ship_panel()
		self._make_buttons()
		self.config(width=self.X_PADDING * 3 + self._my_grid.size * 2 + self.SHIP_PANEL_WIDTH)
		# here 50 is an estimate for the size of the button
		self.config(height=self.Y_PADDING * 3 + self._my_grid.size + 50)
		
		self.reset()
		self.process_state()
		
		self.set_all_bgs(self, "white")
			
	def set_all_bgs(self, parent, color, depth=0):
		parent.config(background=color)
	
		if depth < 10:
			for child in parent.winfo_children():
				#print child
				self.set_all_bgs(child, color, depth + 1)
		
	def _add_ship_panel(self):
		'''Add a list of ships in the same spot as the opponent's grid.'''
		
		self._ship_panel = Frame(self)
		self._ship_panel.place(x=self.X_PADDING, y=self.Y_PADDING * 4)
		
		self._ship_var = IntVar()
		self._ship_buttons = {}
		
		for i, ship in enumerate(ShipModel.SHIPS):
			self._ship_buttons[ship[0]] = Radiobutton(self._ship_panel, text=ship.title(), value=i, variable=self._ship_var)
			self._ship_buttons[ship[0]].pack(anchor=W)
		
	def process_state(self):
		if self._state == 0:
			# hide opponent's grid during setup
			for child in self._their_grid_frame.winfo_children():
				child.pack_forget()
				
			self._play_game_button.config(state=DISABLED)
		else:
			self._their_grid_label.pack()
			self._their_grid.pack(side=LEFT, pady=20)
			
	def _shot(self, event):
		id = self._their_grid.find_withtag(CURRENT)[0]
		# here we can safely process the shot
		result = self._their_grid.process_shot(id)
		if result == ShipModel.HIT or result == ShipModel.SUNK:
			self._their_grid.tag_unbind(CURRENT, "<Button-1>")
			print "Go again"
		else:
			print "not your turn"
			time.sleep(2)
			print "now you can go"
			
	def _add_grid_events(self):
		'''Add events to the grids.'''
		
		pass
		#f = lambda event: self._shot()
		self._their_grid.tag_bind("tile", "<Button-1>", self._shot)
			
	def _add_grids(self):
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
		
		self._my_grid.reset()
		self._their_grid.reset()
		self._state = 0
		self._vertical = { ship : True for ship in ShipModel.SIZES.keys()}
		self._set_ships = {ship : False for ship in ShipModel.SIZES.keys()}
		
		for x, y in self._my_grid.get_tiles():
			self.reset_closure(x, y)
			
	def reset_closure(self, x, y):
		tag_id = self._my_grid._get_tile_name(x, y)
		c = self.get_add_ship_callback()
		f = lambda event: self._my_grid.add_ship(x, y, self.get_current_ship(), self.get_current_vertical(), callback=c)
		self._my_grid.tag_bind(tag_id, "<Button-1>", f)
		
	def get_add_ship_callback(self):
		return lambda: self.ship_set(self.get_current_ship())
		
	def ship_set(self, ship):
		self._set_ships[ship] = True
		self._ship_buttons[ship].config(foreground="forest green")
		
		if all(self._set_ships.values()):
			self._play_game_button.config(state=NORMAL)
		
	def all_ships_set(self):
		return all([self.ship_set(ship) for ship in ShipModel.SIZES.keys()])
		
	def rotate_ship(self):
		'''Rotate current ship.'''
		
		if self._my_grid.rotate_ship(self.get_current_ship()):
			self._vertical[self.get_current_ship()] = not self.get_current_vertical()
		
	def get_current_ship(self):
		'''Return the current ship.'''
	
		return ShipModel.SHIPS[self._ship_var.get()][0].lower()
		
	def get_current_vertical(self):
		'''Return current vertical orientation.'''
	
		return self._vertical[self.get_current_ship()]
		
	def play_game(self):
		self._state = 1
		self.process_state()
		
	def auto_place(self):
		ships = ShipLoader.read("sample_ship_config.txt")
		
		for ship in ships:
			self._ship_buttons[ship._type].invoke()
			self._my_grid.add_ship(*ship.coords(), ship=ship._type, vertical=ship._vertical=="v", callback=self.get_add_ship_callback())
		
	def _make_buttons(self):
		'''Create action buttons at the bottom.'''
	
		button_row = self._my_grid.size + self.Y_PADDING + 40
		button_frame = Frame(self)
		button_frame.place(x=self._my_grid.size - self.X_PADDING, y=button_row)
	
		reset_button = Button(button_frame, text="Reset", command=self.reset)
		reset_button.pack(side=LEFT, padx=5, pady=5)
		
		rotate_button = Button(button_frame, text="Rotate Ship", command=self.rotate_ship)
		rotate_button.pack(side=LEFT, padx=5, pady=5)
		
		self._play_game_button = Button(button_frame, text="Play", command=self.play_game)
		self._play_game_button.pack(side=LEFT, padx=5, pady=5)
		
		autoplace_button = Button(button_frame, text="Auto-place ships", command=self.auto_place)
		autoplace_button.pack(side=LEFT, padx=5, pady=5)
		
		
if __name__ == "__main__":
	app = Tk()
	
	frame = Game(app)
	frame.pack()
	frame.pack(fill=BOTH, expand=1)
	
	app.mainloop()
	pass
	