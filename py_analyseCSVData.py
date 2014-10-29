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

CSV_DIR_CLEAN = u'clean_csv'
CSV_DIR_ANALYS = u'analys'


def run(in_path=CSV_DIR_CLEAN, out_path=CSV_DIR_ANALYS):
    # stop if in_path doesn't exist
    if not os.path.isdir(in_path):
        print u'%s is not a valid path' % in_path
        exit(0)
    # create out_path if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    # Load known variables
    A = MakeInfo()
    A.makeAbbrevLicense()
    A.makeAbbrevSource()

    # start analysis
    analyseYear(file_in=u'%s/%s.csv' % (in_path, 'ausstellung'),
                file_out=u'%s/analys-%s.txt' % (out_path, 'ausstellung')
                )
    analysePhoto(A,
                 file_in=u'%s/%s.csv' % (in_path, 'photo'),
                 file_out=u'%s/analys-%s.txt' % (out_path, 'photo')
                 )
    analyseMulti(file_in=u'%s/%s.csv' % (in_path, 'multimedia'),
                 file_out=u'%s/analys-%s.txt' % (out_path, 'multimedia')
                 )


def analyseYear(file_in=u'Ausstellung_1.1.csv', file_out=u'analys-Ausstellung.txt'):
    '''
    Exhibitanalyser:
    verifies that the year can be interpreted
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
    first = True
    for l in lines:
        if first:
            first = False
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
            elif (lyear == 4) and (lyfrom != 0):
                if int(year) != int(yfrom[:4]):
                    data.append(u'error y2|%s' % lout)
                # elif lytil != 0 and int(ytil[:4]) != int(year):
                #    data.append(u'error y7|%s' % lout)
            elif (lyear == 9) and (lyfrom != 0 or lytil != 0):
                if lyfrom != 0 and int(year[:4]) != int(yfrom[:4]):
                    data.append(u'error y3|%s' % lout)
                elif lytil != 0 and int(year[-4:]) != int(ytil[:4]):
                    data.append(u'error y3|%s' % lout)
    # loop done
    f = codecs.open(file_out, 'w', 'utf-8')
    f.write(u'<!--From: %s -->\n' % file_in)
    f.write(u'===year problems===\n')
    f.write(u'y1:\t Could not match JahrS to any YYYY or YYYY-YYYY or YYYY-YY\n')
    f.write(u'y2:\t JahrS is not the same as starting year in Von-Bis range')
    f.write(u'- please amend JahrS\n')
    f.write(u'y3:\t JahrS is span which doesn\'t match in Von-Bis range')
    f.write(u'- please amend as appropriate\n')
    f.write(u'#error\tAusId\tAusJahrS\tAusDatumVonD\tAusDatumBisD\n')
    for d in data:
        splits = d.split('|')
        txt = ''
        for s in splits:
            txt = u'%s\t%s' % (txt, s)
        f.write(u'%s\n' % txt[7:])
    f.close()
# done


def analysePhoto(A, file_in=u'photo_1.2.csv', file_out=u'analys-photo.txt'):
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
    f = codecs.open(file_out, 'w', 'utf-8')
    f.write(u'<!--From: %s -->\n' % file_in)
    first = True
    for l in lines:
        if first:
            first = False
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
        f.write(u'there are NO dupes in MullId\n')
    if len(dupePhoid) != 0:
        f.write(u'---Duplicate phoIds with different info---\n')
        for k, v in dupePhoid.iteritems():
            f.write(u'%s: %s <> %s\n' % (v[0], k, v[1]))
    f.close()
# done


def analyseMulti(file_in=u'multimedia_1.2.csv', file_out=u'analys-multimedia.txt'):
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
    f = codecs.open(file_out, 'w', 'utf-8')
    f.write(u'<!--From: %s -->\n' % file_in)
    first = True
    for l in lines:
        if first:
            first = False
            continue
        col = l.split('|')
        idd = col[1]  # MulPhoId
        fullname = ''.join([col[2], col[3], col[4]])
        # test if each filename has only one photoid
        if fullname in ndict.keys():
            if idd != ndict[fullname]:
                ndiffCount = ndiffCount+1
                print idd, ndict[fullname]
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
    f.close()
    print sameCount, diffCount, ccount, ndiffCount
    print len(lines), len(ids)
# done


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_analyseCSVData.py in_path out_path\n' \
        + u'\tin_path (optional):the relative pathname to the ' \
        + u'cleaned csv directory. Defaults to "%s"\n' % CSV_DIR_CLEAN \
        + u'\tout_path (optional):the relative pathname to the target ' \
        + u'directory. Defaults to "%s"' % CSV_DIR_ANALYS
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 2:
        run(in_path=argv[0], out_path=argv[1])
    else:
        print usage
# EoF
