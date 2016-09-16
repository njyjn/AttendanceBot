### Based on darrenwee/voglbot

#!/usr/bin/python

import datetime
import time
from voglogger import logger
from authorized import whoIs
import pymongo

# establish connection to mongodb server
try:
    connection = pymongo.MongoClient('monty', 27017)

except pymongo.errors.ConnectionFailure as e:
    logger.error('Failed to connect to MongoDB: %s' % e)
    logger.error('ARIADNE exiting!')
    sys.exit(1)

# database -> collection -> document
# database
db = connection['ariadne']

# collection
students = db['students']
houses = db['houses']

### helper functions ###
def houseIsValid(house):
    houses = {
        'verde': True,
        'nox': True,
        'aether': True,
        'hydra': True,
        'angstrom': True,
        'sigvar': True,
        'all': True,
    }
    return houses.get(house, False)

def fieldIsValid(field):
    fields = {
        'name': True,
        'type': True,
        'house': True,
        'color': True,
        'chatID': True,
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
            if field == 'house':
                reply += '%s: %s\n' % (field.title(), person[field][0].title())
            elif field == 'diet' or field == 'medical':
                reply += '%s: %s\n' % (field.title(), person[field])
            else:
                reply += '%s: %s\n' % (field.title(), person[field].title())
        i += 1
        reply += '\n'

    return reply

def makeTimestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%I:%M%p, %d %B')

def exists(chatID):
    if students.find_one({'chatID': chatID}) == None:
        return False
    return True

def yell(bot, audience, message, requester):
    typeList = ['all', 'cvogl', 'ogl', 'freshie', 'gov']
    if audience in typeList:
        # yell to types

        if students.find( {'type': audience} ) != None:
            recipients = students.find( {'type': audience} )

            for recipient in recipients:
                # send to each recipient
                bot.sendMessage(recipient['chatID'], message)
        else:
            # no records from audience found
            bot.sendMessage(requester, 'Yell failed: no records found!')
    elif houseIsValid(audience):
        # yell to house (excluding 'all')

        if students.find( {'color': audience} ) != None:
            recipients = students.find( {'color': audience} )

            for recipient in recipients:
                # send to each recipient
                bot.sendMessage(recipient['chatID'], message)
        else:
            # no records from audience found
            bot.sendMessage(requester, 'Yell failed: no records found!')

### executive functions ###

# /add
def add(house, name, chatID):

    if houseIsValid(house):

        # check for duplicate name
        if students.find( {'name': name, 'house': house }).count() != 0:
            logger.warn('/add failed due to duplicate entry')
            return 'There is already someone with that name and house in the database. /add failed.'

        timestamp = str(datetime.datetime.now())
    
        logger.info('Adding \'%s\' from \'%s\' of id %s' % (name, house, chatID))
        
        student = {
            'name': name,
            'type': 'freshie',
            'house': [house, 'all'],
            'color': house,
            'chatID': chatID
        }

        students.insert_one(student)
        logger.info('Added \'%s\' of id %d to \'%s\' house' % (chatID, name, house))
        return
    logger.info('/add query failed (invalid parameters)')
    return

# /remove
def remove(house, name, requester):
    reply = 'Removed \'%s\' of \'%s\' house from database.' % (name, house)

    # perform remove
    if students.find( {'name': name, 'house': house }).count() == 0:
        return 'No such record found.'
    elif students.find( {'name': name, 'house': house }).count() == 1:
        students.remove( {'name': name, 'house': house}, 1 )
        logger.info(whoIs(requester) + ': ' + reply)
        return reply

    return 'Multiple records with the same name and house found. Contact Justin for removal.'

# /enum
def getEnumerate(house, requester):
    if houseIsValid(house):

        # cover the all case and single house case
        if house == 'all':
            houses = ['nox', 'hydra', 'verde', 'sigvar', 'aether', 'angstrom']
        else:
            houses = [house]

        reply = ''
        for target_house in houses:
            reply += '=====================\n'
            reply += target_house.upper() + '\n\n'
            # query for database cursor
            results = students.find( {'house': target_house} )
            
            # sort results
            results.sort( [ ('color', 1), ('name', 1) ] )
    
            reply += status.title() + '\n'
    
            # catch empty house/mode query
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
        return 'Invalid house or status. See \'/help enumerate\''

    logger.info('%s: Returning enumeration for \'%s\' in \'%s\'' % (whoIs(requester), status, house))
    return reply

# /find
def find(house, pattern, requester):
    reply = ''

    if houseIsValid(house):
        # query for database cursor
        results = students.find( {'name': { '$regex': '.*' + pattern + '.*'}, 'house': house } )
    
        # sort results
        results.sort( [ ('color', -1), ('name', 1) ] )

        details = ['name', 'color', 'type', 'chatID']
    
        # build the reply
        reply += 'Finding any names containing \'%s\' for \'%s\'\n\n' % (pattern, house)
        reply += enumerator(results, details)
    else:
        # catch shitty parameters
        logger.info('%s: /find query failed (invalid parameters)' % whoIs(requester))
        return 'Invalid house. See \'/help find\''

    logger.info('%s: Returning find query for pattern \'%s\' for \'%s\'' % (whoIs(requester), pattern, house))
    return reply

# /updater
def updater(house, name, field, content, requester):
    reply = 'Updating \'%s\' for \'%s\' in \'%s\' house.\n\n' % (field, name, house)

    if houseIsValid(house):
        # check if result was found
        if students.find_one( {'name': name, 'house':house} ) == None:
            # no results
            reply += 'Could not find \'%s\' from \'%s\' house.' % (name, house)
        else:
            # got results
            if fieldIsValid(field) and field != 'house':
                logger.info('%s: Updating \'%s\' for \'%s\' in \'%s\' with: \'%s\'' % (whoIs(requester), field, name, house, content))
                students.update_one( {'name': name, 'house': house}, { '$set': { field: content } } ) # perform update
                reply += 'Successfully updated \'%s\' field for \'%s\' in \'%s\' with: \'%s\'' % (field, name, house, content)
            else:
                reply += 'Invalid field.'
    return reply





