### Based on darrenwee/voglbot

#!/usr/bin/python

import datetime
import time
from voglogger import logger
import pymongo

# establish connection to mongodb server
try:
    connection = pymongo.MongoClient('localhost', 27017)
except pymongo.errors.ConnectionFailure as e:
    logger.error('Failed to connect to MongoDB: %s' % e)
    logger.error('ARIADNE exiting!')
    sys.exit(1)

# database -> collection -> document
# database
db = connection['acglbot']

# collection
cgls = db['cgls']
cgs = db['cgs']
tally = db['tally']

### helper functions ###
def cgIsValid(cg):
    cg_dict = {
        'mj': True,
        'tpja': True,
        'tpjb': True,
        'vja': True,
        'vjb': True,
        'tj': True,
        'dmh': True,
    }
    return cg_dict.get(cg, False)

def cglFieldIsValid(field):
    fields = {
        'name': True,
        'cg': True,
        'chatID': True,
    }
    return fields.get(field, False)

def cgFieldIsValid(field):
    fields = {
        'l': True, # Leaders
        'ir': True, # Irregulars
        'nc': True, # Newcomers
        'f': True, # Freshies
        'v': True, # Visitors
        'nb': True, # New Believers
        'total': True, # Total tally
    }
    return fields.get(field, False)

def enumerator(cursor, fields):
    reply = ''

    # catch size 0 cursor
    if cursor.count() == 0:
        return 'No records found.'

    i = 1
    for person in cursor:
        reply += str(i) + '.\n'
        for field in fields:
            if field == 'cg':
                reply += '%s: %s\n' % (field.title(), person[field][0].title())
            else:
                reply += '%s: %s\n' % (field.title(), person[field].title())
        i += 1
        reply += '\n'

    return reply

def makeTimestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%I:%M%p, %d %B')

def exists(check_id):
    if cgls.find_one( {'chatID': str(check_id)} ) == None:
        return False
    return True

### executive functions ###

# Retrieve a singular cgl dictionary
def retrieve(check_id):
    return cgls.find_one( {'chatID': str(check_id)} )

def getMe(chatID):
    cgl = retrieve(chatID)
    return 'You are ' + cgl['name'].title() + ' from ' + cgl['cg'][0].upper() + '.\n\nContact @njyjn if not correct.'

def getName(chatID):
    try:
        return retrieve(chatID).get('name')
    except:
        return 'Unregistered user'

def getCG(chatID):
    try:
        return retrieve(chatID).get('cg')[0]
    except:
        return 'Unregistered user'

# /add
def add(cg, name, chatID):

    if cgIsValid(cg):

        # check for duplicate name
        if cgls.find( {'name': name, 'cg': cg }).count() != 0:
            logger.warn('/add failed due to duplicate entry')
            return 'There is already someone with that name and cg in the database. /add failed.'

        timestamp = str(datetime.datetime.now())
    
        logger.info('Adding \'%s\' from \'%s\' of id %s' % (name, cg, chatID))
        
        cgl = {
            'name': name,
            'cg': [cg, 'all'],
            'chatID': chatID
        }

        cgls.insert_one(cgl)
        logger.info('Added %d of id \'%s\' to \'%s\' cg' % (chatID, name, cg))
        return
    logger.info('/add failed (CG does not exist)')
    return

# /remove
def remove(cg, name, requester):
    reply = 'Removed \'%s\' of \'%s\' cg from database.' % (name, cg)

    # perform remove
    if cgls.find( {'name': name, 'cg': cg }).count() == 0:
        return 'No such record found.'
    elif cgls.find( {'name': name, 'cg': cg }).count() == 1:
        cgls.remove( {'name': name, 'cg': cg}, 1 )
        logger.info(whoIs(requester) + ': ' + reply)
        return reply

    return 'Multiple records with the same name and cg found. Contact Justin for removal.'

# /enum
def getEnumerate(cg, requester):
    if cgIsValid(cg):

        # cover the all case and single cg case
        if cg == 'all':
            cgs = ['mj', 'vja', 'vjb', 'tpja', 'tpjb', 'tj', 'dmh']
        else:
            cgs = [cg]

        reply = ''
        for target_cg in cgs:
            reply += '=====================\n'
            reply += target_cg.upper() + '\n\n'
            # query for database cursor
            results = cgls.find( {'cg': target_cg} )
            
            # sort results
            results.sort( [('name', 1)] )
    
            reply += status.title() + '\n'
    
            # catch empty cg/mode query
            if results.count() == 0:
                reply += 'No records found.\n'
            else:
                # build the reply message
                i = 1
                for person in results:
                    reply += '%d. %-15s' % (i, person['name'].title())
                    i += 1
                    if (i+1)%2 == 0:
                        reply += '\n'
                reply += '\n'
    else:
        # catch invalid parameters
        logger.info('%s: /enum query failed (invalid parameters)' % whoIs(requester))
        return 'Invalid cg or status. See \'/help enumerate\''

    logger.info('%s: Returning enumeration for \'%s\' in \'%s\'' % (whoIs(requester), status, cg))
    return reply

# /find
def find(cg, pattern, requester):
    reply = ''

    if cgIsValid(cg):
        # query for database cursor
        results = cgls.find( {'name': { '$regex': '.*' + pattern + '.*'}, 'cg': cg } )
    
        # sort results
        results.sort( [ ('name', 1) ] )

        details = ['name', 'chatID']
    
        # build the reply
        reply += 'Finding any names containing \'%s\' for \'%s\'\n\n' % (pattern, cg)
        reply += enumerator(results, details)
    else:
        # catch shitty parameters
        logger.info('%s: /find query failed (invalid parameters)' % whoIs(requester))
        return 'Invalid cg. See \'/help find\''

    logger.info('%s: Returning find query for pattern \'%s\' for \'%s\'' % (whoIs(requester), pattern, cg))
    return reply

# /updater
def updater(cg, name, field, content, requester):
    reply = 'Updating \'%s\' for \'%s\' in \'%s\' cg.\n\n' % (field, name, cg)

    if cgIsValid(cg):
        # check if result was found
        if cgls.find( {'name': name, 'cg':cg} ) == None:
            # no results
            reply += 'Could not find \'%s\' from \'%s\' cg.' % (name, cg)
        else:
            # got results
            if fieldIsValid(field) and field != 'cg':
                logger.info('%s: Updating \'%s\' for \'%s\' in \'%s\' with: \'%s\'' % (whoIs(requester), field, name, cg, content))
                cgls.update_one( {'name': name, 'cg': cg}, { '$set': { field: content } } ) # perform update
                reply += 'Successfully updated \'%s\' field for \'%s\' in \'%s\' with: \'%s\'' % (field, name, cg, content)
            else:
                reply += 'Invalid field.'
    return reply

## CG functions
# /updateAttendance
def updateAttendance(cg, field, number):
    if cgIsValid(cg):
        return cgs.update_one( { 'name': cg }, { '$set': { field: str(number) } }, upsert=True )

def isAllSubmitted():
    results = cgs.find( {'done': True } )
    if results.count() == cgs.find( {} ).count():
        updateGrandAttendance()
        reset()
        return True
    return False

def reset():
    fieldList = ['l','f','ir','nb','nc','v','total']
    for field in fieldList:
        cgs.update( {}, { '$set': { { field: 0 }, { 'done': False } } } )

# /updateGrandAttendance
# This will update the total attendance for the cluster.
def updateGrandAttendance():
    date = time.strftime('%d/%m/%Y')
    cgList = cgs.find( {} )
    total, totalL, totalF, totalIR, totalNC, totalNB, totalV = 0
    for cg in cgList:
        total += cg['total']
        totalL += cg['l']
        totalF += cg['f']
        totalIR += cg['ir']
        totalNC += cg['nc']
        totalNB += cg['nb']
        totalV += cg['v']
    tally.save( { 'date': date }, {'$set': { 'total': total, 'l': totalL, 'f': totalF, 'ir': totalIR, 'nc': totalNC, 'nb': totalNB, 'v': totalV } } )

def getCGFinalString(cg):
    cgDoc = cgs.find_one( { 'name': cg.lower() } )
    total = cgDoc['total']
    leaders = cgDoc['l']
    freshies = cgDoc['f']+'F, ' if cgDoc['f'] != 0 else ''
    ncs = cgDoc['nc']+'NC, ' if cgDoc['nc'] != 0 else ''
    nbs = cgDoc['nb']+'NB, ' if cgDoc['nb'] != 0 else ''
    irs = cgDoc['ir']+'IR, ' if cgDoc['ir'] != 0 else ''
    visitors = cgDoc['v']+'V, ' if cgDoc['v'] != 0 else ''
    string = freshies + irs + ncs + visitors + nbs
    string = rreplace(string, ', ', '', 1)
    return 'East (%s): %s+%s (%s)' % (cg.upper(), total, leaders, string)

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

# def printTally():
#     date = time.strftime('%d/%m/%Y')
#     tally.find_one( { 'date': date } )
#     mjDoc = cgs.find_one( { 'name': 'mj' } )
#     mj = '%d+%d (%s, %s, %s, %s, %s)' % (mjDoc['total'])
#     return 'East (MJ): %s\nEast (VJ A): %s\nEast (VJ B): %s\nEast (TPJ A): %s\nEast (TPJ B): %s\nEast (TJ): %s\nEast (DHS): %s\nEAST TOTAL=%s\n' % (mj, vja, vjb, tpja, tpjb, tj, dmh, total)


from authorized import whoIs
