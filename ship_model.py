from copy import deepcopy

class ShipModel(object):

	SIZES = {
		"a" : 5,
		"b" : 4,
		"d" : 3,
		"s" : 3,
		"m" : 2
	}
	
	SHIPS = [
		"aircraft carrier",
		"battleship",
		"destroyer",
		"submarine",
		"minesweeper"
	]

	# this object should be inverted
	SHIP_POS = {
		"d" : set([
			(1, 2),
			(1, 3),
			(1, 4),
		]),
		
		"s" : set([
			(9, 1),
			(9, 2),
			(9, 3),
		]),
		
		"b" : set([
			(3, 4),
			(4, 4),
			(5, 4),
			(6, 4)
		]),
		
		"a" : set([
			(8, 3),
			(8, 4),
			(8, 5),
			(8, 6),
			(8, 7)
		]),
		
		"m" : set([
			(0, 0),
			(1, 0)
		])
	}
	
	NULL = 0
	HIT = 1
	SUNK = 2
	MISS = -1
	
	SIZE = 10
	
	@staticmethod
	def state_to_str(state):
		return {
			self.NULL: "NULL",
			self.HIT: "HIT",
			self.SUNK: "SUNK",
			self.MISS: "MISS"
		} [state]
	
	def reset(self):
		self._ship_pos = deepcopy(self.SHIP_POS)
		
		self._tile_states = {}
		
		# invert the stupid SHIP_POS structure
		self._ship_dict = {}
		
		for ship, coords in self._ship_pos.iteritems():
			for coord in coords:
				self._ship_dict[coord] = ship
	
	def __init__(self):
		self.reset
		
	def is_valid_square(self, x, y):
		return 0 <= x < self.SIZE and 0 <= y < self.SIZE
		
	def is_valid_ship_placement(self, x, y, ship, vertical):
		return all([ self.is_valid_square(x, y) for x, y in self.get_ship_covering_squares(x, y, ship, vertical)])
		
	def get_ship_covering_squares(self, x, y, ship, vertical):
		'''Return squares covered by the ship.'''
	
		if vertical:
			return [(x, y + i) for i in range(self.SIZES[ship])]
		else:
			return [(x + i, y) for i in range(self.SIZES[ship])]
		
	def is_hit(self, x, y):
		result = self.MISS
	
		for ship, coords in self._ship_pos.iteritems():
			if (x, y) in coords:
				result = self.HIT
				break
				
		if result != self.MISS:
			self._ship_pos[ship].remove((x, y))
			
			if len (self._ship_pos[ship]) == 0:
				print "Sunk %s" % ship
				result = self.SUNK
		
		return result
		
	def shoot(self, x, y):
		'''Shoot at the given coordinate. Return result.'''
		
		# if already shot there...
		if (x, y) in self._tile_states:
			return self._tile_states[(x, y)]
			
		# mark the shot as a hit
		result = self.MISS
			
		# if not...
		if (x, y) in self._ship_dict:
			# figure out if it's sunk or not
			ship = self._ship_dict[(x, y)]
			all_coords = self._ship_pos[ship]
			
			s = all_coords.difference(set(self._tile_states.keys()))
			#print s
			if len(s) < 2:
				# mark all the coords in tile_states as sunk
				for coord in all_coords:
					self._tile_states[coord] = self.SUNK
					
				result = self.SUNK
			else:
				result = self.HIT
		
		# save result before returning
		self._tile_states[(x, y)] = result
		return result
		
	def get_ship(self, x, y):
		if (x, y) in self._ship_dict:
			return self._ship_dict[(x, y)]
			
	def get_state(self, x, y):
		if (x, y) in self._tile_states:
			return self._tile_states[(x, y)]
		else:
			return self.NULL
			
class Ship(object):
	NULL = 0
	MISS = 1
	HIT = 2
	SUNK = 3
	
	SIZES = {
		"a" : 5,
		"b" : 4,
		"d" : 3,
		"s" : 3,
		"m" : 2
	}
	
	SHOT_RESULTS = {
		NULL : "NULL",
		MISS : "MISS",
		HIT : "HIT",
		SUNK : "SUNK"
	}

	def __init__(self, x=None, y=None, type=None, vertical=None):
		self._x = x
		self._y = y
		self._type = type
		self._vertical = vertical
		
		self._size = ShipModel.SIZES[self._type]
		
		self._hit = set([])
		
	def coords(self):
		'''Return coordinates of ship's root
		i.e. top or left square.'''
	
		return (self._x, self._y)
		
	def get_origin(self):
		'''Alias for coords.'''
	
		return self.coords()
		
	def get_size(self):
		return self._size
		
	def get_covering_squares(self):
		'''Return the squares this ship covers.'''
		
		if self._vertical:
			return [(self._x, self._y + i) for i in range(self._size)]
		else:
			return [(self._x + i, self._y) for i in range(self._size)]
			
	def get_covering_set(self):
		'''Return the *set* of covering squares.'''
		
		return set(self.get_covering_squares())
		
	def mark(self, x, y):
		self._hit.add((x, y))
			
	def intersects_with(self, other):
		'''Return True iff this ship intersects with another ship.'''
	
		s1 = self.get_covering_set()
		s2 = other.get_covering_set()
		return len(s1.intersection(s2)) > 0
		
	def get_name(self):
		return self._type
		
	def is_sunk(self):
		'''Return True iff this ship is sunk.'''
	
		return len(self._hit) == self._size
		
	def _get_str_v(self):
		if self._vertical:
			return "vertical"
		else:
			return "horizontal"
		
	def __str__(self):
		return "Ship {} @ {} oriented {}ly".format(self._type, (self._x, self._y), self._get_str_v())
			
class ShipLoader(object):
	'''Load ship object from a file.'''
	
	@staticmethod
	def read(fname):
		f = open(fname)
		ships = []
		
		for line in f:
			if len(line.strip()) == 0 or line.strip().count(" ") != 3:
				continue
				
			ship_type, x, y, v = l = line.strip().split()
			
			if ship_type in ShipModel.SIZES:
				ship = Ship(x=int(x), y=int(y), type=ship_type, vertical=v)
				ships.append(ship)
				
		f.close()
				
		return ships
		