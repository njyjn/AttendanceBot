#!/usr/bin/python

import sys
import time
import datetime
import re
import telepot

from telepot.delegate import per_chat_id, create_open

# modules
from settings_secret import TOKEN
from botlogger import logger
import authorized
import helper
import easter
import withinus
import manager
import video

def getTime():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S, %d %B %Y ')
    
# ''' 
#     Allows admin to add points to house through bot
# '''
# def addPoints(bot, message, requester_id):
#     ap_re = re.compile('\s*/addPoints\s+([a-zA-Z+]+)\s+(\d+)', re.I)

#     matches = re.match(ap_re, message)
#     target_house = matches.group(1)
#     points = matches.group(2)

#     try:
#         # add points to house database
#         if authorized.groupIsValid(target_house):
#             bot.sendMessage(requester_id, manager.addPoints(target_house, points))
#             # log in database
#             logger.info('%d points added to %s by %s' % (points, target_house, authorized.whoIs(requester_id)))
            
#             # inform admins
#             bot.sendMessage(authorized.groups.get('admins'), '%d points added to %s by %s' % (points, target_house, authorized.whoIs(requester_id)))
#         else:
#             # bad group parameters
#             bot.sendMessage(requester_id, 'The target house is not valid.')
#             logger.warn('%s: /addPoints denied; invalid house' % authorized.whoIs(requester_id))

#     except:
#         logger.warn('%s: /addPoints denied; no valid params!' % authorized.whoIs(requester_id))
#         bot.sendMessage(requester_id, 'Add what to what?')
#         return

def groupArg2List(groupList):
    if '+' not in groupList:
        return [groupList]
    else:
        return re.split('\s*+\s*', groupList)

#class ARIADNEbot(telepot.helper.ChatHandler):
class ARIADNEbot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(ARIADNEbot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def on_chat_message(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)

        command = message['text']
        logger.info('Received \'%s\' from \'%s\' (%s)' % (command, manager.getName(chat_id), chat_id) )

        # To save time
        def reply(reply):
            logger.info('Replied \'%s\' to %s' % (reply, chat_id))
            self.sendMessage(chat_id, reply)

        # Groups cannot talk to the bot
        if chat_id < 0:
            return

        # Return a system ready flag to the admin when the command is complete.    
        adminFlag = False
        
        # ================================ COMMANDS FOR ADMINS
        # This is for administrators.

        if authorized.isAdmin(chat_id):

            # /admin
            if command == '/admin':
                adminFlag = True
                reply('You are an admin. Commands available:\n/admin - View this\n/yell AUDIENCE: MSG\n/ls - Show all users in database\n/find FROM NAME - Show list of names you are finding.\n/update HOUSE NAME FIELD PARAM\n/purge HOUSE NAME\n/scoreb - Show scoreboard\n/award HOUSE POINTS')
            
            # /scoreb
            elif command == '/scoreb':
                adminFlag = True
                reply(manager.getScoreboard())

            # /yell
            elif command.startswith('/yell'):
                try:
                    adminFlag = True
                    audience, message = re.match('/yell\s+([a-zA-Z]+)\s*:\s*(.+)', command, re.DOTALL).groups()
                    audience = audience.lower()
                    manager.yell(self, audience, message, chat_id)
                except:
                    reply('/yell AUDIENCE: MESSAGE')
                    return
            elif command == '/qwertyuiop':
                adminFlag = True
                video.getVideoID(self, 'static/CHAOSPart2.mp4')            
            # /dm
            elif command.startswith('/dm'):
                adminFlag = True
                audience, message = re.match('\s*/dm\s+(\d+)\s+(.+)', command, re.DOTALL).groups()
                manager.dm(self, audience, message, chat_id)
            
            # /award HOUSE POINT
            elif command.startswith('/award'):
                adminFlag = True
                house, points = re.match('/award\s(aether|angstrom|hydra|sigvar|nox|verde)\s(\d+)', command, re.IGNORECASE).groups()
                reply(manager.addPoints(house, points))
            
            # /update HOUSE NAME FIELD PARAM
            elif command.startswith('/update'):
                if command == '/update':
                    reply('/update HOUSE NAME FIELD PARAM')
                    return
                else:
                    adminFlag = True 
                    house, name, field, content = re.match('/update\s+([a-zA-Z]+)\s+([a-zA-Z\s]+)\s+(name|type)\s+([a-zA-Z]+)\s*' ,command).groups()
                    reply(manager.updater(house.lower(), name.title(), field.lower(), content.lower(), chat_id))
            # /ogl HOUSE NAME
            elif command.startswith('/ogl'):
                adminFlag = True
                house, name = re.match('/ogl\s+([a-zA-Z]+)\s+(.+)\s*', command).groups()
                reply(manager.updater(house.lower(), name.title(), 'type', 'ogl', chat_id))
            # /ls al or param
            elif command.startswith('/ls'):
                adminFlag = True
                if command == '/ls':
                    reply('Did you mean /ls la?\n\nla: List all users\nhouse: List all listeners in house') 
                elif command == '/ls la':
                    reply(manager.getEnumerate('all', chat_id))
                else:
                    house = re.match('/ls\s([a-zA-Z]+)', command).group(1)
                    reply(manager.getEnumerate(house, chat_id))

            elif command.startswith('/find'):
               adminFlag == True
               if command == '/find':
                   reply('Enter a search param!')
               else:
                   house,name = re.match('/find\s([a-zA-Z]+)\s([a-zA-Z]+)', command).groups()
                   reply(manager.find(house.lower(), name.title(), chat_id))

            # CHAOS ADMIN
            elif command == '/chaospart2videosend all':
                adminFlag = True
                reply('Attempting to propagate video...')
                file_id = videoIDs.get('ChaosPart2HighRes')
                reply(manager.sendVideo(self,'test', file_id, chat_id))

            if adminFlag == True:
                reply('System ready.')
                return
        
        # /stop
        if command == '/stop':
            if manager.removeByID(chat_id):
                reply('You have been purged. Goodbye.')
            else:
                reply('You are not a citizen of Forena.')
            return
        
        # ================================ COMMANDS FOR REGISTERED USERS
        # This is for registered participants
        if authorized.isRegistered(chat_id):

            # GAME: WITHINUS
            if command.startswith('/key') or command.startswith('/answer'):
                if command == '/key' or command == '/answer':
                    reply('Be more specific.')
                else:
                    matches = re.match('\s*/(key|answer)\s+(.+)\s*', command)
                    kind = matches.group(1)
                    param = matches.group(2)
                    reply(str(withinus.responseHandler(kind,param)))                       
            # /help [<command>]
            elif command == '/help':
                reply(helper.getNaiveHelp())
            elif command.startswith('/help'):
                keyword = re.match('\s*/help\s+([a-z]+)\s*', command).group(1)
                reply(helper.getHelp(keyword))
            # /retrieve_key
            elif command == '/retrieve_key':
                reply(str(chat_id))
            # /me
            elif command == '/me':
                reply(manager.getMe(chat_id))

            # /points
            elif command == '/points':
                # reply(manager.getPoints(chat_id))
                reply(manager.getScoreboard())

            else:
                reply(easter.responseHandler(command))
        
        # ================================ COMMANDS FOR UNREGISTERED USERS
        # for '/start'
        elif command == '/start':
            reply('[I missed you] Hello there. Please enter \'/start Full Name House\'\n\nEg: /start Justin Ng Aether')
        elif command.startswith('/start'):
            matches = re.match('\/start\s+([a-zA-Z ]+)\s+(aether|angstrom|hydra|nox|sigvar|verde)', command, re.IGNORECASE)
            if matches is None:
                reply('Please follow the appropriate format: \'/start Your Name Faction\'')
            else:
                name = matches.group(1)
                house = matches.group(2)
                logger.info('/name: %s is \'%s\' from \'%s\'' % (chat_id, name, house))
                manager.add(house.lower(), name.title(), chat_id)
                reply('Welcome to Forena. Enter /me to view your ID, or /help to see what you can do.')
        # otherwise it must be trying to talk to ARIADNE!
        else:
            reply('You are not a citizen of Forena. Press /start.')
        return

logger.info('ARIADNE is listening ...')

bot = ARIADNEbot(TOKEN)
bot.message_loop()

#bot = telepot.DelegatorBot(TOKEN, [(per_chat_id(), create_open(ARIADNEbot, timeout=120)),])

while 1:
    time.sleep(500)
