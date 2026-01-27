from given_names.female import FEMALE_GIVEN_NAMES
from given_names.hollow import HOLLOW_GIVEN_NAMES
from given_names.male   import MALE_GIVEN_NAMES
from family_names.list  import FAMILY_NAMES
from occupations.test   import city_occupations

import random

def get_resident_count( ave, min, max, less, more ):
    # a=[random.randint(1,10) for i in range(0,10)]
    resident_count = ave
    more_less = random.randint(0,100)
    if( more_less < less ):
        resident_count -= 1
        while( ( random.randint( 0, 100 ) < less ) and ( resident_count > min ) ):
            resident_count -= 1
        #while
    elif( more_less > ( 100 - more ) ):
        resident_count += 1
        while( ( random.randint( 0, 100 ) > ( 100 - more ) ) and ( resident_count < max ) ):
            resident_count += 1
        #while
    #if
    return resident_count
#def

class Resident:
    def __init__(self, street_name, house_number, family_name=None ):
        ## Address ##
        self.street_name = street_name
        self.house_number = house_number
        self.family_name = family_name

        ##################################################### need to add age stuff
        ## Name, gender ##
        if family_name is None:
            self.family_name = random.choice( FAMILY_NAMES )
        #if
        gender_type = random.randint(1,11)
        self.gender = "Male"
        self.given_name = None
        if gender_type == 11:
            self.gender = "Hollow"
            self.given_name = random.choice( HOLLOW_GIVEN_NAMES )
        elif ( gender_type % 2 ) == 0:
            self.gender = "Female"
            self.given_name = random.choice( FEMALE_GIVEN_NAMES )
        else:
            self.given_name = random.choice( MALE_GIVEN_NAMES )
        #if

        ## Occupation, Stats ##
        occupation_data = random.choice( city_occupations )
        self.occupation = occupation_data.name
        self.level = occupation_data.level
        self.POW = 6 + ( 4 * occupation_data.pow )
        self.AGY = 6 + ( 4 * occupation_data.agy )
        self.HRT = 6 + ( 4 * occupation_data.hrt )
        self.COM = 6 + ( 4 * occupation_data.cmd )
        self.DEF = self.AGY - occupation_data.agy
        self.FOR = self.HRT - occupation_data.hrt
        # 3d4 + bonus totals... kind of
        self.LIFE = sum([random.randint(1,4) for i in range(3)]) \
                    + occupation_data.pow \
                    + occupation_data.agy \
                    + occupation_data.hrt \
                    + occupation_data.cmd
        self.wealth = sum([random.randint(1,6) for i in range(self.level)])
    #def
#class

class StreetData:
    def __init__(self, street_name, house_count, res_ave, res_min, res_max, res_less, res_more ):
        self.street_name = street_name
        self.house_count = house_count
        self.res_ave = res_ave
        self.res_min = res_min
        self.res_max = res_max
        self.res_less = res_less
        self.res_more = res_more
    #def
#class

population = []

for street in city_data :
    for house_number in range( street.house_count ):
        for resident in range( get_resident_count(  street.res_ave, 
                                                    street.res_min, 
                                                    street.res_max, 
                                                    street.res_less, 
                                                    street.res_more ) ):
            population.append( create_resident( street.street_name, house_number+1 ) )
        #for resident
    #for house_number
#for street

