#!/usr/bin/python
# -*- coding: UTF-8
#
# Take cleaned csv files to deriv-state
# This is a quick setup reusing prewritten functions but not outputting
# separate files inbetween. Yes I know the code is horrible!
#
# Includes the following old files:
# * py-makePhoto_multi.py
# * py-Py-Photo-ObjDaten
#
# TODO: Make sure dicts/txt are del after they are used to free up memory
#
'''what to run:
crunchFiles()

All functions take as input, and output, csv text strings
where the first line is the header
'''
import codecs
import os
import urllib2
from common import Common

CSV_DIR_CLEAN = u'clean_csv'
CSV_DIR_CRUNCH = u'deriv_csv'


def crunchFiles(in_path=CSV_DIR_CLEAN, out_path=CSV_DIR_CRUNCH):
    # create target if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    # load clean_csv
    f = codecs.open(u'%s/photo.csv' % CSV_DIR_CLEAN, 'r', 'utf-8')
    photo = f.read()
    f = codecs.open(u'%s/multimedia.csv' % CSV_DIR_CLEAN, 'r', 'utf-8')
    multi = f.read()
    f = codecs.open(u'%s/photoObjDaten.csv' % CSV_DIR_CLEAN, 'r', 'utf-8')
    photoObjDaten = f.read()
    f = codecs.open(u'%s/objDaten.csv' % CSV_DIR_CLEAN, 'r', 'utf-8')
    objDaten = f.read()
    f.close()

    # start crunching
    # combine photo and multi
    photo_multi = makePhoto_multi(photo, multi, log=u'%s/photo_multimedia.log' % CSV_DIR_CRUNCH, tmp=u'%s/tmp-photo-multi.csv' % CSV_DIR_CRUNCH)
    del photo, multi

    # combine photoObjDaten, photo_multi, objDaten
    # combines all objId into the photo file ";"-separated
    photo_multimedia_ObjIds = photo_ObjDaten(photo_multi, photoObjDaten, objDaten, log=u'%s/photo_objDaten.log' % CSV_DIR_CRUNCH)
    del photo_multi, photoObjDaten


def makePhoto_multi(photo, multi, log, tmp):
    '''
    given the photo and multimedia data this combines the two
    Note: multimedia file must be preped so that each filename
          points to a unique photoId
    '''
    linesP = photo.split('\n')
    linesM = multi.split('\n')
    headerP = linesP.pop(0).split('|')
    headerM = linesM.pop(0).split('|')
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows
    out = u''
    print u"Combining photo and multimedia file for unique files..."
    flog.write(u'---same files used by different MulPhoId---\n')
    flog.write(u'kept: (MulPhoId/MullId) skipped: (MulPhoId/MullId), file: ...\n')

    # read multi into dictionary
    # MulId|MulPhoId|MulPfadS|MulDateiS|MulExtentS
    mDict = {}
    mulPhoIdList = []  # also filter out any duplicates of this
    dcounter = 0  # number of ignored/duplicate files
    for l in linesM:
        if len(l) == 0:
            continue
        col = l.split('|')
        name = u'%s\\%s.%s' % (col[2], col[3], col[4])
        mulPhoId = col[1]
        if mulPhoId in mulPhoIdList:
            dcounter = dcounter+1
            continue
        elif name in mDict.keys():
            dcounter = dcounter+1
            flog.write(u'kept: %s/%s, skipped: %s/%s, file: %s\n' \
                       % (mDict[name][1], mDict[name][0], col[1], col[0], name))
            continue
        else:
            mDict[name] = col
            mulPhoIdList.append(mulPhoId)
    print u'multimedia: %d (%d)' % (len(mDict), dcounter)
    headerM.remove(u'MulPhoId')
    headerM.remove(u'MulId')

    # read photo into dictionary
    # PhoId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|PhoSwdS|MulId|AdrVorNameS|AdrNameS|PhoSystematikS
    pDict = {}
    dcounter = 0  # number of ignored/duplicate rows
    for l in linesP:
        col = l.split('|')
        phId = col[0]
        if phId in pDict.keys():
            dcounter = dcounter+1
            continue
        else:
            pDict[phId] = col
    print u'photo: %d (%d)' % (len(pDict), dcounter)
    headerP.remove(u'PhoId')
    headerP.remove(u'MulId')

    # make new file
    usedphIds = []
    header = [u'PhoId', u'MulId']+headerP+headerM
    out += u'%s\n' % '|'.join(header)
    for k, rowM in mDict.iteritems():
        phId = rowM[1]
        mId = rowM[0]
        del rowM[1]
        del rowM[0]
        if phId in pDict.keys():
            rowP = list(pDict[phId])  # clone
            del rowP[5]
            del rowP[0]
            row = [phId, mId]+rowP+rowM
            out += u'%s\n' % '|'.join(row)
            usedphIds.append(phId)
        else:
            # log any unused rows in multimedia
            row = [phId, mId]+rowM
            flog.write(u'%s\n' % '|'.join(row))
    # log any unused rows in photo
    flog.write(u'------unused rows in photo-------\n')
    usedphIds = list(set(usedphIds))  # remove dupes
    for phId in usedphIds:
        pDict.pop(phId)
    for phId, rowP in pDict.iteritems():
        mId = rowP[5]
        del rowP[5]
        del rowP[0]
        row = [phId, mId]+rowP
        flog.write(u'%s\n' % '|'.join(row))
    flog.close()
    print u"...done"

    # check if anything needs to be manually handled
    while True:
        print u"Read the log (%s)" % log
        choice = raw_input(u"Does the file need to be manually updated? [Y/N]:")
        if choice in ('y', 'Y'):
            f = codecs.open(tmp, 'w', 'utf8')
            f.write(out)
            f.close()
            print u"Open the temporary file (%s), make any changes " \
                  u"and save" % tmp
            raw_input(u"Press enter when done")
            f = codecs.open(tmp, 'r', 'utf8')
            out = f.read()
            f.close()
            break
        elif choice in ('n', 'N'):
            break
        print "Unrecognised input (%s), try again" % choice
    return out


def photo_ObjDaten(photo_multi, photoObjDaten, objDaten, log):
    '''
    bla
    '''
    linesP = photo_multi.split('\n')
    headerP = linesP.pop(0).split('|')
    poDict = makePOdict(photoObjDaten)
    oDict = makeOdict(objDaten)
    out = u''
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows
    print u"Combining all ObjId into the photo file..."

    # match objInv to ObjId
    print 'matching objInv to ObjId'
    flog.write(u'-----unknown objInvs------\n')
    finalDict = {}
    for phoId, v in poDict.iteritems():
        objIds = []
        for objInv in v:
            if objInv not in oDict.keys():
                print 'crap'
                flog.write(u'%s\n' % objInv)
            else:
                objIds = objIds+oDict[objInv]
        objIds = list(set(objIds))  # remove dupes
        finalDict[phoId] = objIds

    # read in photo_multi and write to new file
    # PhoId|MulId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|PhoSwdS|AdrVorNameS|AdrNameS|PhoSystematikS|MulPfadS|MulDateiS|MulExtentS
    pUsed = []
    out += u'%s\n' % '|'.join(headerP)
    for l in linesP:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[0]
        objId = col[2]
        if phoId in finalDict.keys():
            pUsed.append(phoId)
            objIds = finalDict[phoId]
            if objId not in objIds:
                objIds.append(objId)
            col[2] = ';'.join(objIds)
            out += u'%s\n' % '|'.join(col)
        else:
            out += u'%s\n' % l

    # make sure nothing is left
    for phoId in pUsed:
        finalDict.pop(phoId)
    if len(finalDict) != 0:
        flog.write(u'-----left in finalDict------\n')
        for k, v in finalDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))
    flog.close()
    print u"...done"
    return out
#
def makePOdict(photoObjDaten):
    '''
    called by photo_ObjDaten()
    '''
    linesPO = photoObjDaten.split('\n')
    headerPO = linesPO.pop(0).split('|')
    # read Photo_-_ObjDaten into dictionary
    # PhmId|AufId|AufAufgabeS|MulId|PhoId|ObjInvNrS
    poDict = {}
    dcounter = 0  # number of ignored/duplicate files
    for l in linesPO:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[4]
        objInv = col[5].strip()
        if len(objInv) == 0:
            dcounter = dcounter+1
            continue
        elif phoId in poDict.keys():
            if objInv in poDict[phoId]:  # ignore duplicate rows
                continue
            else:
                poDict[phoId].append(objInv)
        else:
            poDict[phoId] = [objInv, ]
    print 'Photo-ObjDaten: ', (len(linesPO)-1), len(poDict), dcounter
    # write to backup-file
    # ftempPO = codecs.open(u'tempPO', 'w', 'utf-8')
    # for k,v in poDict.iteritems():
    #     ftempPO.write(u'%s|%s\n' %(k,';'.join(v)))
    # ftempPO.close()
    # print 'wrote to tempPO'
    return poDict
#
def makeOdict(objDaten):
    '''
    called by photo_ObjDaten()
    '''
    linesO = objDaten.split('\n')
    headerO = linesO.pop(0).split('|')
    # read (parts of) ObjDaten into dictionary
    # ObjId|ObjKueId|AufId|AufAufgabeS|ObjTitelOriginalS|ObjTitelWeitereM|ObjInventarNrS|ObjInventarNrSortiertS|ObjReferenzNrS|ObjDatierungS|ObjJahrVonL|ObjJahrBisL|ObjSystematikS|ObjFeld01M|ObjFeld02M|ObjFeld03M|ObjFeld06M|ObjReserve01M
    oDict = {}
    dcounter = 0  # number of ignored/duplicate files
    c = 0
    for l in linesO:
        if len(l) == 0:
            continue
        c = c+1
        col = l.split('|')
        objId = col[0]
        objInv = col[6]
        if len(objInv) == 0:
            dcounter = dcounter+1
            continue
        elif objInv in oDict.keys():
            if objId in oDict[objInv]:  # ignore complete duplicates
                continue
            else:
                oDict[objInv].append(objId)
        else:
            oDict[objInv] = [objId, ]
        if c % 1000 == 0:
            print u'%r lines read' % c
    print 'ObjDaten: ', (len(linesO)-1), len(oDict), dcounter
    # write to backup-file
    # ftempO = codecs.open(u'tempO', 'w', 'utf-8')
    # for k,v in oDict.iteritems():
    #     ftempO.write(u'%s|%s\n' %(k,';'.join(v)))
    # ftempO.close()
    # print 'wrote to tempO'
    return oDict
