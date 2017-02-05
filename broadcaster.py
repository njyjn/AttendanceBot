import manager

def yell(bot, audience, message, requester):
    
    recipients = manager.prepareYell(audience)
    for recipient in recipients:
        try:
        	bot.sendMessage(recipient['chatID'], message)
        except:
        	pass
