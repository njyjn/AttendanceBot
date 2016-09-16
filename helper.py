#!/usr/bin/python

"""
    stores command documentation for /help queries
    
    ##### do not terminate the description, examples and parameters dictionaries with newlines ######
"""

# command description list (do not terminate with newlines)
layman = {
    'help': 'Usage: /help\n--> Return this menu.',
    'me': 'Usage: /me\n--> Retrieve your ID.',
    'points': 'Usage: /points\n--> Check house score.',
    'time': 'Usage: /time\n--> See the time.',
    'key': 'Usage: /key\n--> Obtain key (withiNUS)',
    'answer': 'Usage: /answer\n--> Obtain answer (withiNUS)'
}

# admin description list (do not terminate with newlines)
description = {
    'yell': 'Usage: /yell message\n--> Sends a message to everyone on the mailing list (use /who to see who\'s listening to this bot)',
    'whisper': 'Usage: /whisper group message\n--> Sends a message to everyone in the specified group (use /who to see who\'s listening to this bot). You can only send to 1 group at a time.',
    'time': 'Usage: /time\n--> Gets the bot server\' current time. Use this to coordinate efforts and deadlines\n',
    'log': 'Usage: /log\n--> Gets you the 5 most recent announcements. The most recent announcement is at the bottom.',
    'vlog': 'Usage: /vlog n\n--> Gets you the n most recent announcements. The most recent announcement is at the bottom.',
    'who': 'Usage: /who\n--> Lists all the people listening to this bot and who belongs to which groups',
}

# example usage (do not terminate with newlines)
examples = {
    'yell': 'e.g. /yell Hi everyone please come get your food!',
    'whisper': 'e.g. /whisper cvogls Hi COGLs and VOGLs, your shirts are ready!\n\ne.g. /whisper ogls Hi all OGLs, please take note of the warm weather today!',
    'time': 'e.g. /time',
    'vlog': 'e.g. /vlog 10',
    'log': 'e.g. /log',
    'who': 'e.g. /who',
}

# argument list
parameterDict = {
}

# relevant parameter list
relevantParameters = {
}

def getHelp(command):
    reply = ''

    # check if basic doc exists
    if command in description:
        reply += description.get(command) + '\n\n'

        # append the example if there is one
        if command in examples:
            reply += examples.get(command) + '\n\n'

        # append parameters if there are any
        if command in relevantParameters:
            reply += 'Parameters\n'
            for param in relevantParameters.get(command):
                reply += '%s\n' % (parameterDict.get(param))
    else:
        return 'Command not found.'

    return reply

def getNaiveHelp():
    reply = 'Commands available:\n'
    for command in list(description.keys()):
        reply += command + '\n'
    reply += '\nUse \'/help command\' for more info'
    return reply
    
