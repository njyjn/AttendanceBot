#!/usr/bin/python

import sys
import time
import datetime
import re
import telepot

from telepot.delegate import per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

# modules
from settings_secret import TOKEN
from voglogger import logger
import authorized
import helper
import manager

def getTime():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S, %d %B %Y ')

def groupArg2List(groupList):
    if '+' not in groupList:
        return [groupList]
    else:
        return re.split('\s*+\s*', groupList)

#class ACGLBOT(telepot.helper.ChatHandler):
class ACGLBOT(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(ACGLBOT, self).__init__(*args, **kwargs)
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

        def dm(target_id, message):
            logger.info('%s messaged \'%s\' to %s' % (chat_id, reply, target_id))
            self.sendMessage(target_id, message)

        def request_add(target_id, message, to_add_cg, to_add_id, to_add_name):
            logger.info('Superadmin attention was requested from %s' % (chat_id))
            reply_markup = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='/add %s %s %s' % (to_add_cg, to_add_name, to_add_id))],['Reject'],
                ],one_time_keyboard=True,)
            self.sendMessage(target_id, message, reply_markup=reply_markup)

        # Groups cannot talk to the bot
        if chat_id < 0:
            return

        # Return a system ready flag to the admin when the command is complete.    
        adminFlag = False
        
        # ================================ COMMANDS FOR ADMINS
        # This is for superadministrators.
        if authorized.isSuperadmin(chat_id):
            if command == '/hannah':
                adminFlag = True
                reply('Hannah is wonderful <3')
            elif command.startswith('/add'):
                matches = re.match('\/add\s+(MJ|VJA|VJB|TPJA|TPJB|TJ|DMH)\s+([0-9]+)\s+([a-zA-Z ]+)', command, re.IGNORECASE)
                if matches is None:
                    reply('SUPERADMIN: Please follow the appropriate format: \'/add Their Name CG\'')
                else:
                    cg = matches.group(1)
                    target_id = matches.group(2)
                    name = matches.group(3)
                    added_message = 'Attempting to register %s (%s) into %s.' % (target_id, name, cg) 
                    logger.info(added_message)
                    manager.add(cg.lower(), name.title(), target_id)
                    
        # This is for administrators.
        if authorized.isAdmin(chat_id):
            # /admin
            if command == '/admin':
                adminFlag = True
                reply('You are an admin. Commands available:\n/admin - View this\n/yell AUDIENCE: MSG\n/ls - Show all users in database\n/find FROM NAME - Show list of names you are finding.\n/update HOUSE NAME FIELD PARAM\n/purge HOUSE NAME\n/scoreb - Show scoreboard\n/award HOUSE POINTS')
            elif command.startswith('/update'):
                if command == '/update':
                    reply('/update HOUSE NAME FIELD PARAM')
                    return
                else:
                    adminFlag = True 
                    house, name, field, content = re.match('/update\s+([a-zA-Z]+)\s+([a-zA-Z\s]+)\s+(name|type)\s+([a-zA-Z]+)\s*' ,command).groups()
                    reply(manager.updater(house.lower(), name.title(), field.lower(), content.lower(), chat_id))
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
            if adminFlag == True:
                reply('System ready.')
                return
        # /stop
        if command == '/stop':
            if manager.removeByID(chat_id):
                reply('Goodbye.')
            else:
                reply('You cannot stop what you did not begin.')
            return
        
        # ================================ COMMANDS FOR REGISTERED USERS
        # This is for registered participants
        if authorized.isRegistered(chat_id):
            # /help [<command>]
            if command == '/help':
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
            else:
                reply('Unknown command.')
        
        # ================================ COMMANDS FOR UNREGISTERED USERS
        # for '/start'
        elif command == '/start':
            reply('Hello there. Please enter \'/start Full Name CG\'\n\nEg: /start Justin Ng TJ')
        elif command.startswith('/start'):
            matches = re.match('\/start\s+([a-zA-Z ]+)\s+(MJ|VJA|VJB|TPJA|TPJB|TJ|DMH)', command, re.IGNORECASE)
            if matches is None:
                reply('Please follow the appropriate format: \'/start Your Name CG\'')
            else:
                name = matches.group(1)
                cg = matches.group(2)
                request_message = '%s (%s) from %s wants to register.' % (chat_id, name, cg) 
                logger.info(request_message)
                # manager.add(cg.lower(), name.title(), chat_id)
                request_add(authorized.superadmin, request_message, cg, name, chat_id)
                reply('Your registration has been forwarded to Justin (@njyjn) for processing. Please wait...')
        # otherwise it must be trying to talk to ARIADNE!
        else:
            reply('You are not registered. Contact Justin for more information.')
        return

logger.info('ACGLBOT is listening ...')

bot = ACGLBOT(TOKEN)
bot.message_loop()

#bot = telepot.DelegatorBot(TOKEN, [(per_chat_id(), create_open(ARIADNEbot, timeout=120)),])

while 1:
    time.sleep(500)