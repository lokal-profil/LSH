# -*- coding: UTF-8  -*-
#
# Class contining info for making info templates
#
# mechanism for updating commonsconnections
# mechanism for getting pho_mull from orig filename(+path?)
#
#
import codecs
from common import Common

class MakeInfo:
    flog = codecs.open(u'¤MakeInfo.log', 'w', 'utf-8') #logfile
    skiplist = [] #list for storing e.g. id's between testruns
    #Test suit
    def quicktest(self):
        self.readInLibraries()
        self.readConnections()
        pho_mullList = [(u'52630:205996', u'no objects, other versions of same photo'),
                        (u'90361:191521', u'one object, photographer'),
                        (u'86399:189509', u'event, exhibit, role, mull, mass'),
                        (u'89352:189055', u'weird mass'),
                        (u'87058:189818', u'depicted'),
                        (u'56273:47673', u'related objects, materials'),
                        (u'85130:187720', u'many objects'),
                        (u'9309:208654', u'no filename')]
        for pho_mull in pho_mullList:
            self.flog.write('\n====%s====\n' %pho_mull[1])
            wName, out = self.infoFromPhoto(pho_mull[0])
            if out:
                self.flog.write(out)
                self.flog.flush()
    #
    def exampletest(self):
        self.readInLibraries()
        self.readConnections()
        pho_mullList = [(u'84273:187899', u'Häst'),
                        (u'5078:105807', u'tavla'),
                        (u'220:193815', u'negativ')]
        for pho_mull in pho_mullList:
            self.flog.write('\n====%s====\n' %pho_mull[1])
            wName, out = self.infoFromPhoto(pho_mull[0])
            if out:
                self.flog.write(out)
                self.flog.flush()
    #
    def phoIdtoFileTest(self):
        self.readInLibraries()
        self.readConnections()
        pho_mullList = [(u'84273:187899', u'Häst'),
                        (u'5078:105807', u'tavla'),
                        (u'220:193815', u'negativ')]
        for pho_mull in pho_mullList:
            wName, out = self.infoFromPhoto(pho_mull[0], preview=False, testing=False)
            if out:
                bName = u'%s.txt' %wName[:-4].replace(u' ',u'_')
                f = codecs.open(u'output/%s' %bName, 'w', 'utf-8')
                f.write(out)
                f.close()
                print u'%s outputed to %s' %(pho_mull[0],bName)
            else:
                print u'%s failed to make infopage. See log' %pho_mull[0]
    #
    def catTest(self):
        self.readInLibraries()
        self.readConnections()
        f = codecs.open(u'output/catStats.csv', 'w', 'utf-8')
        f.write(u'#RealCats/MetaCats|cat1;cat2...\n')
        count=0
        for pho_mull in self.photoD.keys():
            count=count+1
            if pho_mull in self.skiplist:
                continue
            wName, out = self.infoFromPhoto(pho_mull, testing=True)
            if out:
                f.write(out+'\n')
            if count%1000==0:
                print count
            self.skiplist.append(pho_mull)
        f.close()
    
    def catTestBatch(self, pho_mull_list, log=None):
        self.readInLibraries()
        self.readConnections()
        if not log:
            log = codecs.open(u'output/catStats2.csv', 'w', 'utf-8')
        log.write(u'#RealCats/MetaCats|cat1;cat2...\n')
        count=0
        for pho_mull in pho_mull_list:
            count=count+1
            if pho_mull in self.skiplist:
                continue
            wName, out = self.infoFromPhoto(pho_mull, testing=True)
            if out:
                log.write(out+'\n')
            if count%1000==0:
                print count
            self.skiplist.append(pho_mull)
    #End of test suite
    
    def readInLibraries(self, verbose=False, careful=False):
        '''reads the given files into dictionaries'''
        
        self.photoD     = Common.file_to_dict(u'deriv-photo_multimedia_ObjIds_stichID_samesame_real_noDupes.csv', idcol=[0,1], verbose=verbose, careful=careful)
        self.stichD     = Common.file_to_dict(u'deriv-Photo_stichwort_trim.csv', verbose=verbose, careful=careful)
        self.massD      = Common.file_to_dict(u'deriv-ObjMass.csv', verbose=verbose, careful=careful)
        self.multiD     = Common.file_to_dict(u'deriv-ObjMultiple.csv', verbose=verbose, careful=careful)
        self.objD       = Common.file_to_dict(u'deriv-ObjDaten-trimmed_Ausstellung_sam_eregnis_kuenstler_MulMass.csv', verbose=verbose, careful=careful)
        self.aussD      = Common.file_to_dict(u'deriv-Ausstellung_trim.csv', verbose=verbose, careful=careful)
        self.ereignisD  = Common.file_to_dict(u'deriv-Ereignis_trim.csv', verbose=verbose, careful=careful)
        self.kuenstlerD = Common.file_to_dict(u'deriv-kuenstler_trim.csv', verbose=verbose, careful=careful)
        self.wikinameD  = Common.file_to_dict(u'deriv-filenames.csv', idcol=[0,1], verbose=verbose, careful=careful)
    #
    def readConnections(self, verbose=False):
        '''reads the commonsconections files into dictionaries'''
        self.stichC = Common.makeConnections(u'connections/commons-Keywords.csv', start=u'[[:Category:', end=u']]', multi=True, verbose=verbose)
        self.placesC = Common.makeConnections(u'connections/commons-Places.csv', addpipe=True, verbose=verbose)
        self.ereignisC = Common.makeConnections(u'connections/commons-Events.csv', start=u'[[:Category:', end=u']]', multi=True, verbose=verbose)
        self.ereignisLinkC = Common.makeConnections(u'connections/commons-Events.csv', useCol=2, start=u'[[', end=u']]', verbose=verbose)
        self.peopleLinkC = Common.makeConnections(u'connections/commons-People.csv', useCol=3, start=u'[[', end=u']]', verbose=verbose)
        self.peopleCreatC = Common.makeConnections(u'connections/commons-People.csv', useCol=4, start=u'[[', end=u']]', verbose=verbose)
        self.peopleCatC = Common.makeConnections(u'connections/commons-People.csv', start=u'[[:Category:', end=u']]', verbose=verbose)
        self.materialC = Common.makeConnections(u'connections/commons-Materials.csv', multi=True, verbose=verbose)
        self.objCatC = Common.makeConnections(u'connections/commons-ObjKeywords.csv', start=u'[[:Category:', end=u']]', multi=True, verbose=verbose)
        MakeInfo.makeRoles(self)
        MakeInfo.makeDimensions(self)
        MakeInfo.makeAbbrevLicense(self)
        MakeInfo.makeAbbrevSource(self)
        MakeInfo.makePhotographers(self)
    #
    def infoFromPhoto(self, pho_mull, preview=True, testing=False):
        phoInfo = self.photoD[pho_mull]
        
        #skip any which don't have a filename
        if not pho_mull in self.wikinameD.keys():
            self.flog.write('No filename: %s\n' %pho_mull)
            return ('No filename: %s\n' %pho_mull, None)
        
        #maintanance categories
        cat_meta = []
        
        #collect info from Photo.csv
        wikiname = self.wikinameD[pho_mull][u'filename']
        origFile = self.wikinameD[pho_mull][u'MulDateiS']
        photo_license = self.lic[phoInfo[u'PhoAufnahmeortS']]
        photo_id = phoInfo[u'PhoId']
        source = self.source[phoInfo[u'PhoSwdS']]
        orig_descr = phoInfo[u'PhoBeschreibungM']
        photographer = u'%s %s' % (phoInfo[u'AdrVorNameS'],phoInfo[u'AdrNameS'])
        photographer, cat_photographer = self.photographers[photographer.strip()]
        #multi-valued columns need to be tested first
        objIds = phoInfo[u'PhoObjId']
        if len(objIds) > 0: objIds = objIds.split(';')
        stichIds = phoInfo[u'PstId']
        if len(stichIds) > 0: stichIds = stichIds.split(';')
        #same_photo= phoInfo[u'same_PhoId']
        #if len(same_photo) > 0: same_photo = same_photo.split(';')
        same_object = phoInfo[u'same_object']
        if len(same_object) > 0: same_object = same_object.split(';')
        
        #category-stichwort
        orig_stich=[]
        cat_stich=[]
        if len(stichIds) > 0:
            for s in stichIds:
                stichKey = self.stichD[s][u'StiBezeichnungS']
                orig_stich.append(stichKey)
                #map to actual category
                if stichKey in self.stichC.keys() and self.stichC[stichKey]:
                    for sc in self.stichC[stichKey]:
                        cat_stich.append(sc)
                elif stichKey in self.stichC.keys(): cat_meta.append(u'unmatched keyword')
        if len(cat_stich) == 0: cat_stich = None
        if len(orig_stich) == 0:
            orig_stich = u''
        else:
            orig_stich = ', '.join(orig_stich)
        
        #objId(s)
        objData= {u'invNr':None,
            u'title':None,
            u'description':None,
            u'date':None,
            u'artist':None,
            u'manufacturer':None,
            u'owner':None,
            u'depicted':None,
            u'death_year':None,
            u'exhibits':None,
            u'orig_event':None,
            u'place':None,
            u'title_orig':None,
            u'title_en':None,
            u'material_tech':None,
            u'signature':None,
            u'dimensions':None,
            u'related':None,
            u'cat_meta':None,
            u'cat_event':None,
            u'cat_artist':None,
            u'cat_depicted':None,
            u'cat_obj':None,
            u'multiple':False}
        # Deal with info from objIds
        if len(objIds) == 0: #do nothing
            cat_meta.append(u'no objects')
        elif len(objIds) == 1:
            #cat_meta.append(u'one object')
            objIds = objIds[0]
            objData = MakeInfo.infoFromObject(self, objIds, objData)
            if objData[u'cat_meta']: cat_meta = cat_meta+objData[u'cat_meta']
        else:
            #cat_meta.append(u'many objects')
            objData[u'multiple'] = True
            manyData = {}
            for o in objIds:
                manyData[o] = MakeInfo.infoFromObject(self, o, {u'invNr':None, u'title':'', u'date':None, u'artist':None, u'cat_artist':None, u'manufacturer':None, u'depicted':None, u'cat_depicted':None})
            objData[u'invNr'] = []; objData[u'date'] = []; objData[u'artist'] = []; objData[u'cat_artist'] = []; objData[u'manufacturer'] = []; objData[u'depicted'] = []; objData[u'cat_depicted'] = []
            for k,v in manyData.iteritems():
                if len(v[u'title'])>0: v[u'title'] = u' - %s' %v[u'title']
                objData[u'invNr'].append(u'{{LSH-link|%s|%s}}%s' %(k, v[u'invNr'], v[u'title']))
                if v[u'date']: objData[u'date'].append(u'%s: %s' %(v[u'invNr'], v[u'date']))
                if v[u'artist']:
                    for a in v[u'artist']: objData[u'artist'].append(u'%s: %s' %(v[u'invNr'], a))
                if v[u'cat_artist']: objData[u'cat_artist'] = objData[u'cat_artist'] + v[u'cat_artist']
                if v[u'manufacturer']:
                    for m in v[u'manufacturer']: objData[u'manufacturer'].append(u'%s: %s' %(v[u'invNr'], m))
                if v[u'depicted']: #note that this is different
                    for d in v[u'depicted']: objData[u'depicted'].append(u'%s: %s' %(v[u'invNr'], d))
                if v[u'cat_depicted']: objData[u'cat_depicted'] = objData[u'cat_depicted'] + v[u'cat_depicted']
        
        #see also
        see_also = u''
        printedPics=[]
        if len(same_object) > 0:
            killist = [] #there is a chance that one of these is one of the filenameless files
            for so in same_object: #there is a chance that this is one of the filenameless files
                if not so in self.wikinameD.keys():
                    killist.append(so)
            for so in killist:
                same_object.remove(so)
            see_also, printedPics = MakeInfo.makeGallery(u'Different images of same object', same_object, self.wikinameD, printed=printedPics, addTo=see_also)
        if objData[u'related']:
            killist = []
            for ro in objData[u'related']:
                if not ro in self.wikinameD.keys():
                    killist.append(ro)
            for ro in killist:
                objData[u'related'].remove(ro)
            see_also, printedPics = MakeInfo.makeGallery(u'Related objects', objData[u'related'], self.wikinameD, has_captions=True, printed=printedPics, addTo=see_also)
            
        #Categories need deduplidication
        categories = u''
        printedCats=[]
        if cat_photographer:
            categories, printedCats = MakeInfo.makeCategory(u'Photographer category', [cat_photographer,], printed=printedCats, addTo=categories)
        if cat_stich:
            categories, printedCats = MakeInfo.makeCategory(u'Photograph categories', cat_stich, printed=printedCats, addTo=categories)
        if objData[u'cat_event']:
            categories, printedCats = MakeInfo.makeCategory(u'Event categories', objData[u'cat_event'], printed=printedCats, addTo=categories)
        if objData[u'cat_artist']:
            categories, printedCats = MakeInfo.makeCategory(u'Artist categories', objData[u'cat_artist'], printed=printedCats, addTo=categories)
        if objData[u'cat_depicted']:
            categories, printedCats = MakeInfo.makeCategory(u'Depicted categories', objData[u'cat_depicted'], printed=printedCats, addTo=categories)
        if objData[u'cat_obj']:
            categories, printedCats = MakeInfo.makeCategory(u'Object categories', objData[u'cat_obj'], printed=printedCats, addTo=categories)
        if len(printedCats)==0: cat_meta.append(u'without any categories')
        if len(cat_meta)>0:
            cat_meta = list(set(cat_meta))
            categories, printedCats = MakeInfo.makeCategory(u'Maintanance categories', cat_meta, pre=u'Media contributed by LSH: ', printed=printedCats, addTo=categories)
        
        if testing:
            catData = u'%r/%r|%s' % (len(printedCats)-len(cat_meta), len(cat_meta), ';'.join(printedCats))
            return (None, catData)
        
        text = MakeInfo.makeTemplate(wikiname, 
                                    origFile, 
                                    photo_license, 
                                    photo_id, 
                                    source, 
                                    orig_descr, 
                                    orig_stich, 
                                    photographer, 
                                    objIds, 
                                    see_also, 
                                    categories, 
                                    objData[u'invNr'],
                                    objData[u'title'],
                                    objData[u'description'],
                                    objData[u'date'],
                                    objData[u'artist'],
                                    objData[u'manufacturer'],
                                    objData[u'owner'],
                                    objData[u'depicted'],
                                    objData[u'death_year'],
                                    objData[u'exhibits'],
                                    objData[u'orig_event'],
                                    objData[u'place'],
                                    objData[u'title_orig'],
                                    objData[u'title_en'],
                                    objData[u'material_tech'],
                                    objData[u'signature'],
                                    objData[u'dimensions'],
                                    objData[u'multiple'],
                                    preview=preview)
        return (wikiname, text)
        
    #
    def infoFromObject(self, objId, data):
        '''returns a dictionary of information based on an objId'''
        objInfo = self.objD[objId]
        cat_meta = []
        
        #collect info from ObjDaten.csv
        source         = self.source[objInfo[u'AufAufgabeS']]
        nyckelord      = objInfo[u'ObjTitelOriginalS'] #titel/nyckelord
        kort           = objInfo[u'ObjTitelWeitereM'] #kortbeskrivning
        invNr          = objInfo[u'ObjInventarNrS']
        group          = objInfo[u'ObjReferenzNrS']
        classification = objInfo[u'ObjSystematikS']
        date           = objInfo[u'ObjDatierungS']
        description    = objInfo[u'ObjReserve01M']
        #multi-valued columns need to be tested first
        exhibits = objInfo[u'ausId']
        if len(exhibits) > 0: exhibits = exhibits.split(';')
        related = objInfo[u'related']
        if len(related) > 0: related = related.split(';')
        events = objInfo[u'ergId']
        if len(events) > 0: events = events.split(';')
        roles = objInfo[u'role:roleCmt:kueId']
        if len(roles) > 0: roles = roles.split(';')
        mulId = objInfo[u'mulId']
        if len(mulId) > 0: mulId = mulId.split(';')
        dimensions = objInfo[u'massId']
        if len(dimensions) > 0: dimensions = dimensions.split(';')
        
        #InvNr. Note that Skokloster boksamling uses kort
        if len(invNr) == 0: invNr = kort
        data[u'invNr'] = u'%s %s' %(source, invNr)
        
        #Title
        if source == u'LRK': data[u'title'] = kort
        else: data[u'title'] = nyckelord
        
        #description
        if len(description) >0: data[u'description'] = description
        
        #datering
        stdDate = Common.stdDate(date)
        if stdDate: date = stdDate
        else: cat_meta.append(u'malformated year')
        data[u'date'] = date
        
        #exhibits
        if len(exhibits)>0:
            data[u'exhibits'] = []
            exhibitD = {}
            counter = 0
            for e in exhibits:
                counter = counter+1
                exName = self.aussD[e][u'AusTitelS']
                exPlace = self.aussD[e][u'AusOrtS']
                exYear = self.aussD[e][u'std_year']
                if exPlace in self.placesC.keys() and self.placesC[exPlace]: exPlace = self.placesC[exPlace]
                elif exPlace in self.placesC.keys(): cat_meta.append(u'unmatched place')
                if len(exYear)>0: out = u'%s (%s) %s' %(exName, exYear, exPlace)
                else:  out = u'%s: %s' %(exName, exPlace)
                exhibitD['%s%r' %(exYear,counter)] = out.strip(u': ')
            for key in sorted(exhibitD.iterkeys()):
                data[u'exhibits'].append(exhibitD[key])     
        
        #events
        if len(events)>0:
            orig_event=[]
            cat_event=[]
            for e in events:
                eventKey = self.ereignisD[e][u'ErgKurztitelS']
                #map to actual category
                if eventKey in self.ereignisC.keys() and self.ereignisC[eventKey]:
                    for ec in self.ereignisC[eventKey]:
                        cat_event.append(ec)
                elif eventKey in self.ereignisC.keys(): cat_meta.append(u'unmatched event')
                if eventKey in self.ereignisLinkC.keys() and self.ereignisLinkC[eventKey]:
                    orig_event.append(u'[[%s|%s]]' %(self.ereignisLinkC[eventKey],eventKey))
                else: orig_event.append(eventKey)
            if len(cat_event) != 0: data[u'cat_event'] = cat_event
            if len(orig_event) != 0: data[u'orig_event'] = orig_event
        
        #ObjMul
        if len(mulId)>0: MakeInfo.multiCruncher(self, mulId, data, cat_meta)
        
        #ObjMass
        if len(dimensions)>0:
            dims = []
            for d in dimensions:
                dType = self.massD[d][u'ObmTypMasseS']
                if not dType in self.massC.keys(): continue #filter on translatable values
                dType = self.massC[dType]
                dValue = self.massD[d][u'ObmMasseS']
                dims.append((dType, dValue))
                #dims.append(u'%s: %s' %(dType, dValue)) # temporary solution
            dims = MakeInfo.dimensionCruncher(self, dims, cat_meta) #takes a list of tuples and returns a list of strings
            if len(dims) >0:
                data[u'dimensions'] = dims
        
        #objcategories from group and classification
        cat_obj=[]
        #group if source == HWY
        if source == u'HWY':
            if len(group)>0:
                if group in self.objCatC.keys() and self.objCatC[group]:
                    for sc in self.objCatC[group]:
                        cat_obj.append(sc)
                elif group in self.objCatC.keys(): cat_meta.append(u'unmatched objKeyword')
        #classifiction for the others
        #note failiure for ord2 keywords containing a comma
        if len(classification)>0:
            if not u'(' in classification:
                if classification in self.objCatC.keys() and self.objCatC[classification]:
                    for sc in self.objCatC[classification]:
                        cat_obj.append(sc)
                elif classification in self.objCatC.keys(): cat_meta.append(u'unmatched objKeyword')
            else:
                parts = classification.split(')')
                for p in parts:
                    if len(p)<2: continue
                    if '(' in p:
                        pos = p.find('(')
                        ord1 = p[:pos].strip(', ')
                        if ord1 in self.objCatC.keys() and self.objCatC[ord1]:
                            for sc in self.objCatC[ord1]:
                                cat_obj.append(sc)
                        elif ord1 in self.objCatC.keys(): cat_meta.append(u'unmatched objKeyword')
                        else:
                            ord2 = p[pos+1:].split(',')
                            ord2 = ord2[len(ord2)-1].strip() #keep only last word
                            if ord2 in self.objCatC.keys() and self.objCatC[ord2]:
                                for sc in self.objCatC[ord2]:
                                    cat_obj.append(sc)
                            elif ord2 in self.objCatC.keys(): cat_meta.append(u'unmatched objKeyword')
        if len(cat_obj) >0: data[u'cat_obj'] = cat_obj
        
        #related
        if len(related)>0:
            relList=[]
            relDict = {}
            for r in related:
                if not r in self.objD.keys(): continue #skip items without uploaded images
                rInvNr  = self.objD[r][u'ObjInventarNrS']
                rSource = self.source[self.objD[r][u'AufAufgabeS']]
                if len(rInvNr) == 0: rInvNr = self.objD[r][u'ObjTitelWeitereM']
                rInvNr = u'%s %s' %(rSource, rInvNr)
                relDict[r] = ['',rInvNr]
            if len(relDict)>0:
                #file assoicated filenames (only use those with an unique objId)
                for r_pho_mull, rPhoto in self.photoD.iteritems():
                    rObjId = rPhoto[u'PhoObjId']
                    if rObjId in relDict.keys():
                        if not r_pho_mull in self.wikinameD.keys(): continue
                        relDict[rObjId] = [r_pho_mull, relDict[rObjId][1]]
                for r, v in relDict.iteritems():
                    if len(v[0]) == 0: continue
                    relList.append(v)
                if len(relList)>0: data[u'related'] = relList
        
        #roles
        artistRoles = [u'Konstnär', u'Upphovsman', u'Författare', u'Kompositör']
        manufacturerRoles =[u'Tillverkare', u'Gravör']
        ownerRoles = [u'Ägare']
        depictedRoles = [u'Avbildning av', u'Avbildning']
        okRoles = artistRoles+manufacturerRoles+ownerRoles+depictedRoles
        badRoleCmts = [u'av kopia']
        artist = []; manufacturer =[]; owner=[]; depicted=[]; cat_artist=[]; cat_depicted=[]
        if len(roles)>0:
            for r in roles:
                role, roleCmt, kueId = r.split(':')
                if roleCmt in badRoleCmts: continue
                if role in okRoles:
                    name = MakeInfo.formatKuenstler(self, kueId, cat_meta, role in (artistRoles+manufacturerRoles))
                    if role in self.rolesC.keys(): name = u'%s: %s' %(self.rolesC[role], name)
                if role in manufacturerRoles: manufacturer.append(name)
                elif role in ownerRoles: owner.append(name)
                elif role in depictedRoles: depicted.append(name)
                elif role in artistRoles: artist.append(name)
                if role in (artistRoles+manufacturerRoles):
                    if kueId in self.peopleCatC.keys() and self.peopleCatC[kueId]:
                        cat_artist.append(self.peopleCatC[kueId])
                if role in depictedRoles:
                    if kueId in self.peopleCatC.keys() and self.peopleCatC[kueId]:
                        cat_depicted.append(self.peopleCatC[kueId])
                if role in artistRoles:     
                    death_year = self.kuenstlerD[kueId][u'KudJahrBisL']
                    if len(death_year) > 0:
                        if data[u'death_year']: death_year = max(data[u'death_year'],int(death_year))
                        data[u'death_year'] = death_year
            if len(manufacturer)>0: data['manufacturer'] = manufacturer
            if len(owner)>0: data['owner'] = owner
            if len(depicted)>0: data['depicted'] = depicted
            if len(artist)>0: data['artist'] = artist
            if len(cat_artist)>0: data['cat_artist'] = cat_artist
            if len(cat_depicted)>0: data['cat_depicted'] = artist
        if len(cat_meta)>0: data[u'cat_meta'] = cat_meta
        return data
    #-----------------------------------------------------------------------------------------------
    def multiCruncher(self, mulId, data, cat_meta):
        tOrt=[]; tLand=[]; title_en=[]; title_orig=[]; material_tech=[]; sign=[]
        mat_techTypes = [u'Material', u'Material och teknik', u'Teknik']
        sigTypes = [u'Signatur/Påskrift', u'Signering', u'Signatur']
        okTypes = [u'Tillverkningsort', u'Tillverkningsland', u'Titel (engelsk)', u'Titel']+sigTypes+mat_techTypes
        for m in mulId:
            typ = self.multiD[m][u'OmuTypS']
            value = self.multiD[m][u'OmuInhalt01M'].strip()
            val_cmt = self.multiD[m][u'OmuBemerkungM'].strip()
            if typ in okTypes and len(value)>0:
                if len(val_cmt)==0 or val_cmt==value: val_cmt=None
                if typ in sigTypes:
                    if val_cmt: value = u'%s [%s]' %(value, val_cmt)
                    sign.append(value)
                elif typ in mat_techTypes:
                    if value in self.materialC.keys() and self.materialC[value]:
                        for sc in self.materialC[value]:
                            value = u'{{technique|%s}}' %sc
                            if val_cmt: value = u'%s (%s)' %(value, val_cmt)
                            material_tech.append(value)
                    elif value in self.materialC.keys(): cat_meta.append(u'unmatched material')
                elif typ == u'Tillverkningsort':
                    if value in self.placesC.keys() and self.placesC[value]: value = self.placesC[value]
                    elif value in self.placesC.keys(): cat_meta.append(u'unmatched place')
                    tOrt.append(value)
                elif typ == u'Tillverkningsland':
                    if value in self.placesC.keys() and self.placesC[value]: value = self.placesC[value]
                    elif value in self.placesC.keys(): cat_meta.append(u'unmatched place')
                    if val_cmt: value = u'%s (%s)' %(value, val_cmt)
                    tLand.append(value)
                elif typ == u'Titel (engelsk)':
                    if value !=data[u'title']:
                        if val_cmt: value = u'%s (%s)' %(value, val_cmt)
                        title_en.append(value)
                elif typ == u'Titel':
                    if value !=data[u'title']:
                        if val_cmt: value = u'%s (%s)' %(value, val_cmt)
                        title_orig.append(value)
        #format and send to relevant field
        #this is were Connection-lookup shold be done add maintanance cat if lookup fails
        if len(sign)>0: data[u'signature'] = sign
        if len(material_tech)>0: data[u'material_tech'] = material_tech
        if len(title_en)>0: data[u'title_en'] = title_en
        if len(title_orig)>0: data[u'title_orig'] = title_orig
        if len(tOrt)>0 and len(tLand)>0:
            data[u'place'] = []
            if len(tOrt) == len(tLand):
                for i in range(0,len(tLand)):
                    place = '%s, %s' %(tOrt[i],tLand[i])
                    data[u'place'].append(place)
            else:
                tOrt = '; '.join(tOrt)
                tLand = '; '.join(tLand)
                data[u'place'].append(u'%s / %s' %(tOrt, tLand))
        elif len(tOrt)>0: data[u'place'] = tOrt
        elif len(tLand)>0: data[u'place'] = tLand
    def dimensionCruncher(self, dims, cat_meta, debug=''):
        '''takes a list of tuples and returns a list of strings'''
        #check if all are simply formatted
        lUnits = [u'm',u'dm', u'cm', u'mm']
        wUnits = [u'g',u'kg']
        returns=[] #list of strings
        types =[]
        prefixes = []
        circas=[]
        nice=True
        units=[]
        nice_dims = []
        for d in dims: # check if formating is "prefix number unit"
            ca=''
            if d[1].endswith(u' c'): #additional possible ending is "c" for circa
                ca ='ca.'
                vals = d[1][:-2].replace('  ', ' ').split(' ')
            else:
                vals = d[1].replace('  ', ' ').split(' ')
            i = len(vals)-2
            if i < 0:
                cat_meta.append(u'dim-without units|%s%s' %(debug, d[0]))
                nice = False
                break
            if not Common.is_number(vals[i].replace(',','.')):
                nice = False
                break
            role, prefix, num, unit = (d[0], ' '.join(vals[:i]), vals[i].replace(',','.'), vals[i+1])
            nice_dims.append([role, prefix, num, unit, ca])
            if role != u'weight':
                units.append(unit)
                prefixes.append(prefix)
                circas.append(ca)
                types.append(role)
        units = list(set(units))
        unique_r = len(list(set(types))) == len(types)
        prefixes = list(set(prefixes))
        circas = list(set(circas))
        if nice and len(units)==1 and unique_r and len(prefixes)<2 and len(circas)==1:
            #well formated and suitable for a single size template
            unit_size=''
            prefix_size=''
            circa_size=''
            size=''
            for d in nice_dims:
                role, prefix, num, unit, ca = d
                if role == u'weight':
                    if not unit in wUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s' %(debug, role, unit))
                    if len(prefix)>0: prefix = u' (%s)' %prefix
                    if len(ca)>0: ca = u'{{circa}} '
                    returns.append(u'%s{{weight|%s|%s}}%s' %(ca, unit, num, prefix))
                else:
                    if not unit in lUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s' %(debug, role, unit))
                    unit_size = unit
                    prefix_size = prefix
                    circa_size= ca
                    size = u'%s|%s=%s' %(size,role,num)
            if len(size)>0:
                if len(prefix_size)>0: prefix_size = u' (%s)' %prefix_size
                if len(circa_size)>0: circa_size = u'{{circa}} '
                returns.append(u'%s{{size|unit=%s%s}}%s' %(circa_size,unit_size, size, prefix_size))
        elif nice:
            #well formated but separate templates needed
            cat_meta.append(u'dim-with multiple size templates')
            for d in nice_dims:
                role, prefix, num, unit, ca = d
                if len(prefix)>0: prefix = u' (%s)' %prefix
                if len(ca)>0: ca = u'{{circa}} '
                if role == u'weight':
                    if not unit in wUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s' %(debug, role, unit))
                    returns.append(u'%s{{weight|%s|%s}}%s' %(ca, unit, num, prefix))
                else:
                    if not unit in lUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s' %(debug, role, unit))
                    returns.append(u'%s{{size|unit=%s|%s=%s}}%s' %(ca, unit, role, num, prefix))
        else: #ill formated
            cat_meta.append(u'dim-with unformated dimensions')
            for d in dims:
                returns.append(u'%s: %s' %(d[0], d[1]))
        return returns
    #create these once - ideally they should query commonspage directly
    def makeAbbrevLicense(self):
        self.lic = {
            u'CC BY-SA':u'CC-BY-SA',
            u'CC0':u'CC0', 
            u'Public Domain':u'PD'
                    }
    def makeAbbrevSource(self):
        '''Last two are for objects'''
        self.source = {
            u'Livrustkammaren':u'LRK',
            u'Skoklosters slott':u'SKO',
            u'Hallwylska museet':u'HWY',
            u'':u'LSH',
            u'LRK dubletter':u'LRK',
            u'Skoklosters slotts boksamling':u'SKO',
                       }
    def makeRoles(self):
        self.rolesC = {
            u'Författare':u'{{Occupation|author}}',
            u'Gravör':u'{{Occupation|engraver}}',
            u'Kompositör':u'{{Occupation|composer}}'
                        }
    def makeDimensions(self):
        self.massC = {
            u'Höjd':u'height',
            u'Bredd':u'width',
            u'Längd':u'length',
            u'Diameter':u'diameter',
            u'Djup':u'depth',
            u'Tjocklek':u'thickness',
            u'Vikt':u'weight',
            u'Vidd':u'width'
                        }
            #bredd should be breath but doesn't seem to exist
            #kanske = [u'kaliber', u'antal', u'Omkrets]
    def makePhotographers(self):
        self.photographers = {
            u'Göran Schmidt':(u'[[Creator:Göran Schmidt|]]',u'Göran Schmidt'),
            u'Samuel Uhrdin':(u'[[Creator:Samuel Uhrdin|]]',u'Samuel Uhrdin'),
            u'Jens Mohr':(u'[[Creator:Jens Mohr|]]',u'Jens Mohr'),
            u'Erik Lernestål':(u'[[Creator:Erik Lernestål|]]',u'Erik Lernestål'),
            u'Matti Östling':(u'[[Creator:Matti Östling|]]',u'Matti Östling'),
            u'Olav Nyhus':(u'[[Creator:Olav Nyhus|]]',u'Olav Nyhus'),
            u'Per Åke Persson':(u'[[Creator:Per Åke Persson|]]',u'Per Åke Persson'),
            u'Madeleine Söder':(u'[[Creator:Madeleine Söder|]]',u'Madeleine Söder'),
            u'Nils Åzelius':(u'Nils Åzelius',None),
            u'Torsten Lenk':(u'Torsten Lenk',None),
            u'Georg Schmidt':(u'Georg Schmidt',None),
            u'Anton Blomberg':(u'Anton Blomberg',None),
            u'':(u'',None)
                             }
    #formating output
    def formatKuenstler(self, kueId, cat_meta, creative=False):
        if creative and kueId in self.peopleCreatC.keys() and self.peopleCreatC[kueId]:
            return u'{{%s}}' %self.peopleCreatC[kueId]
        elif creative and kueId in self.peopleCreatC.keys(): cat_meta.append(u'unmatched creator')
        kuenstler = self.kuenstlerD[kueId]
        name = u'%s %s' %(kuenstler[u'KueVorNameS'], kuenstler[u'KueNameS'])
        if kueId in self.peopleLinkC.keys() and self.peopleLinkC[kueId]:
            return u'[[%s|%s]]' %(self.peopleLinkC[kueId],name.strip())
        bYear = kuenstler[u'KudJahrVonL']
        dYear = kuenstler[u'KudJahrBisL']
        ort   = kuenstler[u'KudOrtS']
        land  = kuenstler[u'KudLandS']
        yrke  = kuenstler[u'KueFunktionS']
        years = ''
        if len(bYear) >0 or len(dYear)>0: years = u'%s-%s' %(bYear, dYear)
        bracket =u'%s, %s' %(yrke, years)
        if len(years) >0 or len(yrke)>0: bracket = u' (%s) ' %bracket.strip(', ')
        place=u'%s%s' %(ort, land)
        if len(ort) >0 and len(land)>0: place = u'%s, %s' %(ort, land)
        out = u'%s%s%s' %(name.strip(), bracket, place.strip())
        return out.strip()
    @staticmethod
    def makeTemplate(wikiname, origFile, photo_license, photo_id, source, orig_descr, 
                    orig_stich, photographer, objIds, see_also, categories, invNr, title, description, date, artist, manufacturer,
                    owner, depicted, death_year, exhibits, orig_event, place, title_orig, title_en, material_tech, signature, dimensions, 
                    multiple, preview=False):
        #event (orig_event)
        #text = u'%s\n' % wikiname
        text = u'{{LSH artwork\n'
        text = text + u'|artist= '
        if artist:
            if len(artist)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(artist)
        else: text = text + u'\n'
        if manufacturer:
            text = text + u'|manufacturer= '
            if len(manufacturer)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(manufacturer)
        text = text + u'|title= '
        if title_orig or title_en:
            titlar = u'{{Title\n'
            if title_orig: titlar = titlar + u'|%s\n' % title_orig[0]
            if title_en: titlar = titlar + u'|en = %s\n' % title_en[0]
            if title: titlar = titlar + u'|sv = %s\n' % title
            text = text + titlar+ u'}}\n'
        elif title: text = text + u'{{Title|%s}}\n' % title
        #if title_orig or title_en:
            #if title_orig: text = text + u'%s\n' % title_orig[0]
            #if title: text = text + u'{{sv|%s}}\n' % title
            #if title_en: text = text + u'{{en|%s}}\n' % title_en[0]
        #elif title: text = text + u'%s\n' % title
        else: text = text + u'\n'
        text = text + u'|description= '
        if depicted:
            if multiple:
                for dep in depicted:
                    invNr = dep[0]
                    depList = dep[1]
                    text = text + MakeInfo.depictedFormater(depicted, invNr=invNr)
            else:
                text = text + MakeInfo.depictedFormater(depicted)
        if description: text = text + u'{{sv|%s}}\n' % description
        else: text = text + u'%s\n' % orig_descr
        text = text + u'|original caption= %s' % orig_descr
        if len(orig_stich)>0:
            text = text + u'<br/>\n\'\'\'Nyckelord\'\'\': %s\n' % orig_stich
        else: text = text + u'\n'
        if orig_event:
            text = text + u'|event= '
            if len(orig_event)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(orig_event)
        text = text + u'|date= '
        if multiple and date: text = text + u'* %s\n' % '\n* '.join(date)
        elif date: text = text + u'%s\n' % date
        else: text = text + u'\n'
        text = text + u'|medium= '
        if material_tech:
            text = text + u'%s\n' % u' - '.join(material_tech)
        else: text = text + u'\n'
        text = text + u'|dimensions= '
        if dimensions:
            if len(dimensions)>1: text = text + u'* '
            text = text + u' %s\n' % '\n* '.join(dimensions)
        else: text = text + u'\n'
        text = text + u'|source= %s\n' % source
        text = text + u'|provenance= '
        if owner:
            if len(owner)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(owner)
        else: text = text + u'\n'
        text = text + u'|exhibition= '
        if exhibits:
            if len(exhibits)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(exhibits)
        else: text = text + u'\n'
        text = text + u'|inscriptions= '
        if signature:
            if len(signature)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(signature)
        else: text = text + u'\n'
        text = text + u'|place of origin= '
        if place:
            if len(place)>1: text = text + u'* '
            text = text + u'%s\n' % '\n* '.join(place)
        else: text = text + u'\n'
        text = text + u'|original filename= %s\n' % origFile
        if multiple:
            text = text + u'|object-multiple= * %s\n' % '\n* '.join(invNr)
        else:
            text = text + u'|object-id= %s\n' % objIds
            text = text + u'|inventory number= %s\n' % invNr
        text = text + u'|photo-id= %s\n' % photo_id
        text = text + u'|photo-license= %s\n' % photo_license
        text = text + u'|photographer= %s\n' % photographer
        text = text + u'|deathyear= '
        if death_year: text = text + u'%s\n' % death_year
        else: text = text + u'\n'
        text = text + u'|other_versions= %s\n' % see_also
        if preview: text = text + u'}}<pre>\n%s</pre>\n' % categories
        else: text = text + u'}}\n%s\n' % categories
        return text.replace(u'<!>',u'<br/>')
    @staticmethod
    def depictedFormater(depicted, invNr=None):
        '''takes a list of people and returns one or more depicted people tempaltes'''
        ending = u'style=plain text'
        if invNr: ending = u'%s|comment=%s' %(ending, invNr)
        if len(depicted)<9:
            return u'{{depicted person|%s|%s}}\n' % ('|'.join(depicted), ending)
        else:
            text = ''
            i=0
            start=True
            for d in depicted:
                if start:
                    text = text + u'{{depicted person|'
                    start=False
                i=i+1
                text = text + u'%s|' % d
                if i%9==0:
                    text = text + u'%s}}\n' %ending
                    start=True
            if not start: text = text + u'%s}}\n' %ending
            return text
    @staticmethod
    def makeGallery(caption, lList, dDict, printed, addTo, col=u'filename', has_captions=False):
        #check for duplicates and escape if all were dupes
        for p in printed:
            if p in lList: lList.remove(p)
        printed = printed+lList
        if len(lList)==0: return addTo, printed
        #output
        text = addTo + u'\n<gallery caption="%s">\n' % caption
        for s in lList:
            if has_captions: text = text + u'File:%s|%s\n' % (dDict[s[0]][col],s[1])
            else: text = text + u'File:%s\n' % dDict[s][col]
        text = text + u'</gallery>'
        return text, printed
    @staticmethod
    def makeCategory(caption, lList, printed, addTo, pre=u''):
        #check for duplicates and escape if all were dupes
        for p in printed:
            if p in lList: lList.remove(p)
        printed = printed+lList
        if len(lList)==0: return addTo, printed
        #output
        text = addTo + u'\n<!--%s-->\n' %caption
        for c in lList:
            text = text + u'[[Category:%s%s]]\n' % (pre, c)
        return text, printed
#
