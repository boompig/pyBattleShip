from grid_model import GridModel
from ship_model import Ship
from sys import stdout

class ShipAI(object):


	def __init__(self, grid_model=None):
		if grid_model is None:
			grid_model = GridModel()
			
		self._model = grid_model
		
		self._grid = {}
		self._unsunk_ships = Ship.SIZES.keys()
		
	def get_shot(self):
		max_val = 0
		best_shot = None
	
		for x in range(GridModel.SIZE):
			for y in range(GridModel.SIZE):
				if self._grid[(x, y)] > max_val:
					best_shot = (x, y)
					max_val = self._grid[best_shot]
					
		return best_shot
		
	def set_shot_result(self, x, y, result):
		if result == Ship.SUNK:
			# have to re-check whole initial bit of stat model
			# necessary to set sunk ship squares properly
			s = self._model.get_sunk_ship(x, y)
			self._unsunk_ships.remove(s.get_name())
			margin = s.get_size()
		else:
			margin = 5
			
		# remake the stat model around this ship
		self.make_stat_model()#x - margin, x + margin, y - margin, y + margin)
		
		
	def _prelim_mark_stat_model_square(self, x, y):
		state = self._model.get_state(x, y)
				
		if state == Ship.NULL:
			self._grid[(x, y)] = 0
		else:
			# mark as negative
			# allow for some distinguishing marks between hit and miss
			self._grid[(x, y)] = state * -1
		
	def prelim_mark_stat_model(self):
		for x in range(GridModel.SIZE):
			for y in range(GridModel.SIZE):
				self._prelim_mark_stat_model_square(x, y)
		
	def make_stat_model(self):#, x_start=0, x_end=GridModel.SIZE, y_start=0, y_end=GridModel.SIZE):
		'''(re)compute the statistical model in the given range.'''
		
		# initialize all squares
		self.prelim_mark_stat_model()
	
		for x in range(0, GridModel.SIZE):
			for y in range(0, GridModel.SIZE):
			
				for ship in self._unsunk_ships:
					for v in [True, False]:
						s = Ship(x, y, ship, v)
						
						r = self.add_ship_to_stat_model(s)
				
	def get_ship_stat_weight(self, s):
		w = 1
	
		for sq in s.get_covering_squares():
			state = self._model.get_state(*sq)
			
			# means this configuration is impossible
			# contribute nothing to probability of that spot
			if state in [Ship.SUNK, Ship.MISS]:
				return 0
			elif state == Ship.HIT:
				w += 5 # add bonus for every hit
				
		return w
				
	def add_ship_to_stat_model(self, s):
		'''Add a given *hypothetical* ship to the statistical model.
		More hits along a ship count for more likelihood that it is real.'''
	
		# first, can the grid add the ship?
		if self._model.can_add_ship(s._x, s._y, s.get_name(), s._vertical):
			# next, can the statistical model add the ship?
			squares = s.get_covering_squares()
			if all([self._model.get_state(*sq) not in [Ship.MISS, Ship.SUNK] for sq in squares]):
				w = self.get_ship_stat_weight(s)
			
				for sq in squares:
					if self._grid[sq] >= 0:
						self._grid[sq] += w
				return True
			
		return False
		
	def read_stat_model(self, fname):
		f = open(fname)
		
		for x, line in enumerate(f):
			for y, val in enumerate(line.split()):
				self._grid[(x, y)] = int(val)
		
		f.close()
		
	def show_stat_model(self):
		self._write_stat_model(stdout)
		
	def _write_stat_model(self, f):
		for x in range(GridModel.SIZE):
			line = ""
		
			for y in range(GridModel.SIZE):
				line += str(self._grid[(x, y)]).ljust(3) + " "
			f.write(line.strip() + "\n")
		
	def write_stat_model(self, fname):
		'''Write the statistical model to disk.'''
	
		f = open(fname, "w")
		self._write_stat_model(f)
		f.close()
		
if __name__ == "__main__":
	grid = GridModel()
	grid.add_ship(4, 4, "a", True)
	grid.finalize()
	
	ai = ShipAI(grid)
	ai.read_stat_model("stat")
	#ai.show_stat_model()
	
	result = Ship.NULL
	c = 0
	ai.show_stat_model()
	
	for i in range(10):
		shot = ai.get_shot()
		print "Shot: " + str(shot)
		#print "Shot: {}".format(shot)
		result = grid.process_shot(*shot)
		print "Result: " + Ship.SHOT_RESULTS[result]
		ai.set_shot_result(*shot, result=result)
		
		if result == Ship.HIT:
			c += 1
	
		ai.show_stat_model()
		
	