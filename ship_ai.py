'''
Written by Daniel Kats
March 5, 2013
'''

#################################################
#                    IMPORTS                        #
from ship_model import Ship
from grid_model import GridModel
#                                                #
#################################################
#                                                #
from collections import deque
from sys import maxint, stdout
#                                                #
#################################################

def minint():
    '''Return system's most negative int.'''

    return -1 * maxint - 1

class ShipAI(object):
    '''A naive battleship AI.'''


    def __init__(self, home_grid_model=None, enemy_grid_model=None):
        if enemy_grid_model is None:
            enemy_grid_model = GridModel()
        if home_grid_model is None:
            home_grid_model = GridModel()
        
        self._enemy_model = enemy_grid_model
        self._home_model = home_grid_model
        self.reset()
        
    def place_ships(self):
        '''Place the ships on the grid.
        This placement will be sub-optimal but still mildly smart.'''
        
        self.reverse_probs()
        self._placements = {}

        for val in sorted(self._d.keys()):
            for root in self._d[val]:
                for ship in filter(lambda s: s not in self._placements, Ship.SHORT_NAMES):
                    if self.try_place(root, ship):
                        if len(self._placements) == 5:
                            return True
                        # break here, because no point adding different ship to same place
                        break

    def print_results(self):
        '''Show results of placement.'''

        for item in self._placements.itervalues():
            print "**** ship: " + item.get_full_name()
            for coord in item.get_covering_squares():
                print "{} --> {}".format(coord, self._probs[coord])

    def try_place(self, root, ship):
        '''Try to place the given ship at the root, at any orientation.
        Return the result.'''

        ships = [
            Ship(root[0], root[1], ship, True),
            Ship(root[0], root[1], ship, False)
        ]

        for s in sorted(ships, key=self.get_ship_prob):
            if self._home_model.can_add(s):
                self._home_model.add(s)
                self._placements[ship] = s
                return True

        return False

    def get_ship_prob(self, s):
        '''Return sum of probabilities of given ship.'''
            
        return sum([self.get_tile_prob(coord) for coord in s.get_covering_squares()])

    def get_tile_prob(self, tile):
        '''Return probability of the tile.'''

        if self._enemy_model.is_valid_square(*tile):
            return self._probs[tile]
        else:
            # super negative
            return minint()

    def reverse_probs(self):
        '''Reverse the probability table, instead mapping from values to coordinates.'''

        self._d = {}

        for coord, val in self._probs.iteritems():
            if val not in self._d:
                self._d[val] = []

            #print "{} <-- {}".format(val, coord)
            self._d[val].append(coord)
            
        
    def load_probs(self, fname):
        '''Load probabilities from a file.'''
        
        self._probs = {}
        f = open(fname)
        
        for y, line in enumerate(f):
            for x, val in enumerate(line.split()):
                self._probs[(x, y)] = int(val)
        
        f.close()
            
    def reset(self):
        self._prev_shot = None
        self._probs = {}
        self._unsunk_ships = Ship.SIZES.keys()
        
    def get_shot(self):
        max_val = 0
        best_shot = None
    
        for x in range(GridModel.SIZE):
            for y in range(GridModel.SIZE):
                if self._probs[(x, y)] > max_val:
                    best_shot = (x, y)
                    max_val = self._probs[best_shot]
                    
        self._prev_shot = best_shot
        return best_shot
        
    def set_shot_result(self, result):
        if result == Ship.SUNK and self._prev_shot is not None:
            # have to re-check whole initial bit of stat model
            # necessary to set sunk ship squares properly
            s = self._enemy_model.get_sunk_ship(*self._prev_shot)
            self._unsunk_ships.remove(s.get_name())
            margin = s.get_size()
        else:
            margin = 5
            
        # remake the stat model around this ship
        self.make_stat_model()#x - margin, x + margin, y - margin, y + margin)
        
        
    def _prelim_mark_stat_model_square(self, x, y):
        state = self._enemy_model.get_state(x, y)
                
        if state == Ship.NULL:
            self._probs[(x, y)] = 0
        else:
            # mark as negative
            # allow for some distinguishing marks between hit and miss
            self._probs[(x, y)] = state * -1
        
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
            state = self._enemy_model.get_state(*sq)
            
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
        if self._enemy_model.can_add_ship(s._x, s._y, s.get_name(), s._vertical):
            # next, can the statistical model add the ship?
            squares = s.get_covering_squares()
            if all([self._enemy_model.get_state(*sq) not in [Ship.MISS, Ship.SUNK] for sq in squares]):
                w = self.get_ship_stat_weight(s)
            
                for sq in squares:
                    if self._probs[sq] >= 0:
                        self._probs[sq] += w
                return True
            
        return False
        
    def read_stat_model(self, fname):
        f = open(fname)
        
        for x, line in enumerate(f):
            for y, val in enumerate(line.split()):
                self._probs[(x, y)] = int(val)
        
        f.close()
        
    def show_stat_model(self):
        self._write_stat_model(stdout)
        
    def _write_stat_model(self, f):
        for x in range(GridModel.SIZE):
            line = ""
        
            for y in range(GridModel.SIZE):
                line += str(self._probs[(x, y)]).ljust(3) + " "
            f.write(line.strip() + "\n")
        
    def write_stat_model(self, fname):
        '''Write the statistical model to disk.'''
    
        f = open(fname, "w")
        self._write_stat_model(f)
        f.close()
        
        
def foo():
    grid = GridModel()
    grid.add_ship(4, 4, "a", True)
    grid.finalize()
    
    ai = ShipAI(grid)
    ai.read_stat_model("ai/stat")
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
        
if __name__ == "__main__":
    #foo()
    pass
    