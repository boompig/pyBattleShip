from collections import OrderedDict
import itertools
from six.moves import filter
from sys import stdout

from ship_model import Ship


class GridModel(object):
    '''Model for one grid.
    
    Below are data representations:
        * _state_dict:
            maps squares which have been fired upon to the result (SINK, HIT, SUNK)
            HIT squares are updated to SUNK once the ship has been sunk
            Used by opponent to query status
        * _coords:
            maps squares on which ships are placed to name of ship placed there
        * _ships:
            maps name of ship to Ship object (containing location info)
            this is always up to date
    '''
    
    # this is more-or-less static
    SIZE = 10
    
    def __init__(self):
        '''Create a new grid model.'''
    
        self.reset()
    
    def reset(self):
        self._ships = {}
        self._coords = {}
        self._finalized = False
        self._state_dict = OrderedDict()
        
    def finalize(self, error_check=True):
        '''Create data structures that are costly to create but useful for ship lookup during second half of game.
        <code>error_check</code> determines whether to make sure the grid is correct. Usually on, off for debugging.'''
    
        if error_check:
            assert len(self._ships) == len(Ship.SHIPS)
        
        for ship_name, s in self._ships.items():
            for sq in s.get_covering_squares():
                self._coords[sq] = ship_name
        
        self._finalized = True
        
    def get_sunk_ship(self, x, y):
        '''Return sunk ship at (x, y).
        If ship is not sunk, return None.'''
        
        s = self._ships[self._coords[(x, y)]]
        if s.is_sunk():
            return s
            
    def get_ship_at(self, x, y):
        '''Return the ship at the given coordinates.
        Try not to abuse this.'''
        
        if (x, y) in self._coords:
            return self._ships[self._coords[(x, y)]]
        
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
        
    def all_sunk(self):
        '''Return True iff all the ships on this grid have been sunk.'''
        
        return all([s.is_sunk() for s in self._ships.values()])
        
    def get_null_squares(self):
        '''Return the set of all squares that have not yet been fired upon.
        Actually returns an itertools object.'''
        
        all_squares = itertools.product(range(self.SIZE), range(self.SIZE))
        #print tuple(all_squares)
        l = filter(self.is_empty_square, all_squares)
        #print tuple(l)
        return l
    
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
        
    def is_empty_square(self, sq):
        '''Return True iff the square (x, y) has not been fired upon.'''
    
        #print sq
        #print Ship.get_state_name(self.get_state(*sq))
        return self.get_state(*sq) == Ship.NULL
        
    def _can_add_ship(self, s):
        '''This is a helper function
        Whether the given ship can be added to the grid.
        There are actually two use cases:
            - when placing initially, consider secret ships
            - when constructing model of opponent, hide secret ships'''
    
        for other_name, other_ship in self._ships.items():
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

    def can_add(self, s):
        '''Wether the given ship *object* can be added to the grid.'''

        return all([self.is_valid_square(x, y) for x, y in s.get_covering_squares()]) and self._can_add_ship(s)
        
    
    def can_add_ship(self, x, y, ship, vertical):
        '''Whether the given ship can be added to the grid.
        There are actually two use cases:
            - when placing initially, consider secret ships
            - when constructing model of opponent, hide secret ships'''
            
        s = Ship(x, y, ship, vertical)
        return self.can_add(s)
    
    def remove_ship(self, remove_name):
        '''Remove the ship with given name'''
                
        if remove_name not in self._ships:
            return False
        else:
            del(self._ships[remove_name])
            return True

    def add(self, s):
        '''Add the given ship *object*.'''

        added = False

        if self.can_add(s):
            self._ships[s.get_short_name()] = s
            added = True

        return added
    
    def add_ship(self, x, y, ship, vertical):
        '''Add a new ship, or change orientation of existing ship.'''
        
        s = Ship(x, y, ship, vertical)
        return self.add(s)
        
    def has_all_ships(self):
        '''Return True iff the grid has all ships placed.'''
        
        return len(self._ships) == 5
        
    def read_json(self, obj):
        '''Read configuration from JSON object.'''
        
        pass
        
    def get_ship_placement(self):
        '''Return dictionary for the ship placement on this board.
        Structure: {<ship_short_name> : [x, y, vertical (T/F)], ... }'''
        
        return {name: [ship._x, ship._y, ship.is_vertical()] for name, ship in self._ships.items()}
        
    def get_ships(self):
        '''Return a mapping of ship name to ship object: {str ==> Ship}
        This is the original object, so should only be used for read operations.'''
        
        return self._ships
    
    def get_missed_shots(self):
        '''Return a list of shots on this grid, but only those that missed.'''
        
        return filter(lambda sq: self._state_dict[sq] == Ship.MISS, self._state_dict.keys())
        
    def get_shots(self):
        '''Return list of shots made on this grid.'''
        
        return self._state_dict.keys()
    
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
        '''Show the configuration that will be written to disk.'''
    
        self._write(stdout)
    
    def _write(self, f):
        '''Write the configuration of this model to the given open file.'''
    
        for ship in self._ships.values():
            line = "%s %d %d %s" % (ship.get_name(), ship._x, ship._y, ship._get_str_v()[0])
            f.write(line + "\n")
    
    def write(self, fname):
        '''Write configuration to file.'''
        
        f = open(fname, "w")
        self._write(f)
        f.close()
            
class GridAsciiDrawer(object):
    '''Class to draw the grid in ASCII for command-line debugging.
    Can display grid in different drawing modes.
    
    Here are drawing modes and their definitions:
        * SHOW_PLACEMENT_ONLY: only show placement, do not show shots
        * SHOW_ENEMY_STYLE: show hits and misses, also sunk ships
        * SHOW_ALL: show hits and misses, as well as placed ships (sunk ships are hard to show)
        
    Here are characters and their definitions:
        * HIDDEN_HIT_CHAR: character indicating ship on the square is hit
        * HIDDEN_MISS_CHAR: character indicating a miss
        * NULL_CHAR: character indicating square is empty (or has unknown value)
        * SUNK_CHAR: character indicating ship on the square is sunk
    '''
    
    # drawing modes:
    SHOW_PLACEMENT_ONLY = 1
    SHOW_ENEMY_STYLE = 2
    SHOW_ALL = 3
    
    # different types of characters
    HIDDEN_HIT_CHAR = 'x'
    HIDDEN_MISS_CHAR = '\''
    NULL_CHAR = '.'
    SUNK_CHAR = '!'
    
    def get_hit_ship_char(self, ship, mode):
        '''Return the character for the ship that is hit depending on the mode.'''
        
        return {
            self.SHOW_PLACEMENT_ONLY : ship,
            self.SHOW_ENEMY_STYLE : self.HIDDEN_HIT_CHAR,
            self.SHOW_ALL : ship + self.HIDDEN_HIT_CHAR.upper()
        } [mode]
        
    def get_sunk_ship_char(self, ship, mode):
        '''Return the character for the ship that is sunk depending on the mode.'''
        
        return {
            self.SHOW_PLACEMENT_ONLY : ship,
            self.SHOW_ENEMY_STYLE : ship,
            self.SHOW_ALL : ship + self.SUNK_CHAR.upper()
        } [mode]
        
    def get_hidden_ship_char(self, ship, mode):
        '''Return the character for the ship that is not hit depending on the mode.'''
        
        return {
            self.SHOW_PLACEMENT_ONLY : ship,
            self.SHOW_ENEMY_STYLE : self.NULL_CHAR,
            self.SHOW_ALL : ship.ljust(2)
        } [mode]
        
    def get_miss_ship_char(self,ship, mode):
        '''Return the character for the square that was shot at (no ship there).
        Ship is a parameter that will always be None (so this works with switch statement).'''
        
        return {
            self.SHOW_PLACEMENT_ONLY : self.NULL_CHAR,
            self.SHOW_ENEMY_STYLE : self.HIDDEN_MISS_CHAR,
            self.SHOW_ALL : self.NULL_CHAR + self.HIDDEN_MISS_CHAR
        } [mode]
        
    def get_empty_char(self, mode):
        '''Return the character for the square with nothing in it.'''
        
        return {
            self.SHOW_PLACEMENT_ONLY : self.NULL_CHAR,
            self.SHOW_ENEMY_STYLE : self.NULL_CHAR,
            self.SHOW_ALL : self.NULL_CHAR.ljust(2)
        } [mode]
        
    def get_spacing_char(self, mode):
        '''Return spacing based on the mode.'''
        
        return (" " if mode == self.SHOW_ALL else "")
    
    def draw(self, grid, mode=None):
        '''Show ascii version of the grid. Used for command-line debugging.
        Mode is the drawing mode (see top-level comments)
        Default mode is SHOW_PLACEMENT_ONLY'''
        
        if mode is None:
            mode = self.SHOW_PLACEMENT_ONLY
        
        for row in range(10):
            for col in range(10):
                sq = (col, row)
                ship = grid._coords[sq] if sq in grid._coords else None
                
                if sq in grid._state_dict:
                    c = {
                        Ship.MISS : self.get_miss_ship_char,
                        Ship.HIT : self.get_hit_ship_char,
                        Ship.SUNK : self.get_sunk_ship_char
                    } [grid._state_dict[sq]](ship, mode)
                elif sq in grid._coords:
                    c = self.get_hidden_ship_char(ship, mode)
                else:
                    c = self.get_empty_char(mode)
                
                stdout.write(c + self.get_spacing_char(mode))
                
            stdout.write("\n")
        
if __name__ == "__main__":
    pass
