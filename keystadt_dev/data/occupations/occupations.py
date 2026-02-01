DEMOGRAPHICS = {
    "senior":   range(64,95),
    "middle":   range(32,63),
    "younger":  range(16,31),
    "adult":    range(16,63),
    "older":    range(32,95),
    "grown":    range(16,95),
    "child":    range(0,15),
    "any":      range(0,95)
}

class Occupation:
    def __init__( self, name, per_cap, level, pow, agy, hrt, com, demographic="any" ):
        self.name = name
        self.per_cap = per_cap
        self.level = level
        self.pow = pow
        self.agy = agy
        self.hrt = hrt
        self.com = com
        self.demographic = demographic
        assert( demographic in DEMOGRAPHICS.keys() )
    #def
#class

def get_occupation_cap_total( occupation_list ):
    total = 0
    for occupation in occupation_list:
        total += occupation.per_cap
    #for
    return total
#def
