import random

class DwellingBuilder:
    def __init__( self, street_name, dwelling_number, unit_min,    unit_max,    unit_ave,    unit_less,    unit_more, 
                                                      denizen_min, denizen_max, denizen_ave, denizen_less, denizen_more ):
        self.street_name = street_name
        self.dwelling_number = dwelling_number
        self.unit_min = unit_min
        self.unit_max = unit_max
        self.unit_ave = unit_ave
        self.unit_less = unit_less
        self.unit_more = unit_more
        self.denizen_min = denizen_min
        self.denizen_max = denizen_max
        self.denizen_ave = denizen_ave
        self.denizen_less = denizen_less
        self.denizen_more = denizen_more
    #def

    def output( self ):
        ret_str = ""

        unit_count = self.calc_unit_count( self.unit_min, self.unit_max, self.unit_ave, self.unit_less, self.unit_more )
        for unit_idx in range( unit_count ):
            unit_tag = ""
            if self.unit_cnt > 0:
                unit_tag = f"{chr( ord( 'A' ) + unit_idx )}"
            #if

            denizen_count = self.calc_denizen_count( self.denizen_min, self.denizen_max, self.denizen_ave, self.denizen_less, self.denizen_more )

            ret_str += f"Dwelling( \"{self.dwelling_number}{unit_tag} {self.street_name}\", {denizen_count} )\n"
        #for
    #def

    def calc_unit_count( self, min, max, avg, less, more ):
        seed=random.randint( 1, 100 )
        if seed <= less:
            if avg == min:
                return min
            else:
                return self.calc_unit_count( min, avg-1, avg-1, less, 0 )
            #if
        elif seed > ( 100 - more ):
            if avg == max:
                # whoops, try again :)
                return self.calc_unit_count( self.unit_min, self.unit_max, self.unit_ave, self.unit_less, self.unit_more )
            else:
                return self.calc_unit_count( avg+1, max, avg+1, 0, more )
            #if
        else:
            return avg
        #if
    #def

    def calc_denizen_count( self, min, max, avg, less, more ):
        seed=random.randint( 1, 100 )
        if seed <= less:
            if avg == min:
                return min
            else:
                return self.calc_denizen_count( min, avg-1, avg-1, less, 0 )
            #if
        elif seed > ( 100 - more ):
            if avg == max:
                # whoops, try again :)
                return self.calc_denizen_count( self.denizen_min, self.denizen_max, self.denizen_ave, self.denizen_less, self.denizen_more )
            else:
                return self.calc_denizen_count( avg+1, max, avg+1, 0, more )
            #if
        else:
            return avg
        #if
    #def
#class
