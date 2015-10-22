#!/usr/bin/python
# -*- coding: UTF-8
#
# Take cleaned csv files to data stage by adding the relevant connections
# in the photo and objDaten file and trimming the files down to only
# what is needed
#
# @ToDo: Stick CSV_FILES in start of file (or somewhere equally easy)
# @ToDo: after redux, store processed output as .json instead
#
import codecs
import os
import helpers
from helpers import MyError

CSV_DIR_CLEAN = u'clean_csv'
CSV_DIR_CRUNCH = u'data'


def run(in_path=CSV_DIR_CLEAN, out_path=CSV_DIR_CRUNCH):
    """
    main process for crunching all of the files
    :param in_path: path to directory containing clean csv files
    :param out_path: path to direcotry in whihc to store output
    """
    # convert to unicode if not the case
    if type(in_path) == str:
        in_path = unicode(in_path)
    if type(out_path) == str:
        out_path = unicode(out_path)

    # create target paths if they doen't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    log_path = os.path.join(out_path, u'logs')
    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    # start crunching
    # combine photo and multi
    photoFile = os.path.join(in_path, u'photo.csv')
    multiFile = os.path.join(in_path, u'multimedia.csv')
    logFile = os.path.join(log_path, u'photo_multimedia.log')
    tmpFile = os.path.join(out_path, u'tmp.csv')
    photo_multi = makePhoto_multi(photoFile, multiFile, logFile, tmpFile)

    # combine photo and Photo-ObjDaten
    # populates the objId field in photo_multi with ALL of the RELEVANT
    # ObjIds and
    # removes unused Objects from objDaten to make it smaller
    photoObjDatenFile = os.path.join(in_path, u'photoObjDaten.csv')
    objDatenFile = os.path.join(in_path, u'objDaten.csv')
    logFile = os.path.join(log_path, u'photo_objDaten.log')
    objDaten = photo_ObjDaten(photo_multi, photoObjDatenFile,
                              objDatenFile, logFile)

    # Adds the stichwort id field to photo and
    # removes unused entries from stichworth to make it smaller
    stichFile = os.path.join(in_path, u'stichwort.csv')
    stichwort = stichworth_photo(stichFile, photo_multi)

    # Add two fields to photo_multi:
    # * same photoId-different file
    # * same objId-different photoID
    samesame(photo_multi)

    # Adds the Ausstellung_id field to ObjDaten and
    # trims Ausstellung to unique ids
    ausstellungFile = os.path.join(in_path, u'ausstellung.csv')
    ausstellung = ausstellung_objDaten(ausstellungFile, objDaten)

    # Adds ObjDaten-samhörande field to ObjDaten
    objDatenSamFile = os.path.join(in_path, u'objDatenSam.csv')
    objDaten_sam(objDatenSamFile, objDaten)

    # Adds the Eregnis field to ObjDaten and
    # trims Eregnis to unique ids
    ereignisFile = os.path.join(in_path, u'ereignis.csv')
    logFile = os.path.join(log_path, u'ereignis.log')
    ereignis = ereignis_objDaten(ereignisFile, objDaten, logFile)

    # Adds the kuenstler field to ObjDaten and
    # trims kuenstler
    kuenstlerFile = os.path.join(in_path, u'kuenstler.csv')
    logFile = os.path.join(log_path, u'kuenstler.log')
    kuenstler = kuenstler_objDaten(kuenstlerFile, objDaten, logFile)

    # Adds objMul and objMass fields to ObjDaten
    # then trimms objMul and objMass
    objMassFile = os.path.join(in_path, u'objMass.csv')
    objMultipleFile = os.path.join(in_path, u'objMultiple.csv')
    objMass, objMultiple = mulMass_add(objMassFile, objMultipleFile, objDaten)

    # output all the above
    # @toDO: simplify names (once downstream is checked)
    out_csv = {
        u'photo_multimedia_etc': photo_multi,
        u'stichwort_trim': stichwort,
        u'objMass_trim': objMass,
        u'objMultiple_trim': objMultiple,
        u'objDaten_etc': objDaten,
        u'ausstellung_trim': ausstellung,
        u'ereignis_trim': ereignis,
        u'kuenstler_trim': kuenstler
    }
    # @toDO: Not needed once downstream reads json
    out_headers = {
        u'photo_multimedia_etc':
            'PhoId|MulId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|PhoSwdS|'
            'AdrVorNameS|AdrNameS|PhoSystematikS|MulPfadS|MulDateiS|'
            'MulExtentS|PstId|same_PhoId|same_object',
        u'stichwort_trim':
            'PstId|PhoId|StiBezeichnungS|StiSynonymS',
        u'objMass_trim':
            'ObmId|ObmObjId|ObmTypMasseS|ObmMasseS|ObjAufId|AufAufgabeS',
        u'objMultiple_trim':
            'OmuId|OmuObjId|OmuTypS|OmuBemerkungM|OmuInhalt01M|ObjInventarNrS|'
            'ObjAufId|AufAufgabeS',
        u'objDaten_etc':
            'ObjId|ObjKueId|AufId|AufAufgabeS|ObjTitelOriginalS|'
            'ObjTitelWeitereM|ObjInventarNrS|ObjInventarNrSortiertS|'
            'ObjReferenzNrS|ObjDatierungS|ObjJahrVonL|ObjJahrBisL|'
            'ObjSystematikS|ObjFeld01M|ObjFeld02M|ObjFeld03M|ObjFeld06M|'
            'ObjReserve01M|ausId|related|ergId|role:roleCmt:kueId|mulId|'
            'massId',
        u'ausstellung_trim':
            'AusId|AusTitelS|AusOrtS|std_year|AusJahrS|AusDatumVonD|'
            'AusDatumBisD|AufAufgabeS|AobObjId',
        u'ereignis_trim':
            'ErgId|ErgKurztitelS|ErgArtS|EroObjId',
        u'kuenstler_trim':
            'KueId|KueVorNameS|KueNameS|KudDatierungS|KudJahrVonL|KudJahrBisL|'
            'KudOrtS|KudLandS|KueFunktionS|ObjId'
    }
    for k, v in out_csv.iteritems():
        outFile = os.path.join(out_path, u'%s.csv' % k)
        helpers.dictToCsvFile(outFile, v, out_headers[k])
        print u'\tOutputted %s' % outFile
    print u'Done!'


def makePhoto_multi(photoFile, multiFile, logFile, tmpFile):
    """
    Given the photo and multimedia data this combines the two into one dict
    :param photoFile: path to photo data file
    :param multiFile: path to multimedia data file
    :param logFile: path to logfile
    :param tmpFile: path to temporary file
    :return: dict
    """
    # setup
    flog = codecs.open(logFile, 'w', 'utf-8')  # logfile
    print u"Combining photo and multimedia file for unique files..."
    pathToTrim = u'R:\web\hires\\'
    tmpHeader = 'PhoId|MulId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|' \
                'PhoSwdS|AdrVorNameS|AdrNameS|PhoSystematikS|MulPfadS|' \
                'MulDateiS|MulExtentS'

    # handle multimedia
    multiHeader = 'MulId|MulPhoId|MulPfadS|MulDateiS|MulExtentS'
    multi = helpers.csvFileToDict(multiFile, 'MulId', multiHeader)

    # check that filename is unique
    flog.write('*Same files used by different PhoId, format is PhoId/MulId\n')
    namelist = []
    mulPhoIdList = []
    for k, v in multi.iteritems():
        name = u'%s\\%s.%s' % (v['MulPfadS'], v['MulDateiS'], v['MulExtentS'])
        if name in namelist:
            flog.write('%s/%s\n' % (v['MulPhoId'], v['MullId']))
        else:
            mulPhoIdList.append(v['MulPhoId'])
            namelist.append(name)
    print u'\tmultimedia: %d' % len(multi)

    # handle photo
    # @toDO add duplicate check to cleanup script
    photoHeader = 'PhoId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|PhoSwdS|' \
                  'MulId|AdrVorNameS|AdrNameS|PhoSystematikS'
    photo = helpers.csvFileToDict(photoFile, 'PhoId', photoHeader)
    print u'\tphoto: %d' % len(photo)

    # combine
    combined = {}
    flog.write(u'* unused rows in multimedia\n')
    for k, v in multi.iteritems():
        phoId = v['MulPhoId']
        mulId = v['MulId']
        v['MulPfadS'] = v['MulPfadS'].replace(pathToTrim, u'')  # trim filepath
        v['MulExtentS'] = u''  # MulExtentS is always wrong
        if phoId not in photo.keys():
            flog.write(u'%s\n' % v)
        elif not photo[phoId]['MulId'] == v['MulId']:
            raise MyError("phoId matched but to wrong mulId: p:%s m_found:%s, "
                          "m_expected %s" % (phoId, photo[phoId]['MulId'],
                                             mulId))
        else:
            del v['MulPhoId'], v['MulId']
            combo = photo.pop(phoId)  # move out of photo
            combo.update(v)  # add contents from multi
            combined[phoId] = combo

    # log any unused rows in photo
    flog.write(u'* unused rows in photo\n')
    for k, v in photo.iteritems():
        flog.write(u'%s\n' % v)
    flog.close()
    print u"...done"

    # check if anything needs to be manually handled
    print u"Read the log (%s)" % logFile
    combined = helpers.promptManualUpdate(combined, tmpFile,
                                          tmpHeader, 'PhoId')

    return combined


def photo_ObjDaten(photo_multi, photoObjDatenFile, objDatenFile, logFile):
    """
    Given the photo_multi data and the phoObjDaten + objDaten data files
    any additional relevant ObjIds are added to the PhoObjId field of the
    photo_multi dict, this field is also converted to a list.
    Also returns objDaten for later use
    :param photo_multi: photo_multi dict
    :param photoObjDatenFile: path to phoObjDaten data file
    :param objDatenFile: path to objDaten data file
    :param logFile: path to logfile
    :return: dict (and updates photo_multi)
    """
    # setup
    flog = codecs.open(logFile, 'w', 'utf-8')  # logfile
    print u"Combining all ObjId into the photo file..."

    # handle objDaten
    print u'\treading in objDaten.. (takes a while)'
    objDatenHeader = 'ObjId|ObjKueId|AufId|AufAufgabeS|ObjTitelOriginalS|' \
                     'ObjTitelWeitereM|ObjInventarNrS|ObjInventarNrSortiertS|' \
                     'ObjReferenzNrS|ObjDatierungS|ObjJahrVonL|ObjJahrBisL|' \
                     'ObjSystematikS|ObjFeld01M|ObjFeld02M|ObjFeld03M|' \
                     'ObjFeld06M|ObjReserve01M'
    objDaten = helpers.csvFileToDict(objDatenFile, 'ObjId', objDatenHeader)

    # match each objInvNr to several objId
    objInvNr2ObjId = {}  # old oDict
    print u'\tfinding objInvNr connections...'
    for k, v in objDaten.iteritems():
        objId = v['ObjId']
        objInvNr = v['ObjInventarNrS']
        if len(objInvNr) == 0:
            continue
        if objInvNr not in objInvNr2ObjId.keys():
            objInvNr2ObjId[objInvNr] = []
        objInvNr2ObjId[objInvNr].append(objId)
    print '\tFound %d objInvNr connections in %d objects' % \
          (len(objInvNr2ObjId), len(objDaten))

    # handle photoObjDaten
    photoObjDatenHeader = 'PhmId|AufId|AufAufgabeS|MulId|PhoId|ObjInvNrS'
    photoObjDaten = helpers.csvFileToDict(photoObjDatenFile,
                                          'PhmId',
                                          photoObjDatenHeader,
                                          keep=('PhoId', 'ObjInvNrS'))

    # match each phoId to several objId via the ObjInvNr
    print u'\tfinding photo-object connections...'
    photoObjConnections = {}
    skipped = []  # ObjInvNr not in ObjDaten
    for k, v in photoObjDaten.iteritems():
        objInvNr = v['ObjInvNrS']
        phoId = v['PhoId']
        if len(objInvNr) == 0:
            continue
        if objInvNr not in objInvNr2ObjId.keys():
            skipped.append(objInvNr)
            continue
        if phoId not in photoObjConnections.keys():
            photoObjConnections[phoId] = []
        photoObjConnections[phoId] += objInvNr2ObjId[objInvNr]
    print '\tFound %d connected photos in %d photoObjDaten entries' % \
          (len(photoObjConnections), len(photoObjDaten))

    # add to photo_multi
    allBadObjId = []
    for phoId, v in photo_multi.iteritems():
        objIds = []
        if phoId not in photoObjConnections.keys():
            if len(v['PhoObjId']) > 0:
                objIds.append(v['PhoObjId'])
        else:
            # combine relevant objIds
            objIds = photoObjConnections.pop(phoId)  # new connections
            if len(v['PhoObjId']) > 0:
                objIds.append(v['PhoObjId'])  # old connection
            objIds = list(set(objIds))  # remove dupes

        # check that all of these actually exists (old realObjOnly())
        # and remove otherwise
        badObjId = []
        for objId in objIds:
            if objId not in objDaten.keys():
                badObjId.append(objId)
        if len(badObjId) > 0:
            allBadObjId += badObjId
            for badId in badObjId:
                objIds.remove(badId)

        # set new value
        v['PhoObjId'] = objIds

    # log any skipped ObjInvNr
    if len(skipped) != 0:
        skipped = list(set(skipped))  # remove dupes
        print u"\tthere were %d skipped ObjInvNr, see log (%s)" % \
            (len(skipped), logFile)
        flog.write(u'*Unknown objInvs, i.e. ObjInvNrS in photoObjDaten '
                   u'without a match in ObjDaten\n')
        flog.write(u'%s\n' % ', '.join(skipped))

    # log any bad objId
    if len(allBadObjId) != 0:
        print '\tI found some bad objIds. Check the %s' % logFile
        allBadObjId = list(set(allBadObjId))  # remove dupes
        flog.write(u'* objIds in photo but not in objDaten\n')
        flog.write(u'%s\n' % ', '.join(allBadObjId))

    # trim objDaten
    trimObjDaten(objDaten, photo_multi)

    # confirm and return
    print u"...done"
    flog.close()
    return objDaten


def trimObjDaten(objDaten, photo_multi):
    """
    Removes any unused objects in objDaten, because it is huge!
    :param objDaten: objDaten dict
    :param photo_multi: photo_multi dict
    :return: None
    """
    print u"\tTrimming objDaten..."
    originalSize = len(objDaten)

    # collect all objIds not mentioned in photo_multi
    unusedObjIds = set(objDaten.keys())
    for k, v in photo_multi.iteritems():
        unusedObjIds = unusedObjIds - set(v['PhoObjId'])

    # remove any which should be trimmed
    for objId in unusedObjIds:
        del objDaten[objId]

    print '\tobjDaten reduced from: %d to %d' % (originalSize, len(objDaten))


def stichworth_photo(stichwortFile, photo_multi):
    """
    Given the photo-multi data and the stichwort data file add a stichwort id
    field to photo-multi.
    Also returns the stichwort data after trimming away any unused info
    :param stichwortFile: path to stichwort data file
    :param photo_multi: photo_multi dict
    :return: dict (and updates photo_multi)
    """
    # setup
    print u"Adding stichworth to photo"

    # handle stichwort
    print u'\treading in stichwort...'
    stichwortHeader = 'PstId|PhoId|StiBezeichnungS|StiSynonymS'
    stichwort = helpers.csvFileToDict(stichwortFile, 'PstId', stichwortHeader)
    originalSize = len(stichwort)

    # match each phoId to several stichId
    # removing any entries with invalid phoIds
    photoStichConnection = {}
    for k, v in stichwort.items():
        phoId = v['PhoId']
        pstId = v['PstId']
        if phoId in photo_multi.keys():
            if phoId not in photoStichConnection.keys():
                photoStichConnection[phoId] = set([])
            photoStichConnection[phoId].add(pstId)
        else:
            del stichwort[k]
    print '\tstichwort trimmed from %d to %d, found %d phoId' % \
          (originalSize, len(stichwort), len(photoStichConnection))

    # add stichId to photo_multi
    for k, v in photo_multi.iteritems():
        phoId = v['PhoId']
        v['PstId'] = []
        if phoId in photoStichConnection.keys():
            v['PstId'] = list(photoStichConnection.pop(phoId))

    # confirm and return
    print u"...done"
    return stichwort


def samesame(photo_multi):
    """
    @toDo (after redux)
        * samePhoId no longer needed (but need to make sure it is not
          expected later since removing changes order)
        * base on photo_all + photo_multi to get connections to old
    Adds two fields to the photo_multi dict
    * same_PhoId: same phoId different file
    * same_object: same objId different phoId
    :param photo_multi: photo_multi dict
    :return: None (but updates photo_multi)
    """
    print u"Samesame()"
    objIdConnection = {}
    for k, v in photo_multi.iteritems():
        phoId = v['PhoId']
        mullId = v['MulId']
        phoMullId = '%s:%s' % (phoId, mullId)
        objIds = v['PhoObjId']
        for objId in objIds:
            if objId not in objIdConnection.keys():
                objIdConnection[objId] = []
            objIdConnection[objId].append((phoId, phoMullId))

    # remove any with only one associated phoId
    # this way ( i.e. .items() allows deletions to be made directly and
    # is safe (per https://stackoverflow.com/questions/5384914)
    for k, v in objIdConnection.items():
        if len(v) < 2:
            del objIdConnection[k]
    print u'\tfound %d objects in multiple photos' % len(objIdConnection)

    # invert objIdConnection to get per phoId connection
    print '\tinverting objIdConnection...'
    phoIdConnection = {}
    for objId, v in objIdConnection.iteritems():
        allPhoMull = [entry[1] for entry in v]
        for phoId, phoMullId in v:
            if phoId not in phoIdConnection.keys():
                phoIdConnection[phoId] = []
            phoIdConnection[phoId] += allPhoMull

    print '\tadding samesame to photo...'
    for k, v in photo_multi.iteritems():
        v['same_PhoId'] = ''  # @toDo remove once safe
        v['same_object'] = []
        phoId = v['PhoId']
        mullId = v['MulId']
        phoMullId = '%s:%s' % (phoId, mullId)
        if phoId in phoIdConnection.keys():
            ll = list(set(phoIdConnection[phoId]))  # clone and remove dupes
            ll.remove(phoMullId)  # remove self
            v['same_object'] = ll

    print u"...done"


def ausstellung_objDaten(austellungFile, objDaten):
    """
    Given the austellung data file and the objDaten data add a austellung id
    field to objDaten.
    Also returns the austellung data after
    * adding a std_year field
    * combining all objIds for the same ausId
    * dropping AobId
    :param austellungFile: path to austellung data file
    :param objDaten: objDaten dict
    :return: dict (and updates objDaten)
    """
    # often requires manual fixing prior to crunch
    print u"Confirm that any year formatting issues mentioned in the analysis " \
          u"log have been corrected and the updated ausstellung file saved..."
    raw_input(u"...by pressing enter when done")

    # setup
    dummyTitles = (
        u'reparation', u'utställning', u'lån för undersökning',
        u'OBS! Testpost för admin - utställning, export wikimedia commons',
        u'lån till Frankrike 1947', u'test karin 20100520',
        u'test 20100629 (en post skapad för administrativa tester)',
        u'tennföremål 8 st till Strömsholm', u'utlån f justering av urverk')
    print u"Trimming ausstellung and adding ausstellung to ObjDaten..."

    # handle ausstellung
    austellungHeader = 'AobId|AusId|AusTitelS|AusOrtS|AusJahrS|AusDatumVonD|' \
                       'AusDatumBisD|AobObjId|AufAufgabeS'
    austellung = helpers.csvFileToDict(austellungFile, 'AobId',
                                       austellungHeader)
    originalSize = len(austellung)

    # collect all ausId and drop any with invalid title
    # @toDO: Is keeping objId in austellung really needed?
    #        Otherwise populate objIdConnection here
    foundAusId = {}
    for k, v in austellung.items():  # allow removing entries from within loop
        ausId = v['AusId']
        objId = v['AobObjId']
        title = v['AusTitelS']
        if len(title) == 0 or title in dummyTitles:  # remove empty/dummy
            del austellung[k]
        elif ausId not in foundAusId:  # keep this entry
            foundAusId[ausId] = k
            austellung[k]['AobObjId'] = set([objId, ])
            austellung[k].pop('AobId')  # drop unnecessary id
        else:  # keep only objId part of this entry
            austellung[foundAusId[ausId]]['AobObjId'].add(objId)
            del austellung[k]
    print '\taustellung reduced from %d to %d entries' % \
          (originalSize, len(austellung))

    # populate std_year
    print '\tstandardising years...'
    for k, v in austellung.iteritems():
        year = v['AusJahrS']
        yfrom = v['AusDatumVonD'].replace(u' 00:00:00', u'').strip()
        ytil = v['AusDatumBisD'].replace(u' 00:00:00', u'').strip()
        v['std_year'] = stdAustellungYear(year, yfrom, ytil)
        # to match with pre-redux results. Could possibly be dropped instead?
        v['AusDatumVonD'] = yfrom
        v['AusDatumBisD'] = ytil

    # invert to get per objId connections
    # and convert set to list
    objIdConnection = {}
    for k, v in austellung.iteritems():
        ausId = v['AusId']
        objIds = v['AobObjId']
        v['AobObjId'] = list(objIds)
        for objId in objIds:
            if objId not in objIdConnection.keys():
                objIdConnection[objId] = []
            objIdConnection[objId].append(ausId)

    print '\tadding ausId to objDaten...'
    for k, v in objDaten.iteritems():
        objId = v['ObjId']
        v['ausId'] = []
        if objId in objIdConnection.keys():
            v['ausId'] = objIdConnection.pop(objId)

    print u"...done"
    return austellung


def stdAustellungYear(year, yfrom, ytil):
    """
    Given the three year fields in austellung this returns a standardised
    year in either YYYY or YYYY-YYYY format.
    Assumes all errors part from y1 and y7 (in py-Ausstellung) have been fixed
    @toDO: redo, but in collaboration with better analysis
    :param year: AusJahrS value
    :param yfrom: AusDatumVonD value
    :param ytil: AusDatumBisD value
    :return: str
    """
    # quick sanity check on year
    if len(year.strip('0123456789 -')) != 0:
        return year

    #
    lenYear = len(year)
    lenYfrom = len(yfrom)
    lenYtil = len(ytil)
    if lenYear == 9:  # YYYY-YYYY
        return '%d-%d' % (int(year[:4]), int(year[5:]))
    elif lenYear == 7:  # YYYY-YY
        return '%d-%d%d' % (int(year[:4]), int(year[:2]), int(year[5:]))
    elif lenYear == 4:  # YYYY
        if lenYfrom != 0 and int(yfrom[:4]) != int(year):
            # yfrom takes precedence over year
            year = int(yfrom[:4])
        if lenYtil != 0 and int(ytil[:4]) != int(year):
            return '%d-%d' % (int(year), int(ytil[:4]))
        else:
            return '%d' % int(year)
    elif lenYear == 0:
        if lenYfrom != 0 and lenYtil != 0:
            if int(yfrom[:4]) == int(ytil[:4]):
                return '%d' % int(yfrom[:4])
            else:
                return '%d-%d' % (int(yfrom[:4]), int(ytil[:4]))
        elif lenYfrom != 0:
            return '%d' % int(yfrom[:4])
        else:
            return ''
    else:  # weird year
        return year


def objDaten_sam(objDatenSamFile, objDaten):
    """
    Adds objDatenSam field to ObjDaten
    * adding a std_year field
    * combining all objIds for the same ausId
    * dropping AobId
    :param objDatenSamFile: path to ObjDaten-samhörande data file
    :param objDaten: objDaten dict
    :return: None (but updates objDaten)
    """
    # setup
    print u"Adding ObjDaten-samhörande to ObjDaten"

    # handle objDatenSam
    print '\treading ObjDaten_-_samhörande_nr into dictionary... (slow)'
    objDatenSamHeader = 'OobId|OobObj1ID|OobObj2ID'
    objDatenSam = helpers.csvFileToDict(objDatenSamFile, 'OobId',
                                        objDatenSamHeader)

    # map object connections
    print '\tmapping object connections...'
    objIdConnection = {}
    for k, v in objDatenSam.iteritems():
        objId1 = v['OobObj1ID']
        objId2 = v['OobObj2ID']
        if objId1 not in objIdConnection.keys():
            objIdConnection[objId1] = []
        if objId2 not in objIdConnection.keys():
            objIdConnection[objId2] = []
        objIdConnection[objId1].append(objId2)
        objIdConnection[objId2].append(objId1)
    print '\tfound %d connected objIds in %d entries' % \
          (len(objIdConnection), len(objDatenSam))

    # clean up connections
    print '\tremoving dupes, invalids and self...'
    for objId, connectedIds in objIdConnection.items():
        connectedIds = list(set(connectedIds))  # remove dupe
        if objId in connectedIds:
            connectedIds.remove(objId)  # remove self
        for conId in connectedIds[:]:  # slice allows changes from within loop
            if conId not in objDaten.keys():
                connectedIds.remove(conId)  # remove invalid

        # delete or update
        if len(connectedIds) == 0:
            del objIdConnection[objId]
        else:
            objIdConnection[objId] = connectedIds

    # add to objDaten
    print '\tadding connections to objDaten...'
    for k, v in objDaten.iteritems():
        objId = v['ObjId']
        v['related'] = []
        if objId in objIdConnection.keys():
            v['related'] = objIdConnection.pop(objId)

    print u"...done"


def ereignis_objDaten(ereignisFile, objDaten, logFile):
    """
    Given the ereignis data file and the objDaten data add a ereignis id
    field to objDaten.
    Also returns the ereignis data after
    * combining all objIds for the same ergId
    * dropping EroId
    :param ereignisFile: path to eregnis data file
    :param objDaten: objDaten dict
    :param logFile: path to logfile
    :return: dict (and updates objDaten)
    """
    # setup
    flog = codecs.open(logFile, 'w', 'utf-8')  # logfile
    print u"Trimming eregnis and adding eregnis to ObjDaten..."

    # handle eregnis
    ereignisHeader = 'EroId|ErgId|EroObjId|ErgKurztitelS|ErgArtS'
    ereignis = helpers.csvFileToDict(ereignisFile, 'EroId', ereignisHeader)
    originalSize = len(ereignis)

    # collect all ergId and drop any with invalid title
    # @toDO: Is keeping objId in eregnis really needed?
    #        Otherwise populate objIdConnection here
    foundErgId = {}
    for k, v in ereignis.items():  # allow removing entries from within loop
        ergId = v['ErgId']
        objId = v['EroObjId']
        title = v['ErgKurztitelS']
        if len(title) == 0:  # remove empty
            del ereignis[k]
        elif ergId not in foundErgId.keys():  # keep this entry
            foundErgId[ergId] = k
            ereignis[k]['EroObjId'] = set([objId, ])
            ereignis[k].pop('EroId')  # drop unnecessary id
        else:  # keep only objId part of this entry
            ereignis[foundErgId[ergId]]['EroObjId'].add(objId)
            del ereignis[k]
    print '\tergIds: reduced from %d to %d' % (originalSize, len(ereignis))

    # handle urls in ereignis and convert set to list
    for k, v in ereignis.iteritems():
        objIds = v['EroObjId']
        url = v['ErgArtS']

        # convert set to list
        v['EroObjId'] = list(objIds)

        # handle urls
        if u'%' in url:
            url = helpers.urldecodeUTF8(url)
        # convert external links to internal
        if 'wikipedia' in url:
            url = helpers.external2internalLink(url)
        elif len(url) > 0:
            flog.write(u'weird url: %s\n' % url)
        v['ErgArtS'] = url

    # invert to get per objId connections
    objIdConnection = {}
    for k, v in ereignis.iteritems():
        ergId = v['ErgId']
        objIds = v['EroObjId']
        for objId in objIds:
            if objId not in objIdConnection.keys():
                objIdConnection[objId] = []
            objIdConnection[objId].append(ergId)

    # add to objDaten
    print '\tadding ergId to objDaten...'
    for k, v in objDaten.iteritems():
        objId = v['ObjId']
        v['ergId'] = []
        if objId in objIdConnection.keys():
            v['ergId'] = objIdConnection.pop(objId)

    flog.close()
    print u"...done"
    return ereignis


def kuenstler_objDaten(kuenstlerFile, objDaten, logFile):
    """
    Given the kuenstler data file and the objDaten data add a kuenstler id
    field to objDaten.
    Also returns the kuenstler data after
    * removing certain irrelevant roles and dummy entries
    * combining all objIds for the same kueId
    * standardising years
    * dropping a lot of unneeded fields
    :param kuenstlerFile: path to kuenstler data file
    :param objDaten: objDaten dict
    :param logFile: path to logfile
    :return: dict (and updates objDaten)
    """
    # setup
    flog = codecs.open(logFile, 'w', 'utf-8')  # logfile
    print u"Crunching kuenstler..."
    dummyNames = (u'ingen uppgift', )
    badRoles = (u'Leverantör', u'Auktion', u'Förmedlare', u'Givare',
                u'Återförsäljare', u'Konservator')
    badRoleCmts = (u'Förpaktare, kontrollör', u'av kopia')
    droppedFields = ('OkuId', 'ObjAufId', 'AufAufgabeS', 'OkuArtS',
                     'OkuFunktionS', 'OkuValidierungS', 'KudArtS', 'MulId',
                     'PhoId')

    # handle kuenstler
    kuenstlerHeader = 'OkuId|ObjId|ObjAufId|AufAufgabeS|KueId|KueVorNameS|' \
                      'KueNameS|OkuArtS|OkuFunktionS|OkuValidierungS|KudArtS|' \
                      'KudDatierungS|KudJahrVonL|KudJahrBisL|KudOrtS|KudLandS|' \
                      'KueFunktionS|MulId|PhoId'
    kuenstler = helpers.csvFileToDict(kuenstlerFile, ('OkuId', 'MulId'),
                                      kuenstlerHeader)
    originalSize = len(kuenstler)

    # collect all kueId and drop any with invalid title or role
    # also invert to get per objId connections
    # @toDO: Is keeping objId in kuenstler really needed?
    #        Otherwise populate objIdConnection here
    foundKueId = {}
    objIdConnection = {}
    for k, v in kuenstler.items():  # allow removing entries from within loop
        kueId = v['KueId']
        objId = v['ObjId']
        fName = v['KueVorNameS']
        lName = v['KueNameS']
        role = v['OkuArtS']
        roleCmt = v['OkuFunktionS']

        # filter out any undesired entries
        if role in badRoles or \
                roleCmt in badRoleCmts or \
                len(fName) + len(lName) == 0 or \
                lName in dummyNames:
            del kuenstler[k]
            continue

        # send unique role/kueId combo for objid
        kueCombo = u'%s:%s:%s' % (role, roleCmt, kueId)
        if objId not in objIdConnection.keys():
            objIdConnection[objId] = set([])
        objIdConnection[objId].add(kueCombo)

        # keep only one entry per unique kueId
        if kueId not in foundKueId.keys():  # keep this entry
            foundKueId[kueId] = k
            kuenstler[k]['ObjId'] = set([objId, ])
        else:  # keep only objId part of this entry
            kuenstler[foundKueId[kueId]]['ObjId'].add(objId)
            del kuenstler[k]
    print '\tkueIds: reduced from %d to %d' % (originalSize, len(kuenstler))

    # add to objDaten
    print '\tadding kueId to objDaten...'
    for k, v in objDaten.iteritems():
        objId = v['ObjId']
        v['role:roleCmt:kueId'] = []
        if objId in objIdConnection.keys():
            v['role:roleCmt:kueId'] = list(objIdConnection.pop(objId))

    # further cleanup of kuenstler
    # correcting ort/land entries
    # stripping years from name
    # dropping a bunch of fields
    print '\tfurther cleanup of kuenstler...'
    for k, v in kuenstler.iteritems():
        land = v['KudOrtS']  # missnamed in original database
        ort = v['KudLandS']  # missnamed in original database
        lName = v['KueNameS']
        bYear = v['KudJahrVonL']
        dYear = v['KudJahrBisL']
        objIds = v['ObjId']

        # correct missnaming in original database
        v['KudOrtS'] = ort
        v['KudLandS'] = land

        # convert set to list
        v['ObjId'] = list(objIds)

        # take yearinfo out of name, and store in year
        lName, bYear, dYear, log = extractKuenstlerYear(lName, bYear, dYear)
        if len(log) > 0:
            flog.write(log)
        v['KueNameS'] = lName
        v['KudJahrVonL'] = bYear
        v['KudJahrBisL'] = dYear

        for field in droppedFields:
            del v[field]

    flog.close()
    print u"...done"
    return kuenstler


def extractKuenstlerYear(name, bYear, dYear):
    """
    Checks for the presence of years at the end of a name,
    if found these are stripped after comparison to birth/death years.
    If birth/death years are not known then the found values are returned
    :param name: the string to test
    :param bYear: the known birth year
    :param dYear: the known death year
    :return: str, str, str, str
    """
    log = ''
    testYears = None
    testName = None
    if name.endswith(')'):
        test = name.split('(')[-1][:-1]
        if ',' in test:  # (title, YYYY-YYYY)
            parts = test.split(',')
            testYears = parts[-1].split('-')
            testName = '('.join(name.split('(')[:-1])
            testName += u'(%s)' % ','.join(parts[:-1])
        else:  # (YYYY-YYYY)
            testYears = test.split('-')
            testName = '('.join(name.split('(')[:-1])
    elif helpers.is_int(name[-len('YYYY'):]):  # YYYY-YYYY
        test = name[-len('YYYY-YYYY'):]
        testYears = test.split('-')
        testName = name[:-len('YYYY-YYYY')]

    # found potential matches
    if testYears:
        for i in range(len(testYears)):
            testYears[i] = testYears[i].strip('*+ ')  # (*YYYY-YYYY+)
        if len(testYears) == 2 and \
                all(len(testY) == 0 or helpers.is_int(testY)
                    for testY in testYears):
            # YYYY-YYYY
            if len(bYear) > 0 and bYear != testYears[0]:
                log += u'bYear: %s,\t%s != %s\n' % (name, testYears[0], bYear)
            if len(dYear) > 0 and dYear != testYears[1]:
                log += u'dYear: %s,\t%s != %s\n' % (name, testYears[1], dYear)
            if len(log) == 0:
                name = testName.strip().rstrip(',')
                bYear = testYears[0]
                dYear = testYears[1]

    return name, bYear, dYear, log


def mulMass_add(objMassFile, objMultipleFile, objDaten):
    """
    Given the objMass and the objMultiple data file and the objDaten data
    add an objMass and an objMultiple field to objDaten.
    Also returns the objMass and objMultiple data after
    * removing any entries where objId not in objDaten
    :param objMassFile: path to objMass data file
    :param objMultipleFile: path to objMultiple data file
    :param objDaten: objDaten dict
    :return: dict, dict (and updates objDaten)
    """
    # setup
    print u"Putting objMultiple and objMass into objDaten..."

    # handle objMass
    print '\treading ObjMass into dictionary... (yes this takes some time)'
    objMassHeader = 'ObmId|ObmObjId|ObmTypMasseS|ObmMasseS|' \
                    'ObjAufId|AufAufgabeS'
    objMass = helpers.csvFileToDict(objMassFile, 'ObmId', objMassHeader)
    originalSize = len(objMass)

    # invert to get per objId connections
    # and remove any entries where objId not in objDaten
    print '\tinverting objMass...'
    objIdMassConnection = {}
    for k, v in objMass.items():
        obmId = v['ObmId']
        objId = v['ObmObjId']
        if objId not in objDaten.keys():
            del objMass[k]
            continue
        if objId not in objIdMassConnection.keys():
            objIdMassConnection[objId] = set([])
        objIdMassConnection[objId].add(obmId)
    print '\tobjMass: reduced from %d to %d' % (originalSize, len(objMass))

    # handle objMultiple
    print '\treading ObjMultiple into dictionary... (as does this)'
    objMultipleHeader = 'OmuId|OmuObjId|OmuTypS|OmuBemerkungM|OmuInhalt01M|' \
                        'ObjInventarNrS|ObjAufId|AufAufgabeS'
    objMultiple = helpers.csvFileToDict(objMultipleFile, 'OmuId',
                                        objMultipleHeader)
    originalSize = len(objMultiple)

    # invert to get per objId connections
    # and remove any entries where objId not in objDaten
    print '\tinverting objIdMultiple...'
    objIdMultipleConnection = {}
    for k, v in objMultiple.items():
        omulId = v['OmuId']
        objId = v['OmuObjId']
        if objId not in objDaten.keys():
            del objMultiple[k]
            continue
        if objId not in objIdMultipleConnection.keys():
            objIdMultipleConnection[objId] = set([])
        objIdMultipleConnection[objId].add(omulId)
    print '\tobjMultiple: reduced from %d to %d' % (originalSize,
                                                    len(objMultiple))

    # adding ObjMul and ObjMass id to objDaten
    print '\tadding ObjMul and ObjMass id to objDaten... (and this)'
    for k, v in objDaten.iteritems():
        objId = v['ObjId']
        v['massId'] = []
        v['mulId'] = []
        if objId in objIdMassConnection.keys():
            v['massId'] = list(objIdMassConnection.pop(objId))
        if objId in objIdMultipleConnection.keys():
            v['mulId'] = list(objIdMultipleConnection.pop(objId))

    print u"...done"
    return objMass, objMultiple


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_crunchCSVDataDirty.py in_path out_path\n' \
        + u'\tin_path (optional): the relative pathname to the csv directory\n' \
        + u'\tout_path (optional):the relative pathname to the target directory\n' \
        + u'\tEither provide both or leave them out ' \
        + u'(thus defaulting to "%s", "%s")' % (CSV_DIR_CLEAN, CSV_DIR_CRUNCH)
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 2:
        argv[0] = helpers.convertFromCommandline(argv[0])
        argv[1] = helpers.convertFromCommandline(argv[1])
        run(in_path=argv[0], out_path=argv[1])
    else:
        print usage
# EoF
