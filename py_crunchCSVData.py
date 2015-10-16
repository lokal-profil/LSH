#!/usr/bin/python
# -*- coding: UTF-8
#
# Take cleaned csv files to deriv-state
# This is a quick setup reusing prewritten functions but not outputting
# separate files inbetween. Yes I know the code is horrible!
#
# Includes the following old files:
# * py-makePhoto_multi.py
# * py-Photo-ObjDaten
# * py-TrimObjDaten.py
# * py-Stichwort-photo.py
# * py-samesame.py
# * py-Ausstellung-trim.py
# * py-ObjDaten-sam.py
# * py-Ereignis-trim.py
# * py-kunstler-trim.py
# * py-Mul-mass-add.py
# * py-Mul-mass-trim.py
# * py-realObjOnly.py
#
# TODO: Stick CSV_FILES in start of file (or somewhere equally easy)
# TODO: Cut down log files to only ones worth reading
# TODO: Rewrite using dicts instead of long strings
#
'''
what to run:
crunchFiles()

All functions take as input, and output, csv text strings
where the first line is the header
'''
import codecs
import os
from common import Common

CSV_DIR_CLEAN = u'clean_csv'
CSV_DIR_CRUNCH = u'data'


def crunchFiles(in_path=CSV_DIR_CLEAN, out_path=CSV_DIR_CRUNCH):
    # convert to unicode if not the case
    if type(in_path) == str:
        in_path = unicode(in_path)
    if type(out_path) == str:
        out_path = unicode(out_path)
    # create target if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    log_path = os.path.join(out_path, u'logs')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    # start crunching
    # combine photo and multi
    # py-makePhoto_multi.py
    photo = loadCsv(in_path, u'photo.csv')
    multi = loadCsv(in_path, u'multimedia.csv')
    logFile = os.path.join(log_path, u'photo_multimedia.log')
    tmpFile = os.path.join(out_path, u'tmp-photo-multi.csv')
    photo_multi = makePhoto_multi(photo, multi, log=logFile, tmp=tmpFile)
    del photo, multi

    # combine photo and Photo-ObjDaten
    # populates the objId column with ALL of the relevant ObjIds
    # py-Photo-ObjDaten
    photoObjDaten = loadCsv(in_path, u'photoObjDaten.csv')
    objDaten = loadCsv(in_path, u'objDaten.csv')
    logFile = os.path.join(log_path, u'photo_objDaten.log')
    photo_multimedia_objIds = photo_ObjDaten(photo_multi, photoObjDaten, objDaten, log=logFile)
    del photo_multi, photoObjDaten

    # removes unused Objects from ObjDaten
    # py-TrimObjDaten.py
    objDaten_trim = trimObjDaten(objDaten, photo_multimedia_objIds)
    # objDaten not deleted as used again in realObjOnly()

    # Adds the stichwort id column to photo and
    # removes unused photoIds from stichworth
    # py-Stichwort-photo.py
    stichwort = loadCsv(in_path, u'stichwort.csv')
    logFile = os.path.join(log_path, u'stichworth_photo.log')
    photo_multimedia_ObjIds_stichID, stichwort_trim = stichworth_photo(photo_multimedia_objIds, stichwort, log=logFile)
    del photo_multimedia_objIds, stichwort

    # Add two columns to photo:
    # * same photoId-different file
    # * same objId-different photoID
    # py-samesame.py
    photo_multimedia_ObjIds_stichID_samesame = samesame(photo_multimedia_ObjIds_stichID)
    del photo_multimedia_ObjIds_stichID

    # Trimms Ausstellung to unique ids and adds Ausstellung column to ObjDaten
    # py-Ausstellung-trim.py
    print u"Confirm that any year formating issues mentioned in the analysis " \
          u"log have been corrected and the updated ausstellung file saved..."
    raw_input(u"...by pressing enter when done")
    ausstellung = loadCsv(in_path, u'ausstellung.csv')
    logFile = os.path.join(log_path, u'ausstellung.log')
    ausstellung_trim, objDaten_trim_ausstellung = ausstellung_objDaten(ausstellung, objDaten_trim, log=logFile)
    del ausstellung, objDaten_trim

    # adds ObjDaten-samhörande column to ObjDaten
    # py-ObjDaten-sam.py
    objDatenSam = loadCsv(in_path, u'objDatenSam.csv')
    logFile = os.path.join(log_path, u'objDatenSam.log')
    objDaten_trim_ausstellung_sam = objDaten_sam(objDatenSam, objDaten_trim_ausstellung, log=logFile)
    del objDatenSam, objDaten_trim_ausstellung

    # trimms Eregnis to unique ids and adds Eregnis column to ObjDaten
    # py-Ereignis-trim.py
    ereignis = loadCsv(in_path, u'ereignis.csv')
    logFile = os.path.join(log_path, u'ereignis.log')
    objDaten_trim_ausstellung_sam_eregnis, ereignis_trim = ereignis_objDaten(ereignis, objDaten_trim_ausstellung_sam, log=logFile)
    del ereignis, objDaten_trim_ausstellung_sam

    # Trims kuenstler to remove certain irrelevant roles and dummy entries
    # also standardises years and removes some irrelevant columns and
    # appends kuenstler id's to objDaten
    # py-kunstler-trim.py
    kuenstler = loadCsv(in_path, u'kuenstler.csv')
    logFile = os.path.join(log_path, u'kuenstler.log')
    objDaten_trim_ausstellung_sam_eregnis_kuenstler, kuenstler_trim, kuenstler_roles = kuenstler_objDaten(objDaten_trim_ausstellung_sam_eregnis, kuenstler, log=logFile)
    del objDaten_trim_ausstellung_sam_eregnis, kuenstler
    del kuenstler_roles  # makeRoles in MakeInfo is hardcoded so currently no need to keep

    # Add objMul and objMass columns to ObjDaten
    # then trim objMul and objMass
    # py-Mul-mass-add.py
    # py-Mul-mass-trim.py
    objMass = loadCsv(in_path, u'objMass.csv')
    objMultiple = loadCsv(in_path, u'objMultiple.csv')
    logFile = os.path.join(log_path, u'mulMass.log')
    objDaten_trim_ausstellung_sam_eregnis_kuenstler_mulMass, objMass_trim, objMultiple_trim = mulMass_add(objMass, objMultiple, objDaten_trim_ausstellung_sam_eregnis_kuenstler, log=logFile)
    del objMass, objMultiple, objDaten_trim_ausstellung_sam_eregnis_kuenstler

    # Removes objIds from photo which are not in ObjDaten
    # py-realObjOnly.py
    logFile = os.path.join(log_path, u'realObjOnly.log')
    photo_multimedia_ObjIds_stichID_samesame_real = realObjOnly(objDaten_trim_ausstellung_sam_eregnis_kuenstler_mulMass, photo_multimedia_ObjIds_stichID_samesame, objDaten, log=logFile)
    del objDaten, photo_multimedia_ObjIds_stichID_samesame

    # output all the above
    # comments are filenames used in the original upload
    out_csv = {u'photo_multimedia_etc': photo_multimedia_ObjIds_stichID_samesame_real,  # deriv-photo_multimedia_ObjIds_stichID_samesame_real_noDupes.csv
               u'stichwort_trim': stichwort_trim,  # deriv-Photo_stichwort_trim.csv
               u'objMass_trim': objMass_trim,  # deriv-ObjMass.csv
               u'objMultiple_trim': objMultiple_trim,  # deriv-ObjMultiple.csv
               u'objDaten_etc': objDaten_trim_ausstellung_sam_eregnis_kuenstler_mulMass,  # deriv-ObjDaten-trimmed_Ausstellung_sam_eregnis_kuenstler_MulMass.csv
               u'ausstellung_trim': ausstellung_trim,  # deriv-Ausstellung_trim.csv
               u'ereignis_trim': ereignis_trim,  # deriv-Ereignis_trim.csv
               u'kuenstler_trim': kuenstler_trim  # deriv-kuenstler_trim.csv
               }
    for k, v in out_csv.iteritems():
        outFile = os.path.join(out_path, u'%s.csv' % k)
        f = codecs.open(outFile, 'w', 'utf-8')
        f.write(v)
        f.close()
        print u'\tOutputted %s' % outFile
    print u'Done!'


def makePhoto_multi(photo, multi, log, tmp):
    '''
    given the photo and multimedia data this combines the two
    Note: multimedia file must be prepped so that each filename
          points to a unique photoId
    '''
    linesP = photo.split('\n')
    linesM = multi.split('\n')
    headerP = linesP.pop(0).split('|')
    headerM = linesM.pop(0).split('|')
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows
    out = u''
    print u"Combining photo and multimedia file for unique files..."
    flog.write(u'---same files used by different MulPhoId, format is MulPhoId/MullId---\n')

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
            flog.write(u'kept: %s/%s, skipped: %s/%s, file: %s\n'
                       % (mDict[name][1], mDict[name][0], col[1], col[0], name))
            continue
        else:
            mDict[name] = col
            mulPhoIdList.append(mulPhoId)
    print u'\tmultimedia: %d (%d)' % (len(mDict), dcounter)
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
    print u'\tphoto: %d (%d)' % (len(pDict), dcounter)
    headerP.remove(u'PhoId')
    headerP.remove(u'MulId')

    # make new file
    usedphIds = []
    header = [u'PhoId', u'MulId']+headerP+headerM
    out += u'%s\n' % '|'.join(header)
    for k, rowM in mDict.iteritems():
        phId = rowM[1]
        mId = rowM[0]
        rowM[2] = rowM[2].replace(u'R:\web\hires\\', u'')  # trim filepath
        rowM[4] = u''  # MulExtentS is always wrong
        del rowM[1], rowM[0]
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
    flog.write(u'------\nAction needed if unused do not coincide with duplicates')
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
    combine photo and Photo-ObjDaten
    populates the objId column with ALL of the relevant ObjIds
    ;-separated
    '''
    linesP = photo_multi.split('\n')
    headerP = linesP.pop(0).split('|')
    print u"Combining all ObjId into the photo file..."
    poDict = makePOdict(photoObjDaten)
    oDict = makeOdict(objDaten)
    out = u''
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows

    # match objInv to ObjId
    finalDict = {}
    skipped = []
    for phoId, v in poDict.iteritems():
        objIds = []
        for objInv in v:
            if objInv not in oDict.keys():
                skipped.append(objInv)
            else:
                objIds = objIds+oDict[objInv]
        objIds = list(set(objIds))  # remove dupes
        finalDict[phoId] = objIds
    if len(skipped) != 0:
        print u"\tthere were %d skipped ObjIds, see log (%s)" % (len(skipped), log)
        flog.write(u'-----------')
        flog.write(u'Unknown objInvs, i.e. ObjInvNrS in photoObjDaten ')
        flog.write(u'without a match in ObjDaten')
        flog.write(u'-----------\n')
        flog.write(u'%s\n' % '|'.join(skipped))
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
        flog.write(u'-----left in finalDict------\n')  # phoId in photoObjDaten without a match in photo
        for k, v in finalDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))
    flog.close()
    print u"...done"
    return out


def makePOdict(photoObjDaten):
    '''
    called by photo_ObjDaten()
    '''
    linesPO = photoObjDaten.split('\n')
    linesPO.pop(0).split('|')  # split off headerPO
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
    print '\tphoto-objDaten: %d lines, %d uniques, %d dupes' % (len(linesPO), len(poDict), dcounter)
    # write to backup-file
    # ftempPO = codecs.open(u'tempPO', 'w', 'utf-8')
    # for k,v in poDict.iteritems():
    #     ftempPO.write(u'%s|%s\n' %(k,';'.join(v)))
    # ftempPO.close()
    # print 'wrote to tempPO'
    return poDict


def makeOdict(objDaten):
    '''
    called by photo_ObjDaten()
    '''
    linesO = objDaten.split('\n')
    linesO.pop(0).split('|')  # split off headerO
    # read (parts of) ObjDaten into dictionary
    # ObjId|ObjKueId|AufId|AufAufgabeS|ObjTitelOriginalS|ObjTitelWeitereM|ObjInventarNrS|ObjInventarNrSortiertS|ObjReferenzNrS|ObjDatierungS|ObjJahrVonL|ObjJahrBisL|ObjSystematikS|ObjFeld01M|ObjFeld02M|ObjFeld03M|ObjFeld06M|ObjReserve01M
    oDict = {}
    dcounter = 0  # number of ignored/duplicate files
    for l in linesO:
        if len(l) == 0:
            continue
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
    print '\tobjDaten: %d lines, %d uniques, %d dupes' % (len(linesO), len(oDict), dcounter)
    return oDict


def trimObjDaten(objDaten, photo_multimedia_objIds):
    '''
    Removes unused objects from ObjDaten, because it is huge!
    '''
    linesP = photo_multimedia_objIds.split('\n')
    linesP.pop(0).split('|')  # split off headerP
    linesO = objDaten.split('\n')
    headerO = linesO.pop(0).split('|')
    out = u''
    print u"Trimming objDaten..."

    # read multi into dictionary
    # MulId|MulPhoId|MulPfadS|MulDateiS|MulExtentS
    objIdList = []
    dcounter = 0  # number of ignored/duplicate files
    for l in linesP:
        if len(l) == 0:
            continue
        col = l.split('|')
        objIds = col[2].split(';')
        for objId in objIds:
            if objId in objIdList:
                dcounter = dcounter+1
                continue
            objIdList.append(objId)
    print '\tobjIds: %d uniques, %d dupes' % (len(objIdList), dcounter)
    # read in ObjDaten and write to new file
    out += u'%s\n' % '|'.join(headerO)
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        if objId in objIdList:
            out += u'%s\n' % l
    print u"...done"
    return out


def stichworth_photo(photo_multimedia_objIds, stichwort, log):
    '''
    Adds the stichwort id column to photo and trims stichwort
    '''
    linesP = photo_multimedia_objIds.split('\n')
    headerP = linesP.pop(0).split('|')
    linesS = stichwort.split('\n')
    headerS = linesS.pop(0).split('|')
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows
    out = u''
    outS = u''
    print u"Adding stichworth to photo"

    # read stichwort into dictionary
    print u"\treading stichwort into dictionary..."
    pDict = {}
    dcounter = 0  # number of ignored/duplicate ids
    for l in linesS:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[1]
        pstId = col[0]
        if phoId in pDict.keys():
            if pstId in pDict[phoId]:
                dcounter = dcounter+1
            else:
                pDict[phoId].append(pstId)
        else:
            pDict[phoId] = [pstId, ]
    print '\tphoIds: %d lines, %d uniques, %d dupes' % (len(linesS), len(pDict), dcounter)

    print '\tadding stich id to photo...'
    # read in photo... and write to new file
    pUsed = []
    out += u'%s|PstId\n' % '|'.join(headerP)
    for l in linesP:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[0]
        pstId = ''
        if phoId in pDict.keys():
            pUsed.append(phoId)
            pstId = ';'.join(pDict[phoId])
        out += u'%s|%s\n' % (l, pstId)
    # make sure nothing is left
    pUsed = list(set(pUsed))  # remove dupes
    for phoId in pUsed:
        pDict.pop(phoId)

    print '\ttriming stichwort...'
    # remove any unused stichwort items
    # read in stichwort... and write to new file
    outS += u'%s\n' % '|'.join(headerS)
    for l in linesS:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[1]
        if phoId in pDict.keys():
            continue
        outS += u'%s\n' % l
    # check if anything is left
    if len(pDict) != 0:
        flog.write(u'-----removed from stich, format PhoId|PstIds------\n')
        for k, v in pDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))
    flog.close()
    print u"...done"
    return (out, outS)


def samesame(photo_multimedia_ObjIds_stichID):
    '''
    Add two columns to photo:
    * same photoId-diff file
    * same obj diff photoID
    '''
    linesP = photo_multimedia_ObjIds_stichID.split('\n')
    headerP = linesP.pop(0).split('|')
    out = u''

    print u"Samesame()"
    print u"\treading photo into dictionary..."
    # read stichwort into dictionary
    oDict = {}
    fDict = {}
    fc = 0  # number of ignored/duplicate filenames
    oc = 0  # number of ignored/duplicate objIds
    for l in linesP:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[0]
        pho_mullId = '%s:%s' % (col[0], col[1])
        objIds = col[2].split(';')
        # filenames
        if phoId in fDict.keys():
            if pho_mullId in fDict[phoId]:
                fc = fc+1
            else:
                fDict[phoId].append(pho_mullId)
        else:
            fDict[phoId] = [pho_mullId, ]
        # objIds
        if len(col[2]) == 0:
            continue
        for o in objIds:
            if o in oDict.keys():
                if (phoId, pho_mullId) in oDict[o]:
                    oc = oc+1
                else:
                    oDict[o].append((phoId, pho_mullId))
            else:
                oDict[o] = [(phoId, pho_mullId), ]
    # remove any with only one associated file
    for k in fDict.keys():
        if len(fDict[k]) < 2:
            del fDict[k]
    # remove any with only one associated phoId
    for k in oDict.keys():
        if len(oDict[k]) < 2:
            del oDict[k]
    print u'\tfilenames: %d lines, fDict: %d (dupes: %d), oDict: %d (dupes: %d)' \
          % (len(linesP), len(fDict), fc, len(oDict), oc)

    print '\tinverting oDict...'
    # invert oDict
    # har obj med flera photo
    pDict = {}
    for objId, phIds in oDict.iteritems():
        all_Pho_Mull = [a[1] for a in phIds]
        for phId, pho_mullId in phIds:
            if phId in pDict.keys():
                pDict[phId] = pDict[phId]+all_Pho_Mull
            else:
                pDict[phId] = all_Pho_Mull

    print '\tadding samesame to photo...'
    # read in photo... and write to new file
    out += u'%s|same_PhoId|same_object\n' % '|'.join(headerP)
    for l in linesP:
        if len(l) == 0:
            continue
        col = l.split('|')
        phoId = col[0]
        pho_mullId = '%s:%s' % (col[0], col[1])
        samePhoId = ''
        sameObjId = ''
        if phoId in fDict.keys():
            ll = list(fDict[phoId])  # clone
            ll.remove(pho_mullId)    # remove self
            samePhoId = ';'.join(ll)
        if phoId in pDict.keys():
            ll = list(set(pDict[phoId]))  # clone and remove dupes
            ll.remove(pho_mullId)         # remove self
            sameObjId = ';'.join(ll)
        out += u'%s|%s|%s\n' % (l, samePhoId, sameObjId)
    print u"...done"
    return out


def ausstellung_objDaten(austellung, objDaten_trim, log):
    '''
    Trimms Ausstellung to unique ids and adds Ausstellung column to ObjDaten
    '''
    linesA = austellung.split('\n')
    headerA = linesA.pop(0).split('|')
    linesO = objDaten_trim.split('\n')
    headerO = linesO.pop(0).split('|')
    out = u''   # objDaten+Ausstellung
    outA = u''  # Ausstellung_trim
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows

    print u"Trimming Ausstellung and adding Ausstellung to ObjDaten..."
    print u"\treading Ausstellung into dictionary"
    # read Ausstellung into dictionary
    # AobId|AusId|AusTitelS|AusOrtS|AusJahrS|AusDatumVonD|AusDatumBisD|AobObjId|AufAufgabeS
    aDict = {}
    newA = {}
    newAheader = [headerA[1], headerA[2], headerA[3], u'std_year', headerA[4], headerA[5], headerA[6], headerA[8], headerA[7]]
    dcounter = 0  # number of ignored/duplicate ids
    dummytitles = [u'reparation', u'utställning', u'OBS! Testpost för admin - utställning, export wikimedia commons', u'lån för undersökning', u'lån till Frankrike 1947', u'test karin 20100520', u'test 20100629 (en post skapad för administrativa tester)', u'tennföremål 8 st till Strömsholm', u'utlån f justering av urverk']
    for l in linesA:
        if len(l) == 0:
            continue
        col = l.split('|')
        ausId = col[1]
        objId = col[7]
        title = col[2]
        year = col[4].strip()
        yfrom = col[5].replace(u' 00:00:00', u'').strip()
        ytil = col[6].replace(u' 00:00:00', u'').strip()
        if len(title) == 0 or title in dummytitles:  # remove empty/dummy
            continue
        if ausId in aDict.keys():
            if objId in aDict[ausId]:
                dcounter = dcounter+1
            else:
                aDict[ausId].append(objId)
        else:
            aDict[ausId] = [objId, ]
            newA[ausId] = [title, col[3], stdYear(year, yfrom, ytil), year, yfrom, ytil, col[8]]
    print '\tausIds: %d lines, %d uniques, %d dupes' % (len(linesA), len(aDict), dcounter)

    # add obj to newA and invert aDict
    print '\tinverting aDict'
    oDict = {}
    for ausId, objIds in aDict.iteritems():
        newA[ausId].append(';'.join(objIds))
        for objId in objIds:
            if objId in oDict.keys():
                if ausId in oDict[objId]:
                    continue
                else:
                    oDict[objId].append(ausId)
            else:
                oDict[objId] = [ausId, ]

    print '\tadding ausId id to objDaten...'
    # read in photo... and write to new file
    oUsed = []
    out += u'%s|ausId\n' % '|'.join(headerO)
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        ausId = ''
        if objId in oDict.keys():
            oUsed.append(objId)
            ausId = ';'.join(oDict[objId])
        out += u'%s|%s\n' % (l, ausId)
    # make sure nothing is left
    oUsed = list(set(oUsed))  # remove dupes
    for objId in oUsed:
        oDict.pop(objId)
    if len(oDict) != 0:
        flog.write(u'-----left in oDict------\n')
        for k, v in oDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))

    print '\tcreating trimmed ausstellung'
    # create trimmed Austellungfile
    outA += u'%s\n' % '|'.join(newAheader)
    for ausId in sorted([int(a) for a in newA.iterkeys()]):
        outA += u'%s|%s\n' % (str(ausId), '|'.join(newA[str(ausId)]))
    flog.close()
    print u"...done"
    return outA, out


def stdYear(year, yfrom, ytil):
    '''returns a standardised year in either YYYY or YYYY-YYYY
       assumes all errors part from y1 and y7 (in py-Ausstellung) have been fixed
       TODO: Shift to common
    '''
    lyear = len(year)
    lyfrom = len(yfrom)
    lytil = len(ytil)
    if lyear == 9:  # YYYY-YYYY
        return '%r-%r' % (int(year[:4]), int(year[5:]))
    elif lyear == 7:  # YYYY-YY
        return '%r-%r%r' % (int(year[:4]), int(year[:2]), int(year[5:]))
    elif lyear == 4:  # YYYY
        if lyfrom != 0 and int(yfrom[:4]) != int(year):
            # yfrom takes precedence over year
            year = int(yfrom[:4])
        if lytil != 0 and int(ytil[:4]) != int(year):
            return '%r-%r' % (int(year), int(ytil[:4]))
        else:
            return '%r' % int(year)
    elif lyear == 0:
        if lyfrom != 0 and lytil != 0:
            if int(yfrom[:4]) == int(ytil[:4]):
                return '%r' % int(yfrom[:4])
            else:
                return '%r-%r' % (int(yfrom[:4]), int(ytil[:4]))
        elif lyfrom != 0:
            return '%r' % int(yfrom[:4])
        else:
            return ''
    else:  # weird year
        return year


def objDaten_sam(objDatenSam, objDaten_trim_ausstellung, log):
    '''
    adds ObjDaten-samhörande column to ObjDaten
    '''
    linesOS = objDatenSam.split('\n')
    linesOS.pop(0).split('|')  # headerOS
    linesO = objDaten_trim_ausstellung.split('\n')
    headerO = linesO.pop(0).split('|')
    out = u''
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows

    print u"Adding ObjDaten-samhörande column to ObjDaten"
    print '\treading ObjDaten_-_samhörande_nr into dictionary'
    # OobId|OobObj1ID|OobObj2ID
    oDict = {}
    dcounter = 0  # number of ignored/duplicate ids
    for l in linesOS:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId1 = col[1]
        objId2 = col[2]
        Common.addUniqes(oDict, objId1, objId2, dcounter)
        Common.addUniqes(oDict, objId2, objId1, dcounter)
    print '\tobjIds: %d lines, %d uniques, %d dupes' % (len(linesOS), len(oDict), dcounter)

    print '\tdetermining valid objIds...'
    valids = []
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        valids.append(objId)
    valids = list(set(valids))  # removing dupes

    print '\tremoving dupes, invalids and self...'
    for objId in oDict.keys():
        olist = list(set(oDict[objId]))
        if objId in olist:
            olist.remove(objId)
        remlist = []
        for o in olist:
            if o not in valids:
                remlist.append(o)
        for r in remlist:
            olist.remove(r)
        oDict[objId] = olist

    print '\tadding sam id to objDaten...'
    oUsed = []
    out += u'%s|related\n' % '|'.join(headerO)
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        related = ''
        if objId in oDict.keys():
            oUsed.append(objId)
            related = ';'.join(oDict[objId])
        out += u'%s|%s\n' % (l, related)
    # make sure nothing is left
    oUsed = list(set(oUsed))  # remove dupes
    for objId in oUsed:
        oDict.pop(objId)
    if len(oDict) != 0:
        flog.write(u'-----left in oDict------\n')
        for k, v in oDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))
    flog.close()
    print u"...done"
    return out


def ereignis_objDaten(ereignis, objDaten_trim_ausstellung_sam, log):
    '''
    Trimms Eregnis to unique ids and adds Eregnis column to ObjDaten
    '''
    linesE = ereignis.split('\n')
    headerE = linesE.pop(0).split('|')
    linesO = objDaten_trim_ausstellung_sam.split('\n')
    headerO = linesO.pop(0).split('|')
    out = u''
    outE = u''
    flog = codecs.open(log, 'w', 'utf-8')  # logfile for any unmerged rows

    print u"Trimming Eregnis and adding Eregnis to ObjDaten..."
    print '\treading Ereignis into dictionary'
    # EroId|ErgId|EroObjId|ErgKurztitelS|ErgArtS
    eDict = {}
    newE = {}
    newEheader = [headerE[1], headerE[3], headerE[4], headerE[2]]
    dcounter = 0  # number of ignored/duplicate ids
    dummytitles = []
    for l in linesE:
        if len(l) == 0:
            continue
        col = l.split('|')
        ergId = col[1]
        objId = col[2]
        title = col[3]
        if len(title) == 0 or title in dummytitles:  # remove empty/dummy
            continue
        if ergId in eDict.keys():
            if objId in eDict[ergId]:
                dcounter = dcounter+1
            else:
                eDict[ergId].append(objId)
        else:
            eDict[ergId] = [objId, ]
            newE[ergId] = [title, col[4]]
    print '\tergIds: %d lines, %d uniques, %d dupes' % (len(linesE), len(eDict), dcounter)

    # add obj to newE and invert eDict
    print '\tinverting eDict'
    oDict = {}
    for ergId, objIds in eDict.iteritems():
        newE[ergId].append(';'.join(objIds))
        for objId in objIds:
            Common.addUniqes(oDict, objId, ergId, 0)

    print '\tadding ergId id to objDaten...'
    oUsed = []
    out += u'%s|ergId\n' % '|'.join(headerO)
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        ergId = ''
        if objId in oDict.keys():
            oUsed.append(objId)
            ergId = ';'.join(oDict[objId])
        out += u'%s|%s\n' % (l, ergId)
    # make sure nothing is left
    oUsed = list(set(oUsed))  # remove dupes
    for objId in oUsed:
        oDict.pop(objId)
    if len(oDict) != 0:
        flog.write(u'-----left in oDict------\n')
        for k, v in oDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))

    print '\tcreating new Ereignis...'
    outE += u'%s\n' % '|'.join(newEheader)
    for ergId in sorted([int(e) for e in newE.iterkeys()]):
        url = newE[str(ergId)][1]
        # deal with urlencoded strings
        if u'%' in url:
            url = Common.urldecodeUTF8(url)
        # convert external links to internal
        if 'wikipedia' in url:
            url = Common.external2internalLink(url)
        # TODO: Check end result to se which other urls could appear
        newE[str(ergId)][1] = url
        outE += u'%s|%s\n' % (str(ergId), '|'.join(newE[str(ergId)]))
    flog.close()
    print u"...done"
    return out, outE


def kuenstler_objDaten(objDaten_trim_ausstellung_sam_eregnis, kuenstler, log):
    '''
    Trims kuenstler to remove certain irrelevant roles and dummy entries
    also standardises years and removes some irrelevant columns and
    appends kuenstler id's to objDaten
    '''
    linesK = kuenstler.split('\n')
    headerK = linesK.pop(0).split('|')
    linesO = objDaten_trim_ausstellung_sam_eregnis.split('\n')
    headerO = linesO.pop(0).split('|')
    out = u''  # objDaten_trim_ausstellung_sam_eregnis_kuenstler
    outK = u''  # kuenstler_trim
    outR = u''  # kuenstler_roles
    flog = codecs.open(log, 'w', 'utf-8')  # logfile
    print u"Crunching kuenstler..."

    print '\treading Kunstler into dictionary'
    # OkuId|ObjId|ObjAufId|AufAufgabeS|KueId|KueVorNameS|KueNameS|OkuArtS|OkuFunktionS|OkuValidierungS|KudArtS|KudDatierungS|KudJahrVonL|KudJahrBisL|KudOrtS|KudLandS|KueFunktionS|MulId|PhoId
    oDict = {}
    kDict = {}
    roles = []
    roleCmts = []
    newK = {}
    newKheader = [headerK[4], headerK[5], headerK[6], headerK[11], headerK[12], headerK[13], headerK[14], headerK[15], headerK[16], headerK[1]]
    dcounter = 0  # number of ignored/duplicate ids
    dummytitles = [u'ingen uppgift']
    badRoles = [u'Leverantör', u'Auktion', u'Förmedlare', u'Givare', u'Återförsäljare', u'Konservator']
    badRoleCmts = [u'Förpaktare, kontrollör', u'av kopia']
    for l in linesK:
        if len(l) == 0:
            continue
        col = l.split('|')
        # okuId = col[0]    # OkuId
        objId = col[1]    # ObjId
        kueId = col[4]    # KueId
        fName = col[5]    # KueVorNameS
        lName = col[6]    # KueNameS
        role = col[7]     # OkuArtS
        roleCmt = col[8]  # OkuFunktionS
        # ver = col[9]      # OkuValidierungS
        datum = col[11]   # KudDatierungS
        bYear = col[12]   # KudJahrVonL
        dYear = col[13]   # KudJahrBisL
        land = col[14]    # KudOrtS - missnamed in original database
        ort = col[15]     # KudLandS - missnamed in original database
        yrke = col[16]    # KueFunktionS
        # filter out any undesired rows
        if len(fName) == 0 and (len(lName) == 0 or lName in dummytitles):  # remove empty/dummy
            continue
        if role in badRoles:
            continue
        if roleCmt in badRoleCmts:
            continue
        # take yearinfo out of name
        (lName, bYear, dYear, log) = extractYear(lName, bYear, dYear)
        if len(log) > 0:
            flog.write(log)
        # add to lists and dicts
        roles.append(role)
        roleCmts.append(roleCmt)
        Common.addUniqes(oDict, objId, u'%s:%s:%s' % (role, roleCmt, kueId), dcounter)
        Common.addUniqes(kDict, kueId, objId, 0)
        if kueId not in newK.keys():
            newK[kueId] = [fName, lName, datum, bYear, dYear, ort, land, yrke]
    # clean up lists
    roles = list(set(roles))
    roles.remove('')
    roleCmts = list(set(roleCmts))
    roleCmts.remove('')
    for kueId in kDict:
        klist = list(set(kDict[kueId]))
        newK[kueId].append(';'.join(klist))
    print u'\tobjIds: %d lines, %d uniques, %d dupes, kueIds: %d, roles: %d, roleCmts: %d' % (len(linesK), len(oDict), dcounter, len(newK), len(roles), len(roleCmts))

    print '\tcreating new kunstler...'
    # create trimmed Austellungfile
    outK += u'%s\n' % '|'.join(newKheader)
    for kueId in sorted([int(k) for k in newK.iterkeys()]):
        outK += u'%s|%s\n' % (str(kueId), '|'.join(newK[str(kueId)]))

    print '\tcreating new kunstler-roles...'
    # create trimmed Austellungfile
    roles.sort()
    for role in roles:
        outR += u'%s\n' % role
    outR += '---\n'
    roleCmts.sort()
    for roleCmt in roleCmts:
        outR += u'%s\n' % roleCmt

    print '\tadding kueId to objDaten...'
    oUsed = []
    out += u'%s|role:roleCmt:kueId\n' % '|'.join(headerO)
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        kuenstler = ''
        if objId in oDict.keys():
            oUsed.append(objId)
            kuenstler = ';'.join(oDict[objId])
        out += u'%s|%s\n' % (l, kuenstler)
    # make sure nothing is left
    oUsed = list(set(oUsed))  # remove dupes
    for objId in oUsed:
        oDict.pop(objId)
    if len(oDict) != 0:
        flog.write(u'-----left in oDict------\n')
        for k, v in oDict.iteritems():
            flog.write(u'%s|%s\n' % (k, ';'.join(v)))
    flog.close()
    print u"...done"
    return out, outK, outR


def extractYear(lName, bYear, dYear):
    log = ''
    if len(lName) > 8:
            test = lName[-8:]
            if test[:1] == u'(' and Common.is_number(test[1:5]):
                if len(bYear) > 0 and bYear != test[1:5]:
                    log = u't1: %s\t%s != %s\n' % (lName, test[1:5], bYear)
                else:
                    lName = lName[:-8].strip()
                    bYear = test[1:5]
            elif len(lName) > 11:
                test = lName[-11:]
                if Common.is_number(test[1:5]) and Common.is_number(test[6:10]):
                    if (len(bYear) > 0 and bYear != test[1:5]) or (len(dYear) > 0 and dYear != test[6:10]):
                        log = u't2: %s\t%s != %s\t%s != %s\n' % (lName, test[1:5], bYear, test[6:10], dYear)
                    else:
                        lName = lName[:-11].strip()
                        bYear = test[1:5]
                        dYear = test[6:10]
                elif len(lName) > 13:
                    test = lName[-13:]
                    if Common.is_number(test[2:6]) and Common.is_number(test[7:11]):
                        if (len(bYear) > 0 and bYear != test[2:6]) or (len(dYear) > 0 and dYear != test[7:11]):
                            log = u't3: %s\t%s != %s\t%s != %s\n' % (lName, test[2:6], bYear, test[7:11], dYear)
                        else:
                            lName = lName[:-13].strip()
                            bYear = test[2:6]
                            dYear = test[7:11]
    return (lName, bYear, dYear, log)
#


def mulMass_add(objMass, objMultiple, objDaten_trim_ausstellung_sam_eregnis_kuenstler, log):
    '''
    Adds objMul and objMass columns to ObjDaten
    then trims these
    '''
    linesOmul = objMultiple.split('\n')
    headerOmul = linesOmul.pop(0).split('|')
    linesObm = objMass.split('\n')
    headerObm = linesObm.pop(0).split('|')
    linesO = objDaten_trim_ausstellung_sam_eregnis_kuenstler.split('\n')
    headerO = linesO.pop(0).split('|')
    out = u''  # objDaten_trim_ausstellung_sam_eregnis_kuenstler_Mulmass
    outLog = u''  # used for triming of mul and mass
    outOmul = u''  # objMultiple_trim
    outObm = u''  # objMass_trim
    flog = codecs.open(log, 'w', 'utf-8')  # logfile
    print u"Putting objMultiple and objMass into objDaten..."

    print '\treading ObjMass into dictionary... (yes this takes some time)'
    # ObmId|ObmObjId|ObmTypMasseS|ObmMasseS|ObjAufId|AufAufgabeS
    obmDict = {}
    dcounter = 0  # number of ignored/duplicate ids
    for l in linesObm:
        if len(l) == 0:
            continue
        col = l.split('|')
        obmId = col[0]
        objId = col[1]
        Common.addUniqes(obmDict, objId, obmId, dcounter)
    print '\tobmId:  %d lines, %d uniques, %d dupes' % (len(linesObm), len(obmDict), dcounter)

    print '\treading ObjMultiple into dictionary... (as does this)'
    # OmuId|OmuObjId|OmuTypS|OmuBemerkungM|OmuInhalt01M|ObjInventarNrS|ObjAufId|AufAufgabeS
    omulDict = {}
    dcounter = 0  # number of ignored/duplicate ids
    for l in linesOmul:
        if len(l) == 0:
            continue
        col = l.split('|')
        omulId = col[0]
        objId = col[1]
        Common.addUniqes(omulDict, objId, omulId, dcounter)
    print '\tomulId: %d lines, %d uniques, %d dupes' % (len(linesOmul), len(omulDict), dcounter)

    print '\tadding ObjMul and ObjMass id to objDaten... (and this)'
    # read in photo... and write to new file
    omulUsed = []
    obmUsed = []
    out += u'%s|mulId|massId\n' % '|'.join(headerO)
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        mulId = ''
        massId = ''
        if objId in omulDict.keys():
            omulUsed.append(objId)
            mulId = ';'.join(omulDict[objId])
        if objId in obmDict.keys():
            obmUsed.append(objId)
            massId = ';'.join(obmDict[objId])
        out += u'%s|%s|%s\n' % (l, mulId, massId)
    # make sure nothing is left
    omulUsed = list(set(omulUsed))  # remove dupes
    for objId in omulUsed:
        omulDict.pop(objId)
    if len(omulDict) != 0:
        outLog += u'-----left in omulDict------\n'
        for k, v in omulDict.iteritems():
            outLog += u'%s|%s\n' % (k, ';'.join(v))
    obmUsed = list(set(obmUsed))  # remove dupes
    for objId in obmUsed:
        obmDict.pop(objId)
    if len(obmDict) != 0:
        outLog += u'-----left in obmDict------\n'
        for k, v in obmDict.iteritems():
            outLog += u'%s|%s\n' % (k, ';'.join(v))
    flog.write(outLog)
    flog.close()
    # end of py-Mul-mass-add.py

    # start of py-Mul-mass-trim.py
    linesLog = outLog.split('\n')
    linesLog.pop(0)  # headerLog

    print '\treading log into dictionaries...'
    omulDict = {}
    obmDict = {}
    while len(linesLog) > 0:
        l = linesLog.pop()
        if len(l) == 0:
            continue
        if l.startswith(u'---'):
            break
        col = l.split('|')
        obmDict[col[0]] = col[1].split(';')
    print '\tobmId: %d' % len(obmDict)
    while len(linesLog) > 0:
        l = linesLog.pop()
        if len(l) == 0:
            continue
        if l.startswith(u'---'):
            break
        col = l.split('|')
        omulDict[col[0]] = col[1].split(';')
    print '\tomulId: %d' % len(omulDict)

    print '\twriting trimmed ObjMultiple...'
    outOmul += u'%s\n' % '|'.join(headerOmul)
    for l in linesOmul:
        if len(l) == 0:
            continue
        col = l.split('|')
        omulId = col[0]
        objId = col[1]
        if objId in omulDict.keys():
            if omulId not in omulDict[objId]:
                print 'crap (Omul)'
        else:
            outOmul += u'%s\n' % l

    print '\twriting trimmed ObjMass...'
    outObm += u'%s\n' % '|'.join(headerObm)
    for l in linesObm:
        if len(l) == 0:
            continue
        col = l.split('|')
        obmId = col[0]
        objId = col[1]
        if objId in obmDict.keys():
            if obmId not in obmDict[objId]:
                print 'crap (Obm)'
        else:
            outObm += u'%s\n' % l
    print u"...done"
    return out, outObm, outOmul


def realObjOnly(objDaten_trim_ausstellung_sam_eregnis_kuenstler_mulMass, photo_multimedia_ObjIds_stichID_samesame, objDaten, log):
    '''
    Removes objIds from photo which are not in ObjDaten
    '''
    linesP = photo_multimedia_ObjIds_stichID_samesame.split('\n')
    headerP = linesP.pop(0).split('|')
    linesO = objDaten_trim_ausstellung_sam_eregnis_kuenstler_mulMass.split('\n')
    linesO.pop(0)  # headerO
    linesOld = objDaten.split('\n')
    linesOld.pop(0)  # headerOld
    out = u''  # photo_multimedia_ObjIds_stichID_samesame_real
    flog = codecs.open(log, 'w', 'utf-8')  # logfile
    print u"Removing non-existent objIds..."

    print '\treading in new objId...'
    oList = []
    for l in linesO:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        oList.append(objId)
    oList = list(set(oList))  # removing dupes
    print u'\toList: %d lines, %d uniques' % (len(linesO), len(oList))

    print '\treading in old objId...'
    oldList = []
    for l in linesOld:
        if len(l) == 0:
            continue
        col = l.split('|')
        objId = col[0]
        oldList.append(objId)
    oldList = list(set(oldList))  # removing dupes
    print u'\toldldList: %d lines, %d uniques' % (len(linesOld), len(oldList))

    print '\tremoving unexisting ObjId from photo...'
    once = True
    log = []
    wtflog = []
    out += u'%s\n' % '|'.join(headerP)
    for l in linesP:
        if len(l) == 0:
            continue
        col = l.split('|')
        objIds = col[2].split(';')
        bad = []
        for o in objIds:
            if o not in oList:
                bad.append(o)
                log.append(o)
                if o in oldList:
                    wtflog.append(o)
                    if once:
                        print 'WTFUUUUUUUUUUUUUCCCCKKKKKKK..... %s' % o
                        once = False
        if len(bad) > 0:
            for b in bad:
                objIds.remove(b)
            col[2] = ';'.join(objIds)
            out += u'%s\n' % '|'.join(col)
        else:
            out += u'%s\n' % l
    # deal with log
    print u'\tRAW: removed: %d, wtf\'s: %d' % (len(log), len(wtflog))
    log = list(set(log))  # removing dupes
    wtflog = list(set(wtflog))
    print u'\tUNIQUES: removed: %d, wtf\'s: %d' % (len(log), len(wtflog))
    flog.write(u'----objIds not in objDaten----\n')
    flog.write('%s\n' % '|'.join(log))
    flog.write(u'----WTF (something bad happened)----\n')
    flog.write('%s\n' % '|'.join(wtflog))
    flog.close()
    print u"...done"
    return out


def loadCsv(path, csvFile):
    '''
    Wrapper for quicker loading of csv file
    '''
    return codecs.open(os.path.join(path, csvFile), 'r', 'utf-8').read()


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_crunchCSVDataDirty.py in_path out_path\n' \
        + u'\tin_path (optional): the relative pathname to the csv directory\n' \
        + u'\tout_path (optional):the relative pathname to the target directory\n' \
        + u'\tEither provide both or leave them out ' \
        + u'(thus defaulting to "%s", "%s")' % (CSV_DIR_CLEAN, CSV_DIR_CRUNCH)
    argv = sys.argv[1:]
    if len(argv) == 0:
        crunchFiles()
    elif len(argv) == 2:
        argv[0] = argv[0].decode(sys.getfilesystemencoding())  # str to unicode
        argv[1] = argv[1].decode(sys.getfilesystemencoding())  # str to unicode
        crunchFiles(in_path=argv[0], out_path=argv[1])
    else:
        print usage
# EoF
