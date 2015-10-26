#!/usr/bin/python
# -*- coding: UTF-8
#
# Analysing cleaned csv files to find potential errors which must
# be dealt with before crunching
#
#
# Includes the following old files:
# * py-Ausstellung.py (partially)
# * py-multimedia.py
# * py-photo.py (partially)
#
#
'''
What to do afterwards:
analys-photo:
    1) Ensure no duplicates
    2) Make sure only acceptable license and sources are included
analys-multimedia:
    1) Clean up any BadNames (filetype in filename)
    2) TODO: For each MulPhoId in duplicates
       remove the second occurence from clean_csv
       DONE: in makePhoto_multi
analys-ausstellung:
    1) Fix badly formated years
'''
from py_MakeInfo import MakeInfo  # To get access to handled variables
import codecs
import os
from common import Common
import helpers

CSV_DIR_CLEAN = u'clean_csv'
LOG_FILE = u'¤csv_analys.log'


def run(in_path=CSV_DIR_CLEAN, log_file=LOG_FILE):
    # stop if in_path doesn't exist
    if not os.path.isdir(in_path):
        print u'%s is not a valid path' % in_path
        exit(0)
    # create out_path if it doesn't exist
    if type(log_file) == str:
        log_file = unicode(log_file)

    # create log file
    f = codecs.open(log_file, 'w', 'utf-8')

    # Load known variables
    A = MakeInfo()
    A.makeAbbrevLicense()
    A.makeAbbrevSource()

    # start analysis
    analysePhoto(A, f, file_in=os.path.join(in_path, u'%s.csv' % 'photo'))
    analyseMulti(f, file_in=os.path.join(in_path, u'%s.csv' % 'multimedia'))
    analyseYear(f, file_in=os.path.join(in_path, u'%s.csv' % 'ausstellung'))
    analysePhotoAll(f, file_in=os.path.join(in_path, u'%s.csv' % 'photoAll'))

    print u'Created %s' % log_file


def analyseYear(f, file_in):
    '''
    Exhibitanalyser:
    verifies that the year can be interpreted
    @todo: become stricter. Disallow space as year separator
    '''
    header, lines = Common.openFile(file_in)
    data = []
    exhibits = []
    # AobId
    # AusId
    # AusTitelS
    # AusOrtS
    # AusJahrS
    # AusDatumVonD
    # AusDatumBisD
    # AobObjId
    # AufAufgabeS
    for l in lines:
        if len(l) == 0:
            continue
        col = l.split('|')
        if col[2].strip() == '':  # ignore exhibits wihtout names
            continue
        ExhibId = col[1]  # AusId
        if ExhibId in exhibits:
            continue
        exhibits.append(ExhibId)
        year = col[4].strip()  # AusJahrS
        lyear = len(year)
        yfrom = col[5].replace(u' 00:00:00', u'').strip()  # AusDatumVonD
        lyfrom = len(yfrom)
        ytil = col[6].replace(u' 00:00:00', u'').strip()  # AusDatumBisD
        lytil = len(ytil)
        lout = u'%s|%s|%s|%s' % (ExhibId, year, yfrom, ytil)
        # identify weird year formatting
        if lyear != 0:
            if not (lyear == 4 or lyear == 9 or lyear == 7):
                # if not YYYY or YYYY-YYYY or YYYY-YY
                data.append(u'error y1|%s' % lout)
            elif lyear == 9 and (year[4:5] != '-' and year[4:5] != ' '):
                # if not YYYY-YYYY or YYYY YYYY
                data.append(u'error y1|%s' % lout)  # y5
            elif lyear == 7 and (year[4:5] != '-' and year[4:5] != ' '):
                # if not YYYY-YY or YYYY YY
                data.append(u'error y1|%s' % lout)  # y6
            elif (lyear == 9) and (lyfrom != 0 or lytil != 0):
                if lyfrom != 0 and int(year[:4]) != int(yfrom[:4]):
                    data.append(u'error y3|%s' % lout)
                elif lytil != 0 and int(year[-4:]) != int(ytil[:4]):
                    data.append(u'error y3|%s' % lout)
            # elif (lyear == 4) and (lyfrom != 0):
            #    if int(year) != int(yfrom[:4]):
            #        data.append(u'error y2|%s' % lout)
                # elif lytil != 0 and int(ytil[:4]) != int(year):
                #    data.append(u'error y7|%s' % lout)
    # loop done
    f.write(u'\n\n<!--From: %s -->\n' % file_in)
    f.write(u'===year problems===\n')
    f.write(u'y1:\t Could not match JahrS to any YYYY or YYYY-YYYY or YYYY-YY\n')
    # f.write(u'y2:\t JahrS is not the same as starting year in Von-Bis range')
    # f.write(u'- unless amended Von will be used\n')
    f.write(u'y3:\t JahrS is span which doesn\'t match in Von-Bis range')
    f.write(u'- please amend as appropriate\n')
    f.write(u'#error\tAusId\tAusJahrS\tAusDatumVonD\tAusDatumBisD\n')
    for d in data:
        splits = d.split('|')
        txt = ''
        for s in splits:
            txt = u'%s\t%s' % (txt, s)
        f.write(u'%s\n' % txt[7:])
# done


def analysePhoto(A, f, file_in):
    '''
    Verifies that all licenses and sources can be parsed correctly and
    that there are no duplicates
    '''
    header, lines = Common.openFile(file_in)
    licenses = []
    sources = []
    mulls = []
    phids = {}
    nodupes = True
    dupePhoid = {}
    # PhoId
    # PhoObjId
    # PhoBeschreibungM
    # PhoAufnahmeortS
    # PhoSwdS
    # MulId
    # AdrVorNameS
    # AdrNameS
    # PhoSystematikS
    f.write(u'<!--From: %s -->\n' % file_in)
    for l in lines:
        if len(l) == 0:
            continue
        col = l.split('|')
        lic = col[3]  # PhoAufnahmeortS
        source = col[4]  # PhoSwdS
        phid = col[0]  # PhoId
        if lic not in licenses:
            licenses.append(lic)
        if source not in sources:
            sources.append(source)
        mull = col[5]  # MulId
        if (mull in mulls) and nodupes:
            f.write(u'there are dupes in MullId\n')
            nodupes = False
        else:
            mulls.append(mull)
        # for comparing content
        if phid in phids.keys():
            # Duplicate photoids...
            tt = '|'.join(col[1:4]+col[6:])
            if tt != phids[phid]:
                # with different content
                dupePhoid[tt] = (phid, phids[phid])
        else:
            phids[phid] = '|'.join(col[1:4]+col[6:])
    # loop done
    # find incompatible licenses
    for s in sources:
        if s not in A.source.keys():
            f.write(u'Found an incompatible source: %s\n' % s)
    # find incompatible sources
    for l in licenses:
        if l not in A.lic.keys():
            f.write(u'Found an incompatible license: %s\n' % l)
    if nodupes:
        f.write(u'there are NO dupes in MullId =)\n')
    if len(dupePhoid) != 0:
        f.write(u'---Duplicate phoIds with different info---\n')
        for k, v in dupePhoid.iteritems():
            f.write(u'%s: %s <> %s\n' % (v[0], k, v[1]))
# done


def analyseMulti(f, file_in):
    '''
    Identifies dupes
    identifies images with filetype in the filename
    '''
    header, lines = Common.openFile(file_in)
    ids = []
    mults = []
    bad = []
    difftest = {}
    sameCount = 0
    diffCount = 0
    ccount = 0
    ndiffCount = 0
    ndict = {}
    # MulId
    # MulPhoId
    # MulPfadS
    # MulDateiS
    # MulExtentS
    f.write(u'\n\n<!--From: %s -->\n' % file_in)
    for l in lines:
        if len(l) == 0:
            continue
        col = l.split('|')
        idd = col[1]  # MulPhoId
        fullname = ''.join([col[2], col[3], col[4]])
        # test if each filename has only one photoid
        if fullname in ndict.keys():
            if idd != ndict[fullname]:
                ndiffCount = ndiffCount+1
                # print idd, ndict[fullname]
        else:
            ndict[fullname] = idd
        # testing mullId/phoId duplication
        if idd in ids:
            ccount = ccount+1
            mults.append(idd)
            tt = '|'.join([col[2], col[3], col[4]])
            if tt != difftest[idd]:
                diffCount = diffCount+1
                # print u'>%s\n<%s\n' %(tt, difftest[idd])
            else:
                sameCount = sameCount+1
        else:
            ids.append(idd)
            difftest[idd] = '|'.join([col[2], col[3], col[4]])
        name = col[3]  # MulDateiS
        if name[-4:-3] == '.':
            # If filetype in MulDateiS
            bad.append(name)
    # loop done
    mm = {}
    tot = 0
    for m in mults:
        if m in mm.keys():
            mm[m] = mm[m]+1
            tot = tot+1
        else:
            mm[m] = 2
            tot = tot+2
    if len(mm) > 0:
        f.write(u'===duplicates===\n')
        f.write(u'#Total: %r\n' % tot)
        f.write(u'#MulPhoId|antal\n')
        sortMults = Common.sortedDict(mm)
        for s in sortMults:
            f.write(u'%s|%r\n' % (s[0], s[1]))
    if len(bad) > 0:
        f.write(u'===BadNames===\n')
        for b in bad:
            f.write(u'%s\n' % b)
    if len(bad) == 0 and len(mm) == 0:
        f.write(u'there are no problems with multimedia file =)')
# done


def analysePhotoAll(f, file_in):
    """
    Check that all PhoSystematikS are commonsfiles and each is unique
    """
    header, lines = Common.openFile(file_in)
    badUrls = []
    dupes = []
    sources = {}

    for l in lines:
        if len(l) == 0:
            continue
        col = l.split('|')
        source = col[8].strip()  # PhoSystematikS
        phoId = col[0]  # PhoId
        mulId = col[5]  # MulId
        phoMul = u'%s:%s' % (phoId, mulId)
        if len(source) > 0:
            if '%' in source:
                source = helpers.urldecodeUTF8(source)
            internal = helpers.external2internalLink(source,
                                                     project='wikimedia')
            if not internal.startswith('[[:commons:File:'):
                badUrls.append((phoMul, source))
            else:
                internal = internal[len('[[:commons:File:'):-len(']]')]
                if internal in sources.keys():
                    dupes.append((phoMul, sources[internal],
                                  internal.replace(' ', '_')))
                sources[internal] = phoMul

    f.write(u'\n\n<!--From: %s -->\n' % file_in)
    if len(badUrls) > 0:
        f.write(u'===BadUrls===\n')
        for b in badUrls:
            f.write(u'%s: %s\n' % b)
    if len(dupes) > 0:
        f.write(u'===DuplicateUrls===\n')
        f.write(u'phoId:mulId|phoId:mulId|Filename\n')
        for b in dupes:
            f.write(u'%s|%s|%s\n' % b)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_analyseCSVData.py in_path out_path\n' \
        + u'\tin_path (optional): the relative pathname to the ' \
        + u'cleaned csv directory. Defaults to "%s"\n' % CSV_DIR_CLEAN \
        + u'\tlog_file (optional): the log to which the analysis is ' \
        + u'written. Defaults to "%s"' % LOG_FILE
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 2:
        argv[0] = argv[0].decode(sys.getfilesystemencoding())  # str to unicode
        argv[1] = argv[1].decode(sys.getfilesystemencoding())  # str to unicode
        run(in_path=argv[0], log_file=argv[1])
    else:
        print usage
# EoF
