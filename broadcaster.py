import manager

def yell(bot, audience, message, requester):
    
    recipients = manager.prepareYell(audience)
    for recipient in recipients:
        bot.sendMessage(recipient['chatID'], message)
