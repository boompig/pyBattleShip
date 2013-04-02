from copy import deepcopy
            
'''
Written by Daniel Kats
March 4, 2013
'''
            
class Ship(object):
    '''An object representing a ship in a game of Battleship.'''

    NULL = 0
    MISS = 1
    HIT = 2
    SUNK = 3
    OTHER = -1
    
    SIZES = {
        "a" : 5,
        "b" : 4,
        "d" : 3,
        "s" : 3,
        "m" : 2
    }
    
    SHORT_NAMES = [
        "a",
        "b",
        "d",
        "s",
        "m"
    ]
    
    NAMES = {
        "a" : "aircraft carrier",
        "b" : "battleship",
        "d" : "destroyer",
        "s" : "submarine",
        "m" : "minesweeper"
    }
    
    SHOT_RESULTS = {
        NULL : "NULL",
        MISS : "MISS",
        HIT : "HIT",
        SUNK : "SUNK"
    }
    
    SHIPS = [
        "aircraft carrier",
        "battleship",
        "destroyer",
        "submarine",
        "minesweeper"
    ]

    @staticmethod
    def get_state_name(state):
        '''Return the name of the given state.'''
        
        return {Ship.NULL : "NULL",
                Ship.HIT : "HIT",
                Ship.SUNK : "SUNK"} [state]

    def __init__(self, x=None, y=None, type=None, vertical=None):
        '''Create a new ship with the given parameters.
        Throw assertion error if incorrect ship type given.'''
    
        self._x = x
        self._y = y
        self._type = type
        self._vertical = vertical
        self._full_name = None
        
        if self._type is not None:
            assert self._type in self.SIZES.keys()
            self._size = Ship.SIZES[self._type]
            
            for name in self.SHIPS:
                if name.lower()[0] == self._type:
                    self._full_name = name
                    break
        
        self._hit = set([])
        
    def is_vertical(self):
        '''Return True iff this ship is oriented vertically.'''
    
        return self._vertical
        
    def coords(self):
        '''Return coordinates of ship's root
        i.e. top or left square.'''
    
        return (self._x, self._y)
        
    def get_origin(self):
        '''Alias for coords.'''
    
        return self.coords()
        
    def get_size(self):
        '''Return the size (in number of tiles) of this ship.'''
    
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
        
    def get_hit_list(self):
        '''Return the list of hits as a boolean array.'''
        
        return [coord in self._hit for coord in self.get_covering_squares()]
        
    def mark(self, x, y):
        '''Mark the given spot as a hit.'''
    
        self._hit.add((x, y))
        
    def rotate(self):
        '''Change the orientation of this ship.'''
        
        self._vertical = not self._vertical
            
    def intersects_with(self, other):
        '''Return True iff this ship intersects with another ship.'''
    
        s1 = self.get_covering_set()
        s2 = other.get_covering_set()
        return len(s1.intersection(s2)) > 0
        
    def get_name(self):
        '''Return the name of this ship.
        This is the short name.'''
    
        return self._type
        
    def get_short_name(self):
        '''Return single letter identifier for this ship.'''
    
        return self._type
        
    def get_full_name(self):
        '''Return full name for this ship.'''
        
        return self._full_name
        
    def is_sunk(self):
        '''Return True iff this ship is sunk.'''
    
        return len(self._hit) == self._size
        
    def _get_str_v(self):
        if self._vertical:
            return "vertical"
        else:
            return "horizontal"
        
    def __str__(self):
        return "Ship %s @ %s oriented %sly" % (self._type, str((self._x, self._y)), self._get_str_v())
            
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
            
            if ship_type in Ship.SIZES:
                ship = Ship(x=int(x), y=int(y), type=ship_type, vertical=v)
                ships.append(ship)
                
        f.close()
                
        return ships
        