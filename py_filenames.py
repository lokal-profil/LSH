#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Generates filenames based on image and object descriptions
# Note that file extentions are added separately
#
#
import codecs
import os
import helpers
from helpers import output

# limitations on namelength
# shorten if longer GOODLENGTH cut if longer than MAXLENGTH
GOODLENGTH = 100
MAXLENGTH = 128
PHOTO_FILE = u'photo_multimedia_etc.csv'
OBJDATEN_FILE = u'objDaten_etc.csv'
CSV_FOLDER = u'data'
LOG_SUBFOLDER = u'logs'
MAPPING_FOLDER = u'mappings'


def run(folder=None, mapping=None, outfolder=None,
        filename_photo=None, filename_obj_daten=None):
    """
    Generates filenames from photo and object descriptions
    :param folder: the folder containing csv files
    :param mapping: the folder containing mapping files
    :param filename_photo: the photo data csv file
    :param filename_obj_daten: the objDaten csv file
    :param outfolder: if provided output is not put in default folder
    :return: None
    """
    # set defaults unless overridden
    folder = folder or CSV_FOLDER
    mapping = mapping or MAPPING_FOLDER
    filename_photo = filename_photo or PHOTO_FILE
    filename_obj_daten = filename_obj_daten or OBJDATEN_FILE
    outfolder = outfolder or folder

    # create target folders if they don't exist
    target_folders = (mapping, os.path.join(outfolder, LOG_SUBFOLDER))
    for t in target_folders:
        if not os.path.isdir(t):
            os.mkdir(t)

    # make descriptions
    photo_file = os.path.join(folder, filename_photo)
    obj_daten_file = os.path.join(folder, filename_obj_daten)
    log_file = os.path.join(outfolder, LOG_SUBFOLDER, u'filenames.log')
    descriptions, photo = makeDescriptions(photo_file, obj_daten_file,
                                           log_file)

    # output Commons
    mapping_file = os.path.join(mapping, u'Filenames.txt')
    commonsOutput(descriptions, mapping_file)

    # make Filenames
    filenames_file = os.path.join(outfolder, u'filenames.csv')
    makeFilenames(descriptions, photo, filenames_file)


def makeDescriptions(photoFile, objDatenFile, logFile):
    """
    Given the photo and objDaten data this uses the two generate descriptions.
    Also returns photo for later use
    :param photoFile: path to photo data file
    :param multiFile: path to multimedia data file
    :param logFile: path to logfile
    :return: dict, dict
    """
    # setup
    flog = codecs.open(logFile, 'w', 'utf-8')  # logfile

    # load input files
    photoHeader = 'PhoId|MulId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|' \
                  'PhoSwdS|AdrVorNameS|AdrNameS|PhoSystematikS|MulPfadS|' \
                  'MulDateiS|MulExtentS|PstId|same_PhoId|same_object'
    photo = helpers.csvFileToDict(photoFile, 'PhoId', photoHeader,
                                  lists=('PhoObjId', ))

    objDatenHeader = 'ObjId|ObjKueId|AufId|AufAufgabeS|ObjTitelOriginalS|' \
                     'ObjTitelWeitereM|ObjInventarNrS|ObjInventarNrSortiertS|' \
                     'ObjReferenzNrS|ObjDatierungS|ObjJahrVonL|ObjJahrBisL|' \
                     'ObjSystematikS|ObjFeld01M|ObjFeld02M|ObjFeld03M|ObjFeld06M|' \
                     'ObjReserve01M|ausId|related|ergId|role:roleCmt:kueId|' \
                     'mulId|massId'
    objDaten = helpers.csvFileToDict(objDatenFile, 'ObjId', objDatenHeader)

    # start process
    skipLog = []  # no photoDescr, no objectDescr
    manyLog = []  # no photoDescr, many objects
    noHopeLog = []  # no photoDescr, no objects
    descriptions = {}
    uniques = set([])  # unique filenames
    for k, v in photo.iteritems():
        phoId = v['PhoId']
        objIds = v['PhoObjId']
        museum = v['PhoSwdS']
        if not museum:
            museum = u'LSH'
        phoBes = getDescFromPhoBes(v['PhoBeschreibungM'])

        if not phoBes:  # try to get description from object
            if len(objIds) == 1 and objIds[0]:
                # exactly one object
                phoBes = getDescFromObj(objDaten[objIds[0]])
                if not phoBes:
                    # failed to make a description from the object
                    skipLog.append(phoId)
            elif len(objIds) > 1:
                # multiple objects
                manyLog.append(phoId)
            else:
                # no objects
                noHopeLog.append(phoId)

        if phoBes:
            filename = u'%s - %s - %s' % (phoBes, museum, phoId)
            descriptions[phoId] = {'descr': phoBes,
                                   'filename': filename}
            uniques.add(filename)

    # check uniqueness
    if len(uniques) != len(descriptions):
        output(u'Descriptions are not unique!!!!: %d were duplicate' %
               (len(uniques) - len(descriptions)))

    # output logs
    if skipLog:
        flog.write('* No-objectDescr and No-photoDescr (phoIds)\n')
        flog.write('%s\n' % '\n'.join(skipLog))
    if manyLog:
        flog.write('* Many objects and No-photoDescr (phoIds)\n')
        flog.write('%s\n' % '\n'.join(manyLog))
    if noHopeLog:
        flog.write('* No-objects and No-photoDescr (phoIds)\n')
        flog.write('%s\n' % '\n'.join(noHopeLog))

    # wrap up
    output(u'Processed %d images out of which %d has some type of problem. '
           u'See log (%s) for more info.' %
           (len(photo), len(photo) - len(descriptions), logFile))
    flog.close()
    return descriptions, photo


def getDescFromPhoBes(text):
    """
    Given a text, filter and chop it to get a suitable description
    :param text: text to process
    :return: str
    """
    # setup
    badStrings = (u'LRK.', u'LRK ', u'LRk ', u'HWY ', u'Hwy S', u'ENR ',
                  u'Enr ', u'enr ', u'inv. nr. ', u'SKO ', u'LXIV:',
                  u'unr ', u'XLII:', u'XXX')
    badchar = u'-., '

    # remove any badstrings/ids
    runAgain = True
    while(runAgain):
        runAgain = False
        for b in badStrings:
            if b in text:
                runAgain = True
                pos = text.find(b)

                # find where to stop chopping
                separators = (',', ' och', ' &', '. ')
                sep = None
                pos2 = -1
                for separator in separators:
                    posEnd = text.find(separator, pos + len(b))
                    if posEnd > 0 and (posEnd < pos2 or pos2 < 0):
                        sep = separator.rstrip()
                        pos2 = posEnd

                # chop
                if pos2 > 0:
                    # See if there is a list of ids
                    while(True):
                        pos3 = text.find(',', pos2 + len(sep))
                        if pos3 > 0:
                            bit = text[pos2 + len(sep):pos3]
                            if not bit.strip('0123456789-,. '):
                                pos2 = pos3 + len(',') - len(sep)
                                continue
                        else:
                            bit = text[pos2 + len(sep):]
                            if not bit.strip('0123456789-,. '):
                                pos2 = pos2 + len(bit)
                        break
                    text = u'%s%s %s' % (text[:pos].strip(badchar),
                                         sep,
                                         text[pos2 + len(sep):].strip(badchar))
                else:
                    text = text[:pos]

    # cleanup text
    text = cleanup_routine(text)
    return text


def getDescFromObj(obj):
    """
    Constructs a suitable description based on an entry in ObjDaten
    :param obj: the objDaten item
    :return: str
    """
    badStrings = [u'<!>', u'(?)', u'Biografi och genealogi', u'Geografi',
                  u'Konst- och kulturhistoria', u'Samhälls- & rättsvetenskap',
                  u'Genrebild', u'Historiebild', u'Djurbild', u'Landskapsbild']
    badchar = u'-., '  # kanske även "

    # There are two relevant fields.
    # Which to use depends partly on the collection to which the obj belongs
    orig = obj[u'ObjTitelOriginalS']
    kort = obj[u'ObjTitelWeitereM']

    # remove badStrings from both
    for b in badStrings:
        orig = orig.replace(b, '')
        kort = kort.replace(b, '')

    # strip badchar
    orig = orig.strip(badchar)
    kort = kort.strip(badchar)

    # if only numbers (left)
    if not orig.strip('0123456789,.- '):
        orig = ''
    if not kort.strip('0123456789,.- '):
        kort = ''

    # decision time, pick longer or rely on collection
    descr = ''
    if orig.lower() in kort.lower():
        descr = kort
    elif kort.lower() in orig.lower():
        descr = orig
    elif not kort and not orig:
        descr = ''
    else:
        samling = obj[u'AufAufgabeS']
        if samling in (u'Livrustkammaren', u'Skoklosters slott'):
            descr = kort
        elif samling in (u'Hallwylska museet'):
            descr = '%s: %s' % (orig, kort)
        else:  # u'LRK dubletter', u'Skoklosters slotts boksamling'
            descr = orig

    # cleanup
    descr = cleanup_routine(descr)
    return descr


def cleanup_routine(text):
    """
    Run the full cleanupp routine on a string.

    :param text: the text to clean
    :return: str
    """
    text = cleanName(text)
    text = cleanString(text)
    if not text.strip('0123456789,.- '):
        # if no relevant info left
        text = ''
    else:
        text = shortenString(text)
        text = touchup(text)

    return text


def cleanName(text):
    """
    Removes unwanted strings from a text string
    :param text: text to test
    :return: str
    """
    # simple strings to remove
    easyBadStrings = (u'Fler inventarienr.', u'Fler inventarienr',
                      u'Flera inventarienr.', u'Flera inventarienr',
                      u'Fler inventareinr', u'(?)')
    for b in easyBadStrings:
        text = text.replace(b, '').strip()
    return text


def cleanString(text):
    """
    Removes characters which are forbidden/undesired in filenames from string
    :param text: the text to test
    :return: str
    """
    # bad characters  - extend as more are identified
    # Note that ":" is complicated as it has several different interpretaions.
    # Currently first replacing possesive case and sentence break then
    # dealing with stand alone :
    # maybe also ? and ' symbol
    badChar = {u'\\': u'-', u'/': u'-', u'|': u'-', u'#': u'-',
               u'[': u'(', u']': u')', u'{': u'(', u'}': u')',
               u':s': u's', u': ': u', ',
               u' ': u' ', u' ': u' ', u'	': u' ',  # unusual whitespace
               u'e´': u'é',
               u'”': u' ', u'"': u' ', u'“': u' '}
    for k, v in badChar.iteritems():
        text = text.replace(k, v)

    # replace any remaining colons
    if u':' in text:
        text = text.replace(u':', u'-')

    # replace double space by single space
    text = text.replace('  ', ' ')
    return text.strip()


def shortenString(text):
    """
    If a string is larger than GOODLENGTH then this tries to
    find a sensibel shortening
    :param text: text to test
    :return: str
    """
    badchar = u'-., '  # kanske även "
    if u'<!>' in text:
        text = text[:text.find(u'<!>')]
    # is ok?
    if len(text) < GOODLENGTH:
        return text
    # attempt fixing
    # remove trailing brackets
    if text.endswith(')'):
        pos = text.rfind('(')
        if pos > 0:
            return shortenString(text[:pos].strip(badchar))
    # split string at certain character
    pos = text.rfind('.')
    if pos < 0:
        pos = text.rfind(' - ')
        if pos < 0:
            pos = text.rfind(';')
            if pos < 0:
                pos = text.rfind(',')
                if pos < 0:
                    # try something else
                    if len(text) > MAXLENGTH:
                        text = u'%s...' % text[:MAXLENGTH - 3]
                    return text
    return shortenString(text[:pos].strip(badchar))


def touchup(text):
    """
    Tweaks a string by removing surrounding bracket or quotes as well as
    some trailing punctuation
    :param text: text to test
    :return: str
    """
    # If string starts and ends with bracket or quotes then remove
    brackets = {u'(': ')', u'[': ']', u'{': '}', u'"': '"'}
    for k, v in brackets.iteritems():
        if text.startswith(k) and text.endswith(v):
            if text[:-1].count(k) == 1:
                # so as to not remove unmatching brackets.
                # slice in check is due to quote-bracket
                text = text[1:-1]

    # Get rid of leading/trailing punctuation
    text = text.strip(' .,;')

    # Make sure first character is upper case
    text = text[:1].upper() + text[1:]
    return text


def commonsOutput(descriptions, mappingFile, allEntries=None):
    """
    Given filedescriptions this outputs it correctly in a Commons export format
    :param descriptions: dict of descriptions with phoId as key
    :param mappingFile: the target file for output
    :param allEntries: optional, a list phoIds giving the order in which
                       to output the entries. This allows for easier
                       diff comparison
    :return: None
    """
    # setup
    fOut = codecs.open(mappingFile, 'w', 'utf-8')
    chunkSize = 250
    chunkStart = u"====%d-%d====\n" \
                 u"{| class=\"wikitable sortable\"\n|-\n! PhoId !! generated " \
                 u"<descr> !! improved <descr>\n"
    rowFormat = u"|-\n| %s || %s || \n"

    # write intro
    fOut.write(
        u'Final filename becomes: <descr> - <museum> - <photoId>.<ext>\n\n'
        u'Attempts have been made to keep descriptions under %d characters '
        u'with a hard limit at %d characters\n\n'
        u'You are free to improve the descriptions by adding an alternativ '
        u'in the last column.\n'
        u'===phoId | description | new description===\n\n'
        u'%s' % (GOODLENGTH, MAXLENGTH, chunkStart % (0, chunkSize)))

    if allEntries is None:
        allEntries = descriptions.keys()
    counter = 0
    for phoId in allEntries:
        # Add regular breaks
        counter += 1
        if counter % chunkSize == 0:
            fOut.write(u'|}\n\n' + chunkStart % (counter, counter + chunkSize))

        # write row
        descr = descriptions[phoId]['descr']
        fOut.write(rowFormat % (phoId, insufficient(descr)))

    # # write outro
    fOut.write(u'|}')
    fOut.close()
    output(u'Created %s' % mappingFile)


def insufficient(text):
    """
    Checks if a string is in blacklist, if so wrap in span setting text
    colour to red, otherwise return unchanged.
    :param text: test string
    :return: str
    """
    badStrings = [u'Detalj', u'Helbild', u'Målning', u'Reprofoto',
                  u'Ritning', u'Bok']
    if text in badStrings:
        text = u'<span style="color:red">%s</span>' % text
    return text


def makeFilenames(descriptions, photo, filenamesFile):
    """
    Given filedescriptions this outputs it correctly as csv for later import
    :param descriptions: dict of descriptions with phoId as key
    :param photo: the photo data
    :param filenamesFile: the target file for output
    :return: None
    """
    # setup
    filenamesHeader = 'PhoId|MulId|MulPfadS|MulDateiS|filename|ext'

    # make a dict to be able to reuse helpers.dictToCsvFile()
    filenames = {}
    for phoId, v in descriptions.iteritems():
        filenames[phoId] = {
            'PhoId': phoId,
            'MulId': photo[phoId]['MulId'],
            'MulPfadS': photo[phoId]['MulPfadS'],
            'MulDateiS': photo[phoId]['MulDateiS'],
            'filename': v['filename'],
            'ext': ''
        }

    # output
    helpers.dictToCsvFile(filenamesFile, filenames, filenamesHeader)
    output(u'Created %s' % filenamesFile)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_filenames.py\n'
    argv = sys.argv[1:]
    if not argv:
        run()
    else:
        print usage
# EoF
