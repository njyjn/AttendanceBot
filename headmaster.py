from manager import cgs, tally
from tools import rreplace
import authorized

question_bank = {
	'total': 'How many youths came today, total?',
	'l': 'How many servers including yourself?',
	'f':'How many (F)reshies?',
	'nb':'How many (N)ew (B)elievers?',
	'nc':'How many (N)ew (C)omers?',
	'v':'How many (V)isitors?',
	'ir': 'How many (IR)regulars?',
}

question_order = ['total', 'l', 'f', 'ir', 'nb', 'nc', 'v',]

question_limit = len(question_order)

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
    if cgDoc != None:
        clusterFS = authorized.getClusterFriendlyString(cgDoc.get('cluster', 'Error'))
        total = str(cgDoc.get('total', 0))
        leaders = str(cgDoc.get('l', 0))
        freshies = str(cgDoc.get('f', 0))+'F, ' if not cgDoc['f'] in ('0',0) else ''
        ncs = str(cgDoc.get('nc', 0))+'NC, ' if not cgDoc['nc'] in ('0',0) else ''
        nbs = str(cgDoc.get('nb', 0))+'NB, ' if not cgDoc['nb'] in ('0',0) else ''
        irs = str(cgDoc.get('ir', 0))+'IR, ' if not cgDoc['ir'] in ('0',0) else ''
        visitors = str(cgDoc.get('v', 0))+'V, ' if not cgDoc['v'] in ('0',0) else ''
        string = freshies + irs + ncs + visitors + nbs
        string = rreplace(string, ', ', '', 1)
    else:
        clusterFS = authorized.getClusterFriendlyString(clusterFS)
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

    return '%s\n%s\n%s' % (north, south, east)