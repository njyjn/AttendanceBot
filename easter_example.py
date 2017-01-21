import time
from random import randint
from fuzzywuzzy import fuzz, process
from voglogger import logger

# threshold for string distance
# needs to be tweaked to change sensitivity
global threshold
threshold = 80

easter = {
    '/start': ['Save server resources. Save Forena.'],
    # populate this with your own responses. Each key can hold more than one response, which is then selected randomly.
}

"""
getClosestTerm(text)
    searches the easter dictionary for the closest key match to text
"""
def getClosestTerm(text):
    top_matches = process.extract(text, easter.keys(), limit = 1)
    if top_matches[0][1] >= threshold:
        return top_matches[0][0]
    return

"""
isAlias(text, possibles)
    returns true if text can be reasonably aliased to anything in the possibles string array
"""
def isAlias(text, possibles):
    for possible in possibles:
        if fuzz.ratio(text, possible) >= threshold:
            return True
    return False

"""
getRandomResponse(trigger)
    returns a random response from the dictionary with the key as 'trigger'
    the trigger parameter must be a key inside the dictionary
"""
def getRandomResponse(trigger):
    if trigger in easter.keys():
        target = randint(0, len(easter.get(trigger)) - 1)
        return (easter.get(trigger)[target])
    return


def responseHandler(text):
    try:
        text = text.lower() # set everything to lowercase
        
        # ============ exact trigger term matches ===========
        # I have input some common queries.
        if text in easter:
            return getRandomResponse(text)

        elif 'you see me' in text or 'see see me' in text or 'you see see me' in text or 'see me' in text:
            return 'h i r a e t h'

        # ============ fuzzy match trigger terms ============
        ### for matching to something close to the actual key word ###
    #    elif getClosestTerm(text) is not None:
    #        return getRandomResponse(getClosestTerm(text))

        ### for matching to an alias of the actual key word ###
        elif isAlias(text, ['are you like siri?']):
            return getRandomResponse('siri')
        
        #All other queries/comments.
        else:
            return getRandomResponse('yes')
    
    except Exception as e:
        logger.warn(e)
        return
