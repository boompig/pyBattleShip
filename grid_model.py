from ship_model import Ship
from sys import stdout

class GridModel(object):
	'''Model for one grid.
	
	Here is how we will store stuff:
	<ship_name> -> <ship_object>
	
	# below, all coords, not just root
	<coord> -> <ship_name>
	'''
	
	SIZE = 10
	
	def __init__(self):
		'''Create a new grid model.'''
	
		self.reset()
	
	def reset(self):
		self._ships = {}
		self._coords = {}
		self._finalized = False
		self._state_dict = {}
		
	def finalize(self):
		assert len(self._ships) == len(Ship.SHIPS)
		
		for ship_name, s in self._ships.iteritems():
			for sq in s.get_covering_squares():
				self._coords[sq] = ship_name
		
		self._finalized = True
		
	def get_sunk_ship(self, x, y):
		'''Return sunk ship at (x, y).
		If ship is not sunk, return None.'''
		
		s = self._ships[self._coords[(x, y)]]
		if s.is_sunk():
			return s
		
	def process_shot(self, x, y):
		'''Process shooting the given square.
		Return result.'''
		
		if not self._finalized:
			self.finalize()
		
		result = Ship.MISS
	
		sq = (x, y)
		if sq in self._coords:
			s = self._ships[self._coords[sq]]
			s.mark(x, y)
			if s.is_sunk():
				result = Ship.SUNK
				for p_sq in s.get_covering_squares():
					self._state_dict[p_sq] = Ship.SUNK	
			else:
				result = Ship.HIT
			
		self._state_dict[sq] = result
		#print "[GRID] {} -> {}".format(sq, Ship.SHOT_RESULTS[self._state_dict[sq]])
		return result
		
	def get_state(self, x, y):
		'''Return state of given square.'''
	
		sq = (x, y)
		
		if sq in self._state_dict:
			return self._state_dict[sq]
		else:
			return Ship.NULL
		
	def is_valid_square(self, x, y):
		'''Return True iff (x, y) is a valid square on this grid.'''
	
		return 0 <= x < self.SIZE and 0 <= y < self.SIZE
		
	def is_empty_square(self, x, y):
		return self.get_state == Ship.NULL
		
	def _can_add_ship(self, s):
		'''This is a helper function
		Whether the given ship can be added to the grid.
		There are actually two use cases:
			- when placing initially, consider secret ships
			- when constructing model of opponent, hide secret ships'''
	
		for other_name, other_ship in self._ships.iteritems():
			# ignore unsunk ships once ship placement is finalized
			if self._finalized and not other_ship.is_sunk():
				continue
		
			# can overlap with itself
			if other_name == s.get_name():
				continue
				
			# conflicts with another ship
			if s.intersects_with(other_ship):
				return False
		
		# no conflict
		return True
		
	def can_add_ship(self, x, y, ship, vertical):
		'''Whether the given ship can be added to the grid.
		There are actually two use cases:
			- when placing initially, consider secret ships
			- when constructing model of opponent, hide secret ships'''
			
		s = Ship(x, y, ship, vertical)
		
		return all([self.is_valid_square(x, y) for x, y in s.get_covering_squares()]) and self._can_add_ship(s)
	
	def remove_ship(self, remove_name):
		'''Remove the ship with given name'''
				
		if remove_name not in self._ships:
			return False
		else:
			del(self._ships[remove_name])
			return True
	
	def add_ship(self, x, y, ship, vertical):
		'''Add a new ship, or change orientation of existing ship.'''
		
		added = False
		
		if self.can_add_ship(x, y, ship, vertical):
			s = Ship(x, y, ship, vertical)
			self._ships[ship] = s
			added = True
			
		return added
		
	def has_all_ships(self):
		'''Return True iff the grid has all ships placed.'''
		
		return len(self._ships) == 5
		
	def rotate_ship(self, ship_name):
		'''Rotate the existing ship located at (x, y).
		If no such ship exists, do nothing.'''
		
		if ship_name in self._ships:
			s = self._ships[ship_name]
			result = self.add_ship(s._x, s._y, s._type, not s._vertical)
			return result
		else:
			return False
		
	def read(self, fname):
		'''Load configuration from file.'''
		
		f = open(fname)
		for line in f:
			if len(line.strip()) == 0 or line.strip().count(" ") != 3:
				continue
			ship, x, y, v = line.split()
			r = self.add_ship(int(x), int(y), ship, v == "v")
			assert r # always have to load valid cofiguration
		f.close()
		
	def show(self):
		self._write(stdout)
		
	def _write(self, f):
		for ship in self._ships.itervalues():
			line = "%s %d %d %s" % (ship.get_name(), ship._x, ship._y, ship._get_str_v()[0])
			f.write(line + "\n")
		
	def write(self, fname):
		'''Write configuration to file.'''
		
		f = open(fname, "w")
		self._write(f)
		f.close()
		
if __name__ == "__main__":
	g = GridModel()
	g.read("enemy_ships")
	g.show()
	g.finalize()
	
	print g.process_shot(0, 0)
	assert g.process_shot(0, 0) == Ship.HIT