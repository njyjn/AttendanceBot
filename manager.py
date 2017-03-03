### Based on darrenwee/voglbot

#!/usr/bin/python

from datetime import datetime, timedelta
import time
from voglogger import logger
import pymongo
from settings_secret import HOSTNAME
from authorized import whoIs, number_of_clusters, number_of_cgs, cg_list, getCluster
import headmaster
import re

# establish connection to mongodb server
try:
    connection = pymongo.MongoClient(HOSTNAME, 27017)
except pymongo.errors.ConnectionFailure as e:
    logger.error('Failed to connect to MongoDB: %s' % e)
    logger.error('ARIADNE exiting!')
    sys.exit(1)

# database -> collection -> document
# database
db = connection['acglbot']

# collection
cgls = db['cgls']       # represents a user who is a cgl
cgs = db['cgs']         # represents the cg tally for attendance, one at a time.
tally = db['tally']     # represents the total tally for attendance, per a given event
state = db['state']     # represents an open/close state of an event
events = db['events']   # represents an event
events.create_index('end', expireAfterSeconds=0)

### helper functions ###
def cgIsValid(cg):
    return cg in cg_list or cg == 'all'

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
    return datetime.fromtimestamp(time.time()).strftime('%I:%M%p, %d %B')

# takes in a datetime object and adds count number of days to it
def daysFrom(dt, count):
    return timedelta(days=count) + dt 

# checks database of CGLs to see if they are registered
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
            return

        timestamp = str(datetime.now())
    
        logger.info('Adding \'%s\' from \'%s\' of id %s' % (name, cg, chatID))
        
        cgl = {
            'name': name,
            'cg': [cg, 'all'],
            'chatID': chatID
        }

        cgls.insert_one(cgl)
        logger.info('Added %s of id \'%s\' to \'%s\' cg' % (name, chatID, cg))
        return 'Thanks for waiting, %s. Welcome.' % name
    logger.info('/add failed (CG does not exist)')
    return

# /remove
def remove(cg, name, requester):
    reply = 'Removed \'%s\' of \'%s\' cg from database.' % (name, cg)
    name = name.title()
    cg = cg.lower()
    # perform remove
    if cgls.find( {'name': name, 'cg': cg }).count() == 0:
        return 'No such record found.'
    elif cgls.find( {'name': name, 'cg': cg }).count() >= 1:
        cgls.delete_one( {'name': name, 'cg': cg} )
        logger.info(whoIs(requester) + ': ' + reply)
        return reply

    return 'Multiple records with the same name and cg found. Contact Justin for removal.'

def removeById(chatID):
    logger.info('%s (%s) left.' % (whoIs(chatID), chatID))
    return cgls.delete_one( {'chatID': str(chatID)} )

# /enum
def getEnumerate(cg, requester):
    if cgIsValid(cg):

        # cover the all case and single cg case
        if cg == 'all':
            cgs = cg_list
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
    
            #reply += status.title() + '\n'
    
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

    #logger.info('%s: Returning enumeration for \'%s\' in \'%s\'' % (whoIs(requester), status, cg))
    logger.info('%s: Returning enumeration for \'%s\'' % (whoIs(requester), cg))
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

# Prepare for yell
def prepareYell(audience):
    # typeList = ['cgl', 'ps', 'member', 'cr', 'other']
    if audience == 'all':
        return cgls.find( {} )
    else:
        return cgls.find( { 'cg': { '$in': audience } } )

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

# /newevent
# creates a new attendance taking event which lasts 3 days.
# you cannot create another event until then.
def raiseEvent(name):
    if eventDoesNotExist():
        begins = datetime.today()
        expires = daysFrom(begins, 3)
        expires_string = expires.strftime('%c')
        events.save( { 'name': name, 'start': begins, 'end': expires, 'done': False, 'tally': 0, } )
        return 'You have created a new attendance event \'%s\' which expires %s' % (name, expires_string)
    else:
        return 'A counting event is still ongoing/has been completed. If the latter you must wait three days like Jesus.'

def eventDoesNotExist():
    return events.find_one( {} ) == None

def eventHasEnded():
    return events.find_one( {} )['done'] == True

# /endevent
def forceEndEvent():
    event_name = events.find_one( {} )['name']
    events.update_one( { 'done': False }, { '$set': { 'done': True } } )
    return 'Attendance event \'%s\' ended.' % event_name

def forceDeleteEvent():
    reset()
    events.delete_one( {} )
    logger.info('Event manually deleted.')
    return 'Event deleted.'

# reopen done event
def reopenEvent():
    event_name = events.find( {} )[0]['name'] 
    events.update_one( { 'done': True }, { '$set': { 'done': False } } )
    return 'Attendance event \'%s\' reopened. Now accepting /count commands.' % event_name

# /getevents
def getEvents():
    return events.find( {} )

def setAttendanceDoneForEvent(cg, isFirstTry):
    logger.info('%s has added its attendance record.' % cg)
    isit = False
    if lastToSubmitAttendance():
        isit = True
    # subsequent tries will not increment the tally count, allowing CGs to edit their attendance before all CGs have submitted.
    if isFirstTry:
        events.update_one( { 'done': False }, { '$inc': { 'tally': 1 } } )
    return isit

def lastToSubmitAttendance():
    cursor = events.find_one( { 'done': False } )
    #offset for other, pastor, cr, overseer
    #return cursor['tally'] >= (len(cg_list)-1)-len(cg_cluster_dictionary))
    return cursor['tally'] >= number_of_cgs-1

def submitClusterAttendance(cg):
    cluster = getCluster(cg)
    updateClusterAttendance(cluster)
    updateTotalAttendance()
    #return headmaster.printGrandTally()

## CG functions
# /updateAttendance
def updateAttendance(cg, field, number):
    if cgIsValid(cg):
        cluster = getCluster(cg)
        cgs.update_one( { '$and': [ {'name': cg}, {'cluster': cluster} ] }, { '$set': { field: str(number) } }, upsert=True )

def isAllSubmitted(cluster):
    results = cgs.find( { '$and': [ {'done': True }, {'cluster': cluster} ] } )
    if results.count() == cgs.find( { 'cluster': cluster } ).count():
        updateClusterAttendance(cluster)
        reset()
        return True
    return False

def isFirstTry(cg):
    return cgs.find_one( { 'name': cg } ) == None

def reset():
    # fieldList = ['l','f','ir','nb','nc','v','total']
    # for field in fieldList:
    #     cgs.update( {}, { '$set': { { field: '0' }, { 'done': False } } } )
    cgs.remove()
    tally.remove()

# /updateClusterAttendance
# This will update the total attendance for the cluster.
def updateClusterAttendance(cluster):
    cgList = cgs.find( {'cluster': cluster} )
    total = totalL = totalF = totalIR = totalNC = totalNB = totalV = 0
    for cg in cgList:
        total += int(cg.get('total', 0))
        totalL += int(cg.get('l', 0))
        totalF += int(cg.get('f', 0))
        totalIR += int(cg.get('ir', 0))
        totalNC += int(cg.get('nc', 0))
        totalNB += int(cg.get('nb', 0))
        totalV += int(cg.get('v', 0))
    tally.update_one( { 'cluster': cluster }, { '$set': { 'total': total, 'l': totalL, 'f': totalF, 'ir': totalIR, 'nc': totalNC, 'nb': totalNB, 'v': totalV } }, upsert=True )

def updateTotalAttendance():
    clusterList = tally.find( { 'cluster': { '$ne': 'all'} } )
    # Only bother if all clusters have submitted attendance
    if clusterList.count() < number_of_clusters - 1:
        return
    total = totalL = totalF = totalIR = totalNC = totalNB = totalV = 0
    for cluster in clusterList:
        total += int(cluster.get('total', 0))
        totalL += int(cluster.get('l', 0))
        totalF += int(cluster.get('f', 0))
        totalIR += int(cluster.get('ir', 0))
        totalNC += int(cluster.get('nc', 0))
        totalNB += int(cluster.get('nb', 0))
        totalV += int(cluster.get('v', 0))
    tally.update_one( { 'cluster': 'all' }, { '$set': { 'total': total, 'l': totalL, 'f': totalF, 'ir': totalIR, 'nc': totalNC, 'nb': totalNB, 'v': totalV } }, upsert=True )
