# -*- coding: UTF-8  -*-
#
# Generate filenames
#
# To do:
# TO long descriptions
# Multi obj description
# photoDescr or obj Descr
#
import codecs
from common import Common

#limitations on namelength
#shorten if longer GOODLENGTH cut if longer than MAXLENGTH
GOODLENGTH = 100
MAXLENGTH = 128

def makeFilenames():
	'''Testing PhoBeschreibungM'''
	filenameP=u'deriv-photo_multimedia_ObjIds_stichID_samesame_real.csv'
	headerP, linesP = Common.openFile(filenameP)
	
	oDict = Common.file_to_dict(u'deriv-ObjDaten-trimmed_Ausstellung_sam_eregnis_kuenstler_MulMass.csv')
	
	f = codecs.open(u'deriv-filenames.csv', 'w', 'utf-8') #new csv file
	fbesk = codecs.open(u'deriv-descr_forCommons.log', 'w', 'utf-8') #new csv file for Commons
	flog = codecs.open(u'deriv-filename.log', 'w', 'utf-8') #logfile (for any unmerged rows)
	
	#write headers
	f.write(u'%s|%s|%s|%s|filename\n' % (headerP[0], headerP[1], headerP[9], headerP[10]))
	fbesk.write(u'Final filename becomes: <descr> - <museum> - <filename>.tif \n\n')
	fbesk.write(u'Attempts have been made to keep descriptions under %r characters with a hard limit at %r characters\n\n' %(GOODLENGTH,MAXLENGTH))
	fbesk.write(u'You are free to change the descriptions shown below.\n')
	fbesk.write(u'===phoId|mullId|description===\n')
	
	
	skiplog = []
	noHopelog = []
	dcounter = 0 #number of files skipped where something could be done
	hcounter = 0 #number of files skipped where nothing can be done
	cOut     = 0 #number of outputs
	uTester  = [] # to test uniquenes of filenames
	first = True
	for l in linesP:
		if first:
			first=False
			continue
		col = l.split('|')
		phoId = col[0]
		mullId = col[1]
		objIds = col[2].split(';')
		museum = museumConv2(col[5])
		phoBes, log = phoBesConv(col[3])
		origPath = col[9]
		origFName = col[10]
		same_same = col[13]
		if len(phoBes) == 0: #skip empty ones
			if len(col[2]) == 0:
				noHopelog.append('No-objects-No-photoDescr|%s|%s' % (phoId,mullId))
				hcounter = hcounter+1
				continue #nothing to do
			elif len(objIds) == 1:
				phoBes = getDescFromObj(oDict[objIds[0]])
				if len(phoBes) == 0: #might still be empty
					skiplog.append('No-objectDescr-No-photoDescr|%s|%s' % (phoId,mullId))
					dcounter = dcounter+1
					continue
			else:
				skiplog.append('Many-objects-No-photoDescr|%s|%s' % (phoId,mullId))
				dcounter = dcounter+1
				continue #haven't decided yet
		if len(log) > 0:
			flog.write(u'%s\n' %log.strip('\t'))
		if cOut%250==0:
			fbesk.write(u'====%r-%r====\n' %(cOut,cOut+250))
		cOut = cOut+1
		fbesk.write(u'*%s|%s|%s\n' %(phoId, mullId, phoBes))
		#newfName = u'%s - %s - %s.tif' %(phoBes, museum, origFName)
		ending = phoId
		if len(same_same)>0: ending = u'%s (%s)' %(ending, mullId)
		newfName = u'%s - %s - %s.tif' %(phoBes, museum, ending)
		f.write(u'%s|%s|%s|%s|%s\n' % (phoId, mullId, origPath, origFName, newfName))
		uTester.append(newfName)
	print u'Skipped: %r files out of which %r may have hope.' %(dcounter+hcounter,dcounter)
	if len(uTester) != len(set(uTester)):
		print u'Filenames are not unique!!!!: %r were duplicate' %(len(uTester) - len(set(uTester)))
	flog.write(u'----Skipped (hopeless)----\n')
	for l in noHopelog:
		flog.write(u'%s\n' %l)
	flog.write(u'----Skipped (some hope?)----\n')
	for l in skiplog:
		flog.write(u'%s\n' %l)
	flog.close()
	f.close()
	#
def museumConv(text):
	'''converts plaintext museumname to std. abbrevition'''
	if text == u'Hallwylska museet':
		return u'HWY'
	elif text == u'Livrustkammaren':
		return u'LRK'
	elif text == u'Skoklosters slott':
		return u'SKO'
	else:
		return u'LSH'
def museumConv2(text):
	'''converts plaintext museumname to std. abbrevition'''
	if text == u'':
		return u'LSH'
	else:
		return text
def phoBesConv(text):
	'''strips out inv. numbers etc'''
	#strings preceding inventory no's
	badStrings = [u'LRK.', u'LRK ', u'LRk ', u'HWY ', u'ENR ', u'Enr ', u'enr ', u'inv. nr. ', u'SKO ', u'LXIV:', u'unr ', u'xlii:']
	badchar = u'-., ' #kanske även "
	log=''
	runAgain = True
	while(runAgain):
		runAgain = False
		for b in badStrings:
			if b in text:
				runAgain = True
				pos = text.find(b)
				#find end - must be a better way
				sep = ','
				pos2 = text.find(',',pos)
				posOch = text.find('och',pos)
				posAmp = text.find('&',pos)
				if posOch > 0 and (posOch < pos2 or pos2<0):
					sep = ' och'
					pos2 = posOch
				if posAmp > 0 and (posAmp < pos2 or pos2<0):
					sep = ' &'
					pos2 = posAmp
				#end of ugly
				if pos2 > 0:
					log = u'%s%s\t' %(log, text[pos:pos2])
					text = u'%s%s %s' %(text[:pos].strip(badchar),sep,text[pos2+len(sep):].strip(badchar))
				else:
					log = u'%s%s\t' %(log, text[pos:])
					text = text[:pos]
	text = text.strip(badchar)
	if len(text) == 0:
		return '', log
	elif len(text.strip('0123456789,.- ')) == 0: #if only numbers (left)
		log = u'%s%s\t' %(log, text)
		return '', log
	else:
		text = cleanName(text)
		return shortenNames(text).capitalize(), log
#
def getDescFromObj(obj):
	'''finds a suitable description based on obj'''
	badStrings = [u'<!>', u'(?)', u'Biografi och genealogi', u'Geografi', u'Konst- och kulturhistoria', u'Samhälls- & rättsvetenskap', u'Genrebild', u'Historiebild', u'Djurbild', u'Landskapsbild']
	badchar = u'-., ' #kanske även " 
	
	#There are two relevant fields. Which to use depends partly on the collection to which the obj belongs
	orig = obj[u'ObjTitelOriginalS']
	kort = obj[u'ObjTitelWeitereM']
	
	#remove badStrings from both
	for b in badStrings:
		if b in orig:
			pos = orig.find(b)
			orig = orig[:pos]+orig[pos+len(b):]
		if b in kort:
			pos = kort.find(b)
			kort = kort[:pos]+kort[pos+len(b):]
	#strip badchar
	orig = orig.strip(badchar)
	kort = kort.strip(badchar)
	#if only numbers (left)
	if len(orig.strip('0123456789,.- ')) == 0:
		orig = ''
	if len(kort.strip('0123456789,.- ')) == 0:
		kort = ''
	
	#decision time
	descr = ''
	if orig.lower() in kort.lower():
		descr = kort
	elif kort.lower() in orig.lower():
		descr = orig
	elif len(kort) == 0 and len(orig) == 0:
		descr = ''
	else:
		samling = obj[u'AufAufgabeS']
		if samling in [u'Livrustkammaren', u'Skoklosters slott']:
			descr = kort
		elif samling in [u'Hallwylska museet']:
			descr = '%s: %s' %(orig, kort)
		else: #u'LRK dubletter', u'Skoklosters slotts boksamling'
			descr = orig
	descr = cleanName(descr)
	return shortenNames(descr).capitalize()
#
def cleanName(text):
	'''removes forbidden characters - extend as more are identified'''
	badChar = [u'\\'] #maybe also / ? ' 
	badWhite = [u'	'] #maybe also &nbsp; character
	for b in badChar:
		text = text.replace(b, '-')
	for b in badWhite:
		text = text.replace(b, ' ')
	#replace double space by single space
	text = text.replace('  ', ' ')
	return text
def shortenNames(text):
	'''if a string is larger than MAXLENGTH then this tries to find a sensibel shortening'''
	badchar = u'-., ' #kanske även " 
	#is ok?
	if len(text) < GOODLENGTH:
		return text
	#attempt fixing
	#remove trailing brackets
	if text.endswith(')'):
		pos = text.rfind('(')
		if pos > 0:
			return shortenNames(text[:pos].strip(badchar))
	#split string at certain character
	pos = text.rfind('.')
	if pos < 0:
		pos = text.rfind(' - ')
		if pos < 0:
			pos = text.rfind(';')
			if pos < 0:
				pos = text.rfind(',')
				if pos < 0:
					#try something else
					if len(text)>MAXLENGTH:
						text = u'%s...' %text[:MAXLENGTH-3]
					return text
	return shortenNames(text[:pos].strip(badchar))
#
