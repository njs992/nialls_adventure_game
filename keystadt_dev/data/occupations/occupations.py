class Occupation:
    def __init__( self, name="", per_cap=0, level=0, pow=0, agy=0, hrt=0, cmd=0 ):
        self.name = name
        self.per_cap = per_cap
        self.level = level
        self.pow = pow
        self.agy = agy
        self.hrt = hrt
        self.cmd = cmd
    #def
#class

def get_occupation_cap_total( occupation_list ):
    total = 0
    for occupation in occupation_list:
        total += occupation.per_cap
    #for
    return total
#def
