from authorized import cg_list

# extract all given cgs in authorized into a regex id pattern
def generateCgRegexPattern():
	regex_pattern = '(' 
	for cg in cg_list:
		regex_pattern += cg + '|'
	regex_pattern = rreplace(regex_pattern, '|', ')', 1)
	return regex_pattern

# Replaces substrings within text, from the back
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def getTime():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S, %d %B %Y ')

def groupArg2List(groupList):
    if '+' not in groupList:
        return [groupList]
    else:
        return re.split('\s*+\s*', groupList)