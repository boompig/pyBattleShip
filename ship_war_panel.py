'''
Written by Daniel Kats
March 4, 2013
'''

from Tkinter import *
from ship_model import Ship

class ShipWarPanel(Frame):
	'''Panel to keep track of ships during wartime.
	Track damage and status.'''
	
	########### colors ############
	RECT_NULL_FILL = "forest green"
	RECT_HIT_FILL = "red"
	###############################
	
	######### geometry ############
	Y_SPACING = 20
	RECT_SIZE = 15
	LEFT_PADDING = 10
	TOP_PADDING = 10
	###############################

	def __init__(self, master):
		Frame.__init__(self, master)
		self._create_ui()
		
	def _create_ui(self):
		'''Create all UI widgets.'''
	
		self._l = Label(self, text="My Ships")
		self._l.grid(row=0)
		self._c = Canvas(self)
		self._c.grid(row=1)
		
		self._create_ships()
		
		self.pack_ui()
		
	def update(self, ship, hit_list=None):
		'''Update the given ship.'''
		
		if hit_list is None:
			hit_list = ship.get_hit_list()
		
		for i, r in enumerate(hit_list):
			item = self._ship_squares[ship.get_short_name()][i]
		
			if r:
				self._c.itemconfig(item, fill=self.RECT_HIT_FILL)
			else:
				self._c.itemconfig(item, fill=self.RECT_NULL_FILL)
		
	def reset(self):
		for ship in Ship.SHORT_NAMES:
			s = Ship(0, 0, ship, False)
			self.update(s, [0] * s.get_size())
		
	def _create_ships(self):
		'''Create ships on the canvas.'''
		
		self._ship_squares = {}
		
		for i, ship in enumerate(Ship.SHORT_NAMES):
			y = self.TOP_PADDING + i * (self.Y_SPACING * 2 + self.RECT_SIZE)
			s = Ship(0, 0, ship, False)
			self._c.create_text(self.LEFT_PADDING, y, text=s.get_full_name().title(), anchor=NW)
			
			self._ship_squares[ship] = [None] * s.get_size()
			
			for x in range(s.get_size()):
				self._ship_squares[ship][x] = self._c.create_rectangle(
					self.LEFT_PADDING + x * self.RECT_SIZE,
					y + self.Y_SPACING,
					self.LEFT_PADDING + (x + 1) * self.RECT_SIZE,
					y + self.Y_SPACING + self.RECT_SIZE,
					fill=self.RECT_NULL_FILL,
					outline="black"
				)
		
	def pack_ui(self):
		'''Remedy for my method of hiding frames.'''
	
		self._l.pack()
		self._c.pack()
	