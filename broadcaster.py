import manager, re
from voglogger import logger
from authorized import getCgs
from tools import generateClusterRegexPattern, generateCgRegexPattern

def yell(bot, target_and_message, requester):		
	cg_regex_pattern = generateCgRegexPattern() + '\s+(.+)'
	cg_matches = re.match(cg_regex_pattern, target_and_message)
	# if cluster or 'all'
	if cg_matches is None:
		cluster_regex_pattern = generateClusterRegexPattern() + '\s+(.+)'
		cluster_matches = re.match(cluster_regex_pattern, target_and_message)
		# could be 'all'
		if cluster_matches is None:
			if target_and_message.startswith('all'):
				recipients = manager.prepareYell('all')
				message = target_and_message.replace('all ', '', 1)
			# invalid params
			else:
				return('ADMIN: Please follow the appropriate format: \'/yell target Your message.\'')
		# is cluster
		else:
			audience = cluster_matches.group(1)
			message = cluster_matches.group(2)
			recipients = manager.prepareYell(getCgs(audience))
	# is cg
	else:
		audience = cg_matches.group(1)
		message = cg_matches.group(2)
		audience = [audience]
		recipients = manager.prepareYell(audience)
	
	if recipients == None:
		return('ADMIN: Target invalid.')
	send_receipt = ''
	# # add sender to message
	# message = manager.getName(requester) + ': ' + message
	for recipient in recipients:
		try:
			bot.sendMessage(recipient['chatID'], message)
			send_receipt += recipient['name']+', '
		except:
			pass
	return 'Yelled \'%s\' to %s.' % (message, send_receipt)

def dm(bot, target_and_message, requester):
	regex_pattern = '([0-9]+)\s+(.+)'
	matches = re.match(regex_pattern, target_and_message)
	if matches is None:
		return('ADMIN: Please follow the appropriate format: \'/dm chat_id Your message.\'')
	target_id = matches.group(1)
	message = matches.group(2)
	message = manager.getName(requester) + ': ' + message
	out_message = message + '\n\n[This message was sent as a DM by an admin.]'
	bot.sendMessage(target_id, out_message)
	logger.info('%s sent to %s from %s.' % (message, target_id, requester))
	return '\'%s\' sent to %s (%s).' % (message, manager.getName(target_id), target_id)