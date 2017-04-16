from manager import cgs, tally, events
from tools import rreplace
import authorized

question_bank = {
	'total': 'How many youths came today, total?',
	'l': 'How many servers including yourself?',
	'f':'How many (F)reshies?',
    'rd': 'How many (R)e-(D)edications?',
	'nb':'How many (N)ew (B)elievers?',
	'nc':'How many (N)ew (C)omers?',
	'v':'How many (V)isitors?',
	'ir': 'How many (IR)regulars?',
}

question_order = ['total', 'l', 'f', 'ir', 'rd', 'nb', 'nc', 'v',]

question_limit = len(question_order)

def getEventName():
    eventDoc = events.find_one( {} )
    return str(eventDoc.get('name', 'AttendanceBot')) if eventDoc != None else 'AttendanceBot'

# produces a string for individual cg records, format:
# East (TJ): 30+3 (5F, 1NC, 2NB, 6IR)
def getCGFinalString(cg):
    cluster = authorized.getCluster(cg.lower())
    clusterFS = authorized.getClusterFriendlyString(cluster)
    cgDoc = cgs.find_one( { 'name': cg.lower() } )
    if cgDoc == None:
        return '%s (%s):' % (clusterFS.title(), cg.upper())
    return getFinalString(cgDoc, cg)

def getFinalString(cgDoc, cg=None, clusterFS=None):
    total = leaders = string = ''
    # Blank cursors imply the CG has yet to submit attendance, so we skip them to show blank tally
    if cgDoc != None:
        total = str(cgDoc.get('total', ''))
        leaders = str(cgDoc.get('l', ''))
        freshies = str(cgDoc.get('f', ''))
        ncs = str(cgDoc.get('nc', ''))
        nbs = str(cgDoc.get('nb', ''))
        irs = str(cgDoc.get('ir', ''))
        visitors = str(cgDoc.get('v', ''))
        # Add suffixes only if count is non-zero
        freshies = '' if freshies in ('','0') else freshies+'F, '
        ncs = '' if ncs in ('','0') else ncs+'NC, '
        nbs = '' if nbs in ('','0') else nbs+'NB 🎉, '
        irs = '' if irs in ('','0') else irs+'IR, '
        visitors = '' if visitors in ('','0') else visitors+'V, '
        string = freshies + irs + ncs + visitors + nbs
        # Rid last comma
        string = rreplace(string, ', ', '', 1)
    # Blank clusterFS means the CG is querying this method for its tally string.
    if clusterFS == None:
        clusterFS = authorized.getClusterFriendlyString(cgDoc.get('cluster', 'Error'))
    else:
        clusterFS = authorized.getClusterFriendlyString(clusterFS)
    # Empty CGs mean that the cluster is looking for its total attendance.
    if cg != None:
        cluster_and_cg = '%s (%s)' % (clusterFS.title(), cg.upper())
    else:
        cluster_and_cg = '%s TOTAL' % clusterFS.upper()
    if cgDoc == None:
        return '%s:' % cluster_and_cg
    if string == '':
        return '%s: %s+%s' % (cluster_and_cg,  total, leaders)
    return '%s: %s+%s (%s)' % (cluster_and_cg, total, leaders, string)

def printGrandTally():
    eventName = getEventName()
    
    northTotal = getFinalString(tally.find_one( {'cluster': 'jcn'} ), None, 'jcn')
    ajyj = getCGFinalString('aj/yj')
    sr = getCGFinalString('sr')
    nyej = getCGFinalString('ny/ej')
    rja = getCGFinalString('rja')
    rjbsji = getCGFinalString('rjb/sji')
    rjc = getCGFinalString('rjc')
    ij = getCGFinalString('ij')
    north = '%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n' % (ajyj, sr, nyej, rja, rjbsji, rjc, ij, northTotal)

    southTotal = getFinalString(tally.find_one( {'cluster': 'jcs'} ), None, 'jcs')
    #cjsota = getCGFinalString('cj/sota')
    cja = getCGFinalString('cj a')
    cjb = getCGFinalString('cj b')
    cjc = getCGFinalString('cj c')
    saa = getCGFinalString('sa a')
    sab = getCGFinalString('sa b')
    south = '%s\n%s\n%s\n%s\n%s\n%s\n' % (cja, cjb, cjc, saa, sab, southTotal)

    eastTotal = getFinalString(tally.find_one( {'cluster': 'jce'} ), None, 'jce')
    mj = getCGFinalString('mj')
    vja = getCGFinalString('vja')
    vjb = getCGFinalString('vjb')
    tpja = getCGFinalString('tpja')
    tpjb = getCGFinalString('tpjb')
    tj = getCGFinalString('tj')
    dmh = getCGFinalString('dmh')
    east = '%s\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n' % (mj, vja, vjb, tpja, tpjb, tj, dmh, eastTotal)

    westUnitedTotal = getFinalString(tally.find_one( {'cluster': 'jcwu'} ), None, 'jcwul')
    pjjj = getCGFinalString('pj/jj')
    hc = getCGFinalString('hc')
    nj = getCGFinalString('nj')
    westu = '%s\n%s\n%s\n%s\n' % (pjjj, hc, nj, westUnitedTotal)

    westAcibTotal = getFinalString(tally.find_one( {'cluster': 'jcwa'} ), None, 'jcwal')
    ac = getCGFinalString('ac')
    ibcg = getCGFinalString('ibcg')
    westa = '%s\n%s\n%s\n' % (ac, ibcg, westAcibTotal)

    jcTotal = getFinalString(tally.find_one( {'cluster': 'all'} ), None, 'all') 

    return '%s\n\n%s\n%s\n%s\n%s\n%s\n%s' % (eventName, north, south, east, westu, westa, jcTotal)