PREFIX = [
    "over",
    "under",
    "high",
    "low",
    "of",
    "from",
    "to",
    "eager",
    "big",
    "small",
    "little",
    "great",
    "old",
    "new",
    "young",
    "fast",
    "slow",
    "ster",
    "strong",
    "weak",
    "able",
    "de",
    "le",
    "san",
    "ven",
    "ham",
    "ben",
    "o'",
    "ore"
]

SUFFIX = [
    "kin",
    "ken",
    "gard",
    "port",
    "amor",
    "more",
    "les",
    "sly",
    "ist",
    "ish",
    "shep",
    "erd",
    "ard",
    "dine",
    "ie",
    "o",
    "lek",
    "er",
    "s",
    "en"
]

MAIN = [
    "brook",
    "bottom",
    "arm",
    "head",
    "hill",
    "woode",
    "stone",
    "ston",
    "cave",
    "river",
    "lake",
    "sea",
    "mille",
    "ford",
    "field",
    "dale",
    "vale",
    "gate",
    "town",
    "tonne",
    "porte",
    "path",
    "iron",
    "gold",
    "gild",
    "silver",
    "cliff",
    "stead",
    "helm",
    "ash",
    "thorn",
    "oak",
    "elm",
    "birch",
    "pine",
    "maple",
    "willow",
    "rose",
    "lily",
    "dell",
    "larke",
    "hawke",
    "foxe",
    "wolfe",
    "beare",
    "egret",
    "falcone",
    "isle",
    "mere",
    "bone",
    "forge",
    "deere",
    "cloud",
    "mist",
    "shadow",
    "weave",
    "wend",
    "felt",
    "mont",
    "mon",
    "cane",
    "cannon",
    "castle",
    "fort",
    "house",
    "hall",
    "man",
    "ladie",
    "hond",
    "bright",
    "breath",
    "oxe",
    "harte",
    "weasel",
    "wirt",
    "wil",
    "oracule",
    "might",
    "common"
]

VOWELS = [
    "a",
    "e",
    "i",
    "o",
    "u"
]

import time

def capitalize( word ):
    return word[0].upper() + word[1:]
#def

def generate_names():

    start_time = time.time()
    result = set()

    for m in MAIN:
        result.add( capitalize( m ) )

        for p in PREFIX:
            if p[-1] in VOWELS and m[0] in VOWELS:
                pm = f"{ capitalize( p ) }{ capitalize( m ) }"
            else:
                pm = f"{ capitalize( p ) }{ m }"
            #if
            result.add( pm )

            if m[-1] in VOWELS:
                pm_pre_s = pm[:-1]
                m_pre_s = capitalize( m[:-1] )
                for s in SUFFIX:
                    result.add( f"{ pm_pre_s }{ s }" )
                    result.add( f"{ m_pre_s }{ s }" )
                #for
            else:
                for s in SUFFIX:
                    if m[-2] in VOWELS and s[0] in VOWELS:
                        result.add( f"{ pm }{ pm[-1] }{ s }" )
                        result.add( f"{ capitalize( m ) }{ m[-1] }{ s }" )
                    else:
                        result.add( f"{ pm }{ s }" )
                        result.add( f"{ capitalize( m ) }{ s }" )
                #for
            #if
        #for
    #for

    # Write the result to a file as a Python list
    with open("family_names-list.py", "w", encoding="utf-8") as f:
        f.write("FAMILY_NAMES = [\n")
        for name in sorted(result):
            f.write(f"    \"{name}\",\n")
        #for
        f.write("]\n")
    #with

    end_time = time.time()
    print( f"Generated { len( result ) } unique family names!" )
    print( f"Time taken, in mS: { ( end_time - start_time ) * 1000 }" )
#def
