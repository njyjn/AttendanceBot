#!/usr/bin/python

import re
"""
    user management for ACGLBOT
"""
superadmin = 87244565

# dictionary for Telegram chat IDs
address_book = {
    # admin (approvals)
    'Justin'    : 87244565,     # oweek games
    'Justin2'   : 175212803,
    'jce'       : 62199558,     # choy
    'jcs'       : 46683864,     # sherry
    'jcn'       : 41625478,     # ernest
    'jcn2'      : 62186950,     # janie
    'Test-Group': 0,
}
rev_book = {v: k for k, v in address_book.items()}

# user groups
global groups
groups = {
    'admins'    : ['Justin', 'jce', 'jcs', 'jcn', 'jcn2'],
}

# cgs
#cgs = ['MJ', 'VJA', 'VJB', 'TPJA', 'TPJB', 'TJ', 'DMH']
#cg_list = ['mj','vja','vjb','tpja','tpjb','tj','dmh']
#cluster_list = ['jce', 'jcwu', 'jcwac', 'jcn', 'jcs']

cg_cluster_dictionary = {
    'jce': ['mj','vja','vjb','tpja','tpjb','tj','dmh'],
    'jcs': ['cj/sota', 'sa a', 'sa b'],
    'jcn': ['aj/yj', 'sr', 'ny/ej', 'rja', 'rjb/sji', 'rjc', 'ij'],
}
cluster_list = cg_cluster_dictionary.keys()
cg_list = [item for sublist in [v for k, v in cg_cluster_dictionary.items()] for item in sublist]

cluster_fs_dictionary = {
    'jce': 'East',
    'jcs': 'South',
    'jcwu': 'West',
    'jcwul': 'West United',
    'jcwa': 'West',
    'jcwal': 'West ACIB',
    'jcn': 'North',
}

# """
# returns a list of chat IDs of all listening to yells
# """
# def getMailingList():
#     return list(set(getGroups(['cvogls', 'fopcomm', 'admins', 'safety', 'ogls', 'oweek'])))

# """
#     returns a list of chat IDs from a list of groups
# """
# def getGroups(groupList):
#     lists = [getIDs(groups.get(group)) for group in groupList if group in groups]
#     return [item for sublist in lists for item in sublist]

""" 
    verifies if chat ID is superadmin
"""
def isSuperadmin(chat_id):
    return chat_id == superadmin

"""
    verifies if chat ID is admin
"""
def isAdmin(chat_id):
    if chat_id in rev_book:
        return True
    return False

"""
    verifies if chat ID is registered
"""
def isRegistered(check_id):
    return manager.exists(check_id) 


"""
    get the IDs of a list of people's names
"""
def getIDs(people):
    return [address_book.get(person) for person in people if person in address_book]

"""
    map a chat ID to a name if possible
"""
def whoIs(target_id):
    if target_id in rev_book:
        return rev_book.get(target_id)
    else:
        return target_id

"""
    return the cluster that the cg belongs to
"""
def getCluster(cg):
    return ''.join([k for k, v in cg_cluster_dictionary.items() if cg in v])

def getClusterFriendlyString(cluster):
    return ''.join(cluster_fs_dictionary.get(cluster))

# """
#     enumerates all names inside address_book
#     for /who command
# """
# def enumerateListeners():
#     reply = 'The following people are listening to yells:\n'
#     i = 1

#     # get a list of yell listeners
#     for listening_id in getMailingList():
#         reply += '%d. %-16s' % (i, whoIs(listening_id))
#         i += 1
#         if (i+1) % 2 == 0:
#             reply += '\n'

#     # get group lists
#     reply += '\n-------- Group Lists --------\n'
#     for group in ['cvogls', 'ogls', 'oweek', 'fopcomm', 'safety', 'cogls', 'vogls', 'admins']:
#         reply += 'Group \'%s\'\n' % group

#         # the groups dictionary is maintained in the authorized module
#         # we build the reply using the group key-value in the groups dictionary
#         # only build up to second last element then append last element to get rid of trailing comma
#         for group_member in groups.get(group)[:-1]:
#             reply += '%s, ' % group_member
#         reply += '%s' % groups.get(group)[-1] # append last member
#         reply += '\n\n'

#     return reply

def groupIsValid(group_list):
    for group in group_list:
        if group not in groups:
            return False
    return True

import manager
