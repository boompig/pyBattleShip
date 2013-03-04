'''
Written by Daniel Kats
March 4, 2013
'''

#################
#	IMPORTS		#
#################

from ship_model import Ship
from Tkinter import *

class ShipPlacementPanel(Frame):
	'''A frame which contains visualizations for placing ships.'''
	
	# the size of a single tile
	SHIP_TILE_SIZE = 20
	SHIP_TILE_COLOR = "steel blue"
	TAG = "staging_ship"
	CANVAS_WIDTH = 150

	def __init__(self, master):
		'''Create a new panel with the given parent.'''
	
		Frame.__init__(self, master)
		self._ship_name = StringVar()
		self._create_ui()
		self.reset()
		
	def reset(self):
		'''Remove all staged ships.'''
	
		for item in self._c.find_withtag(self.TAG):
			self._c.delete(item)
			
		self._ship_name.set("")
	
	def _create_ui(self):
		'''Create all UI objects.'''
	
		self._tl = Label(self, text="Staged Ship")
		
		self._sl = Label(self, textvariable=self._ship_name)
		
		self._c = Canvas(self)
		self._c.config(width=self.CANVAS_WIDTH)
		
		self.pack_ui()
		
	def pack_ui(self):
		self._tl.pack(padx=15)
		self._sl.pack(pady=15)
		self._c.pack(side=LEFT, padx=10, pady=10)
		
	def add_ship(self, s):
		'''Add a ship to the staging area. 
		Display what it would look like on the grid.'''
		
		self.reset()
		self._ship_name.set(s.get_full_name().title())
		
		if s.is_vertical():
			x = 0
			x_pad = (self._c.winfo_width() - self.SHIP_TILE_SIZE) / 2.0
			y_pad = (self._c.winfo_height() - self.SHIP_TILE_SIZE * s.get_size()) / 2.0
		
			for y in range(s.get_size()):
				self._draw_ship_tile(
					x_pad + x * self.SHIP_TILE_SIZE, 
					y_pad + y * self.SHIP_TILE_SIZE)
		else:
			y = 0
			x_pad = (self._c.winfo_width() - self.SHIP_TILE_SIZE * s.get_size()) / 2.0
			y_pad = (self._c.winfo_height() - self.SHIP_TILE_SIZE) / 2.0
			
			for x in range(s.get_size()):
				self._draw_ship_tile(
					x_pad + x * self.SHIP_TILE_SIZE, 
					y_pad + y * self.SHIP_TILE_SIZE)
		
	def _draw_ship_tile(self, x, y):
		'''Draw a single tile for the ship at given coordinates.'''
		
		self._c.create_rectangle(
			x,
			y,
			x + self.SHIP_TILE_SIZE,
			y + self.SHIP_TILE_SIZE,
			fill=self.SHIP_TILE_COLOR,
			outline="black",
			tag=self.TAG
		)