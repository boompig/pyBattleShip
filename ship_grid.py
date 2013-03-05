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
from ship_panel import ShipPanel

#################
#	MAIN CLASS	#
#################

class ShipGrid(Canvas):
	'''The UI manager for a player's grid in a game of battleship.
	Takes on the role of view, but also Controller.'''

	############## geometry ############
	RECT_SIZE = 30
	GRID_SIZE = 10
	GRID_X_OFFSET = 25
	GRID_Y_OFFSET = 25
	####################################
	
	############## colors ##############
	RECT_NULL_FILL = "slate blue"
	RECT_MISS_FILL = "grey"
	RECT_HIT_FILL = "red"
	RECT_SUNK_FILL = "powder blue"
	RECT_PLACED_FILL = "forest green"
	####################################

	def __init__(self, master, home=False):
		'''Create a new grid. home determines if this is your grid or the opponent's.'''
	
		Canvas.__init__(self, master)
		
		self.size = self.GRID_SIZE * self.RECT_SIZE + 2 * max(self.GRID_X_OFFSET, self.GRID_Y_OFFSET)
		self.config(height=self.size, width=self.size)
		
		self._home = home
		self._model = GridModel()
		
		self._make_grid()
		self.reset()
		
	def all_placed(self):
		'''Return True iff all the ships have been placed.'''
	
		return self._model.has_all_ships()
	
	def get_tile_coords(self, id):
		'''Return the coordinates of the tile with the given Tkinter ID.'''
	
		return self._tiles[id]
			
	def process_shot(self, id, callback=None):
		'''Shoot this tile. Return the result.'''
		
		x, y = self.get_tile_coords(id)
		
		tag_id = self._get_tile_name(x, y)
		result = self._model.process_shot(x, y)
		
		if result == Ship.SUNK:
			s = self._model.get_sunk_ship(x, y)
			for sq in s.get_covering_squares():
				self._set_tile_state(*sq)
		else:
			self._set_tile_state(x, y)
		
		#if result and callback is not None:
		#callback(result)
		
		return result
		
	def disable(self):
		'''Disable all events on this grid.'''
		
		for id in self._tiles.iterkeys():
			self._prev_state[id] = (self.itemcget(id, 'state') == NORMAL)
			#if not self._prev_state[id]:
				#print self._tiles[id]
			self.itemconfig(id, state=DISABLED)
			
	def enable(self):
		'''Re-enable the events on the grid.'''
		
		for id in self._tiles.iterkeys():
			if self._prev_state[id]:
				self.itemconfig(id, state=NORMAL)
		
	def reset(self):
		'''Reset the grid to starting values.'''
		
		# reset the model
		self._model.reset()
		#if not self._home:
		#	self._model.read("enemy_ships")
		#	self._model.finalize()
			#self._model.show()
		
		# unbind all previous event
		self.unbind("<Button>")
		
		self._ships = {}
		self._prev_state = {} # this is only True for tiles disabled/enabled using disable and enable methods
		
		# reset the squares
		for id, (x, y) in self._tiles.iteritems():
			self._prev_state[id] = False 
			self.itemconfig(id, state=NORMAL)
			self._set_tile_state(x, y)
		
	def add_ship(self, x, y, ship, vertical, callback=None):
		'''Add a ship at (x, y). Vertical is the orientation - True of False.'''
		
		# sometimes nothing is selected, but grid is pressed.
		# ignore these events
		if ship is None:
			return False
		
		result = self._model.can_add_ship(x, y, ship, vertical)
		if result:
			if ship in self._model._ships:
				prev_ship = self._model._ships[ship]
				for sq in prev_ship.get_covering_squares():
					self._set_tile_state(*sq) # reset state
			self._model.add_ship(x, y, ship, vertical)
			for sq in Ship(x, y, ship, vertical).get_covering_squares():
				self._set_tile_state(*sq, state=Ship.OTHER)
			
			if callback is not None:
				callback()
		
		return result
		
	def _set_tile_state(self, x, y, state=None):
		'''Set the tile state at (x, y).'''
	
		if state is None:
			state = self._model.get_state(x, y)
		tag_id = self._get_tile_name(x, y)
		id = self.find_withtag(tag_id)
		
		# set the label state
		#if state == Ship.SUNK:
		#	self.itemconfigure(id, text=self._model.get_ship(x, y))
		#else:
			#self.itemconfigure(id, text="")
			
		# set the color
		fill_colors = {
			Ship.NULL : self.RECT_NULL_FILL,
			Ship.MISS : self.RECT_MISS_FILL,
			Ship.HIT : self.RECT_HIT_FILL,
			Ship.SUNK : self.RECT_SUNK_FILL,
			Ship.OTHER : self.RECT_PLACED_FILL
		}
		self.itemconfigure(id, fill=fill_colors[state])

	def _get_tile_name(self, x, y):
		'''Return the tile's tag name, given its coordinates.'''
	
		x_id = chr(97 + x) # here we assume GRID_SIZE <= 26
		y_id = str(y + 1)
		return "tile%s%s" % (x_id, y_id)
		
	def bind_tile(self, x, y, function):
		'''Bind the given event to the mouse-click of a tile.'''
		
		tag = self._get_tile_name(x, y)
		g = lambda event: function()
		self.tag_bind(tag, "<Button-1>", g)
	
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
		
#################
#	TESTER		#
#################

class Master(Frame):
	def __init__(self, m):
		Frame.__init__(self, m)
		
		p = PlayerController(root)
		p.pack()
		
		b = Button(self,text="play", command=p.play)
		b.pack()

if __name__ == "__main__":
	root = Tk()
	m = Master(root)
	m.pack()
	#sp = ShipPlacementPanel()
	
	
	root.mainloop()