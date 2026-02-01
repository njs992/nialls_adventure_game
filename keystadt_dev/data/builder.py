from given_names.female      import FEMALE_GIVEN_NAMES
from given_names.hollow      import HOLLOW_GIVEN_NAMES
from given_names.male        import MALE_GIVEN_NAMES
from family_names.list       import FAMILY_NAMES
from occupations.occupations import DEMOGRAPHICS
from occupations.list        import city_occupations

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
    def __init__(self, street_name, house_number, gender, age, family_name, parents=None ):
        ## Address ##
        self.street_name = street_name
        self.house_number = house_number
        self.gender = gender
        self.age = age
        self.family_name = family_name
        self.parents = parents
        # gender_type = random.randint(1,11)
        # self.gender = "Male"
        # self.given_name = None
        # if gender_type == 11:
        #     self.gender = "Hollow"
        #     self.given_name = random.choice( HOLLOW_GIVEN_NAMES )
        # elif ( gender_type % 2 ) == 0:
        #     self.gender = "Female"
        #     self.given_name = random.choice( FEMALE_GIVEN_NAMES )
        # else:
        #     self.given_name = random.choice( MALE_GIVEN_NAMES )
        # #if

        ## Occupation, Stats ##
        occupation_data = random.choice( city_occupations )
        self.occupation = occupation_data.name
        self.level = occupation_data.level
        self.POW = 6 + ( 4 * occupation_data.pow )
        self.AGY = 6 + ( 4 * occupation_data.agy )
        self.HRT = 6 + ( 4 * occupation_data.hrt )
        self.COM = 6 + ( 4 * occupation_data.com )
        self.DEF = self.AGY - occupation_data.agy
        self.FOR = self.HRT - occupation_data.hrt
        # 3d4 + bonus totals * level
        # only 3d4 instead of 4d4 because the bonuses * level may add too much
        self.LIFE = sum([random.randint(1,4) for i in range(3)]) \
                    + self.level * ( \
                    + occupation_data.pow \
                    + occupation_data.agy \
                    + occupation_data.hrt \
                    + occupation_data.com )
        self.wealth = sum([random.randint(1,6) for i in range(self.level)])
    #def
#class

# Family member meanings:
# Parent: demographic->grown
# Child: demographic->next-younger of parent
# Single-parent: 10% chance for the child to have a child if they fall into the grown demographic. The child of a single-parent has the family name "Tsi'<single-parent's given name>"
FAMILY_TYPE_OPTIONS = [
    "nuclear", # male parent, female parent, rest are male or female child. All share family name except single-parent child.
    "cohabitant", # male parent, female parent, rest are male or female child. Parents have own family names, rest have hyphenated combo of grown family names except single-parent child.
    "generational", # male parent, female parent, rest are male or female child. parents share family name, for rest female have the family name "Ebra'<male grown's given name>" and the male have the family name "Ebra'<female grown's given name>" except single-parent child.
    "roommates", # Each resident is an independently determined grown with randomly selected gender and family name. Any may be single-parent.
    "household" # Half of the residents (rounded down) are similar to a nuclear family, other residents are treated as roommates
]

def get_residents(street_name, house_number, family_types, resident_count):
    residents = []
    family_type = random.choice( family_types )

    if family_type == "nuclear":
        # Create nuclear family with parents and children
        genders = ["Male", "Female"] + [random.choice(["Male", "Female"]) for _ in range(resident_count - 2)]
        for i, gender in enumerate(genders):
            given_names = MALE_GIVEN_NAMES if gender == "Male" else FEMALE_GIVEN_NAMES
            given_name = random.choice(given_names)
            resident = Resident(street_name, house_number, gender, i, random.choice(FAMILY_NAMES))
            residents.append(resident)

    elif family_type == "cohabitant":
        # Parents with different family names, children with hyphenated names
        parent_names = [random.choice(FAMILY_NAMES), random.choice(FAMILY_NAMES)]
        for i in range(resident_count):
            gender = random.choice(["Male", "Female"])
            family_name = f"{parent_names[0]}-{parent_names[1]}" if i > 1 else parent_names[i % 2]
            resident = Resident(street_name, house_number, gender, i, family_name)
            residents.append(resident)

    elif family_type == "generational":
        # Parents share name, children have derived names
        parent_name = random.choice(FAMILY_NAMES)
        for i in range(resident_count):
            gender = random.choice(["Male", "Female"])
            family_name = parent_name if i < 2 else f"Ebra'{random.choice(MALE_GIVEN_NAMES)}"
            resident = Resident(street_name, house_number, gender, i, family_name)
            residents.append(resident)

    elif family_type == "roommates":
        # Each resident is independent
        for i in range(resident_count):
            gender = random.choice(["Male", "Female"])
            resident = Resident(street_name, house_number, gender, i, random.choice(FAMILY_NAMES))
            residents.append(resident)

    elif family_type == "household":
        # Half nuclear family, half roommates
        nuclear_count = resident_count // 2
        for i in range(resident_count):
            gender = random.choice(["Male", "Female"])
            family_name = random.choice(FAMILY_NAMES) if i >= nuclear_count else random.choice(FAMILY_NAMES)
            resident = Resident(street_name, house_number, gender, i, family_name)
            residents.append(resident)

    return residents
#def

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

