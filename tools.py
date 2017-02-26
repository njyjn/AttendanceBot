from authorized import cg_list

def generateCgRegexPattern():
	regex_pattern = '(' 
    # extract all given cgs in authorized into a regex id pattern
	for cg in cg_list:
		regex_pattern += cg + '|'
	regex_pattern = rreplace(regex_pattern, '|', ')', 1)
	return regex_pattern

# Replaces substrings within text, from the back
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)
