#!/usr/bin/python

import sys
import time
import datetime
import re
import telepot

from telepot.delegate import (
    per_chat_id, create_open, pave_event_space, include_callback_query_chat_id, per_callback_query_origin)
from telepot.namedtuple import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton)
import telepot.helper

# modules
from settings_secret import TOKEN, UPDATES_CHANNEL
from voglogger import logger
from headmaster import question_limit, question_bank, question_order, printGrandTally, getCGFinalString
from tools import rreplace, generateCgRegexPattern
from broadcaster import yell, dm
import authorized, helper, manager, easter

class ACGLBOT(telepot.helper.ChatHandler):
#class ACGLBOT(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(ACGLBOT, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

        # for headmaster
        self._progress = 0
        self._query_cg = None
        self.track_reply = False
        self._first_try = False

    def on_chat_message(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)

        command = message['text']
        # For headmaster to track replies from /count sequence
        try:
            reply_source_message_id = (message['reply_to_message'])['message_id']
            headcount_input = (message['text'])
        except:
            reply_source_message_id = None
            headcount_input = -1

        logger.info('Received \'%s\' from \'%s\' (%s)' % (command, manager.getName(chat_id), chat_id) )

        # To save time
        def reply(reply):
            reply = reply.encode('utf-8')
            logger.info('Replied \'%s\' to %s' % (reply, chat_id))
            #self.sendMessage(chat_id, reply)
            self.sender.sendMessage(reply)

        def request_add(target_id, message, to_add_cg, to_add_id, to_add_name):
            logger.info('Superadmin attention was requested from %s to %s' % (chat_id, target_id))
            reply_markup = ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='/add %s %s %s' % (to_add_cg, to_add_name, to_add_id))],['Reject'],
                ],one_time_keyboard=True,)
            #self.sendMessage(target_id, message, reply_markup=reply_markup)
            bot.sendMessage(target_id, message, reply_markup=reply_markup)


        # Groups cannot talk to the bot
        if chat_id < 0:
            return

        # Return a system ready flag to the admin when the command is complete.
        adminFlag = False

        # ================================ COMMANDS FOR ADMINS
        # This is for superadministrators.
        if authorized.isSuperadmin(chat_id):
            if command == '/alethea':
                reply('Alethea is wonderful <3')
                return

            elif command.startswith('/rm'):
                cg_regex_pattern = generateCgRegexPattern()
                regex_pattern = '\/rm\s+' + str(cg_regex_pattern) + '\s+([a-zA-Z ]+)'
                matches = re.match(regex_pattern, command, re.IGNORECASE)
                #matches = re.match('\/rm\s+(MJ|VJA|VJB|TPJA|TPJB|TJ|DMH|CJ\sA|CJ\sB|CJ\sC|SA\sA|SA\sB|AJ\/YJ|SR|NY\/EJ|RJA|RJB\/SJI|RJC|IJ)\s+([a-zA-Z ]+)', command, re.IGNORECASE)
                if matches is None:
                    reply('SUPERADMIN: Please follow the appropriate format: \'/rm CG Their Name')
                else:
                    cg = matches.group(1)
                    name = matches.group(2)
                    rm_message = 'Attempting to remove %s from %s.' %  (name, cg)
                    logger.info(rm_message)
                    reply(manager.remove(cg, name, chat_id))
                    return

            elif command == '/event clear':
                reply(manager.forceDeleteEvent())
                return

        # This is for administrators.
        if authorized.isAdmin(chat_id):
            # /admin
            if command == '/admin':
                adminFlag = True
                reply('You are an admin. Commands available:\n/admin - View this\n/yell AUDIENCE: MSG\n/ls - Show all users in database\n/find FROM NAME - Show list of names you are finding.\n/update HOUSE NAME FIELD PARAM\n/purge HOUSE NAME\n/scoreb - Show scoreboard\n/award HOUSE POINTS')

            elif command.startswith('/add'):
                cg_regex_pattern = generateCgRegexPattern()
                regex_pattern = '\/add\s+' + str(cg_regex_pattern) + '\s+([0-9]+)\s+([a-zA-Z ]+)'
                matches = re.match(regex_pattern, command, re.IGNORECASE)
                #matches = re.match('\/add\s+(MJ|VJA|VJB|TPJA|TPJB|TJ|DMH|CJ\sA|CJ\sB|CJ\sC|SA\sA|SA\sB|AJ\/YJ|SR|NY\/EJ|RJA|RJB\/SJI|RJC|IJ)\s+([0-9]+)\s+([a-zA-Z ]+)', command, re.IGNORECASE)
                if matches is None:
                    reply('ADMIN: Please follow the appropriate format: \'/add cg chat_id Their Name\'')
                else:
                    cg = matches.group(1)
                    target_id = matches.group(2)
                    name = matches.group(3)
                    added_message = 'Attempting to register %s (%s) into %s.' % (target_id, name, cg)
                    logger.info(added_message)
                    bot.sendMessage(target_id, manager.add(cg.lower(), name.title(), target_id))
                    logger.info('Succesfully registered %s (%s) into %s.' % (target_id, name, cg))
                    added_message = '%s (%s) added' % (name, cg.upper())
                    bot.sendMessage(chat_id, added_message, reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                    return

            elif command.startswith('/update'):
                if command == '/update':
                    reply('/update HOUSE NAME FIELD PARAM')
                    return
                else:
                    adminFlag = True
                    house, name, field, content = re.match('/update\s+([a-zA-Z]+)\s+([a-zA-Z\s]+)\s+(name|type)\s+([a-zA-Z]+)\s*' ,command).groups()
                    reply(manager.updater(house.lower(), name.title(), field.lower(), content.lower(), chat_id))

            elif command.startswith('/ls'):
                if command == '/ls':
                    reply('Did you mean /ls la?\n\nla: List all users\ncg: List all users in cg')
                    return
                elif command == '/ls la':
                    adminFlag = True
                    reply(manager.getEnumerate('all', chat_id))
                else:
                    adminFlag = True
                    cg = re.match('/ls\s([a-zA-Z]+)', command).group(1).lower()
                    reply(manager.getEnumerate(cg, chat_id))

            elif command.startswith('/find'):
                if command == '/find':
                    reply('Enter search params!')
                    return
                else:
                    adminFlag = True
                    house,name = re.match('/find\s([a-zA-Z]+)\s([a-zA-Z\s]+)', command).groups()
                    reply(manager.find(cg.lower(), name.title(), chat_id))

            elif command.startswith('/event'):
                if command == '/event' or command == '/event new':
                    reply('Use format \'/event new Event Name\' or \'/event end\' or \'/event reopen\'')
                    return
                elif command == '/event reopen':
                    adminFlag = True
                    reply(manager.reopenEvent())
                    yell(bot, 'all Attendance taking reopened.', chat_id)
                elif command == '/event end':
                    adminFlag = True
                    reply(manager.forceEndEvent())
                    yell(bot, 'all PTL, all youths have been accounted for. What a day it has been!\n\nSubscribe to %s for updates.' % UPDATES_CHANNEL, chat_id)
                    # Post attendance to official channel
                    bot.sendMessage(UPDATES_CHANNEL, str(printGrandTally()))
                elif command.startswith('/event new'):
                    adminFlag = True
                    event_name = command.replace('/event new ', '')
                    if manager.eventDoesNotExist():
                        yell(bot, 'all Counting attendance for %s has begun. Get /count -ing' % event_name, chat_id)
                    reply(manager.raiseEvent(event_name))
                elif command == '/event report':
                    adminFlag = True
                    reply(printGrandTally())
                else:
                    reply('Improper parameters supplied for /event')
                    return
            elif command.startswith('/yell'):
                if command == ('/yell'):
                    reply('/yell what?')
                    return
                adminFlag = True
                # message = command.replace('/yell ', '')
                # broadcaster.yell(bot, 'all', str(message), chat_id)
                # reply('Message yelled to all.')
                target_and_message = command.replace('/yell ', '')
                reply(yell(bot, target_and_message, chat_id))

            elif command.startswith('/dm'):
                if command == ('/dm'):
                    reply('/dm to who and what?')
                    return
                adminFlag = True
                target_and_message = command.replace('/dm ', '')
                reply(dm(bot, target_and_message, chat_id))

            if adminFlag == True:
                reply('System ready.')
                return

        # /24601
        if command == '/24601':
            reply(str(chat_id))
            return
        # /cg
        if command == '/cg':
            reply('Use the following CG abbreviation codes:')
            reply('\n'.join(str(x) for x in authorized.cg_list))
            return
        # /stop
        if command == '/stop':
            if manager.removeById(chat_id):
                reply('Goodbye.')
            else:
                reply('You cannot stop what you did not begin.')
            return

        # ================================ COMMANDS FOR REGISTERED USERS
        # This is for registered participants
        if authorized.isRegistered(chat_id):
            # Tracking Headmaster queries
            if self.track_reply:
                # Obtain CG at first run.
                if self._query_cg == None:
                    self._query_cg = manager.getCG(chat_id)
                # Throw warning messages if user exits halfway through.
                if command == 'exit':
                    if self._progress == 0:
                        reply('/count process interrupted. Your data is safe.')
                    else:
                        reply('/count process interrupted. Your data is corrupted. Please try again.')
                    self.close()
                # Check if user is counting for the first time.
                if self._progress == 0:
                    self._first_try = manager.isFirstTry(self._query_cg)
                # Edit each field of the attendance as we go along.
                try:
                    count = int(command)
                    if count < 0:
                        raise Exception('Think positive only.')
                    manager.updateAttendance(self._query_cg, question_order[self._progress], count)
                except Exception as e:
                    reply(str(e))
                    reply('Your data is corrupted. Please restart /count.')
                    self.close()
                self._progress += 1
                # Complete method if all fields have been populated.
                if self._progress >= question_limit:
                    self.sender.sendMessage(str(getCGFinalString(self._query_cg)))
                    manager.submitClusterAttendance(self._query_cg)
                    if manager.setAttendanceDoneForEvent(self._query_cg, self._first_try):
                        reply('Congratulations! You are the last to submit your attendance. Here you go ~')
                        reply(printGrandTally())
                        reply('Jesus loves the least, lost and LAST. Shalom.')
                        bot.sendMessage(authorized.superadmin, 'All CGs accounted for. %s was last.' % self._query_cg)
                    else:
                        reply('Congratulations! You are not the last to submit your attendance. /howmany encountered Jesus today?')
                        reply('Shalom out.')
                    #reply(manager.submitClusterAttendance(self._query_cg))
                    self.close()
                # otherwise send the next question
                self.sender.sendMessage(str(question_bank.get(question_order[self._progress])))
            # All other commands
            else:
                # /help [<command>]
                if command == '/help':
                    reply(helper.getNaiveHelp())
                elif command.startswith('/help'):
                    keyword = re.match('\s*/help\s+([a-z]+)\s*', command).group(1)
                    reply(helper.getHelp(keyword))
                # /me
                elif command == '/me':
                    reply(manager.getMe(chat_id))
                elif command == 'alethea':
                    bot.sendSticker(chat_id, 'CAADBQADxQYAAszG4gK3wUYfyR3TSQI')
                elif command == '/howmany':
                    reply(printGrandTally())
                elif command == '/count':
                    if not manager.eventDoesNotExist() and not manager.eventHasEnded():
                        _progress = 0
                        reply('WARNING: You will potentially override existing data if you do not go through with the full procedure. If so, type exit to leave now.')
                        reply(str(question_bank.get(question_order[self._progress])))
                        self.track_reply = True
                    else:
                        reply('No one is counting attendance now. You may wish to do other productive things.')
                else:
                    reply(easter.responseHandler(command))

        # ================================ COMMANDS FOR UNREGISTERED USERS
        # for '/start'
        elif command == '/start':
            reply('Hello there. Please enter \'/start Full Name CG\'\n\nEg: /start Alethea Sim TJ\n')
            reply('For full list of CG abbreviations type in /cg')
        elif command.startswith('/start'):
            cg_regex_pattern = generateCgRegexPattern()
            regex_pattern = '\/start\s+([a-zA-Z ]+)\s+' + str(cg_regex_pattern)
            print(cg_regex_pattern)
            matches = re.match(regex_pattern, command, re.IGNORECASE)
            if matches is None:
                reply('Either you did not follow the appropriate format: \'/start Your Name CG\' or you did not use the correct CG code. (/cg)')
            else:
                name = matches.group(1).title()
                cg = matches.group(2).lower()

                # map CG to appropriate cluster
                cluster = authorized.getCluster(cg)
                approver_id = authorized.address_book.get(cluster)

                request_message = '%s (%s) from %s, %s wants to register.' % (chat_id, name, cluster, cg)
                logger.info(request_message)
                reply('Hello, %s!' % name)

                # ask rep to approve registration
                request_add(authorized.superadmin, request_message, cg, name, chat_id)
                request_add(approver_id, request_message, cg, name, chat_id)
                reply('Your request was sent to your cluster rep (JC %s) for approval. If you do not hear back within a minute, try again.' % authorized.getClusterFriendlyString(cluster))

        # otherwise it must be trying to talk to ARIADNE!
        else:
            reply('You are not registered. Hit /start or contact Justin (@njyjn) for more information.')
        return

bot = telepot.DelegatorBot(TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, ACGLBOT, timeout=120),
        # pave_event_space()(
        #     per_callback_query_origin(), create_open, HeadmasterManager, timeout=60),
])
bot.message_loop(run_forever="ACGLBOT is listening ...")
