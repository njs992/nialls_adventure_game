import random

def generate_random_number():
    return random.randint(0, 99)

class Test:
    def __init__( self, min, max, avg, less, more ):
        self.min = min
        self.max = max
        self.avg = avg
        self.less = less
        self.more = more
    #def

    def output( self ):
        return self.calc_output( self.min, self.max, self.avg, self.less, self.more )
        # output = self.calc_output()
        # if output > self.max:
        #     return self.avg
        # #if
        # return output
    #def

    def calc_output( self, min, max, avg, less, more ):
        seed=random.randint( 1, 100 )
        if seed <= less:
            if avg == min:
                return min
            else:
                return self.calc_output( min, avg-1, avg-1, less, 0 )
            #if
        elif seed > ( 100 - more ):
            if avg == max:
                # whoops, try again :)
                return self.calc_output( self.min, self.max, self.avg, self.less, self.more )
            else:
                return self.calc_output( avg+1, max, avg+1, 0, more )
            #if
        else:
            return avg
        #if
    #def
#class

def test_test( min, max, avg, less, more ):
    t = Test( min, max, avg, less, more )
    data = {}
    for datum in range( min, max+1 ):
        data[ datum ] = 0
    #for
    loops = 1000000
    for _ in range( loops ):
        data[ t.output() ] += 1
    #for

    for datum in data:
        print( f"{datum:3d}: {data[ datum ]:3d} ({data[ datum ] / float( loops ) * 100.0:5.2f}%)" )
    #for
#def
