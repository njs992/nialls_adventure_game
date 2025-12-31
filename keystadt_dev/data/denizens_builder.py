import random
from keystadt_dev.data.family_names.list import FAMILY_NAMES
from keystadt_dev.data.given_names.female import FEMALE_GIVEN_NAMES
from keystadt_dev.data.given_names.male import MALE_GIVEN_NAMES

class DenizenBuilder:
    def __init__( self ):
        self.families = set()
    #def

    def populate_dwelling_unit( self, dwelling ):
        ret_str = ""

        # pick a family name from FAMILY_NAMES and check if it is already used in self.families
        family_name = random.choice( FAMILY_NAMES )
        if family_name in self.families:
            while family_name in self.families:
                family_name = random.choice( FAMILY_NAMES )
            #while
        #if

        family_members = set()
        for _denizen_count in range( dwelling.denizen_count ):
            new_denizen_given_name = random.choice( FEMALE_GIVEN_NAMES )
            if new_denizen_given_name in family_members:
                while new_denizen_given_name in family_members:
                    new_denizen_given_name = random.choice( FEMALE_GIVEN_NAMES )
                #while
            #if

            # pick the occupation

            # add the denizen constructor to the output
            ret_str += f"Denizen( \"{new_denizen_given_name}\", \"{family_name}\", \"{dwelling.name}\","
            ret_str += f"\"{occupation.name}\", {occupation.pow_stat}, {occupation.agy_stat},"
            ret_str += f" {occupation.hrt_stat}, {occupation.cmd_stat}, {occupation.get_age()} )\n"
        #for
    #def
#class
