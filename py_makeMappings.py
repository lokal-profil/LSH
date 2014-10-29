#!/usr/bin/python
# -*- coding: UTF-8
#
# Produces mapping tables by getting frequency from new files and
# reusing previous mappings.
# Final output is a file for Commons
#
# Includes the following old files:
# * py-tmp.py
# * py-tmp3.py
# * py-Photo_stichworth.py
# * py-photo.py (partially)
# * py-Ausstellung.py (partially)
# * py-Ereignis.py
#
# If PhoSystematikS is introduced in photo then search thorugh comments
# to see where editing is needed
#
from py_MakeInfo import MakeInfo
from py_prepCSVData import CSV_FILES  # so as to be able to reference these in output
import codecs
import os

# roller som inte tas med i People
ROLE_BLACKLIST = [u'Säljare', u'Auktion', u'Förmedlare', u'Givare', u'Återförsäljare', u'Konservator']
IN_PATH = u'old_connections'
OUT_PATH = u'mappings'


def run(in_path=IN_PATH, out_path=OUT_PATH):
    # Load all relevant files
    A = MakeInfo()
    A.readInLibraries()
    A.readConnections(keepskip=True, folder=in_path)

    # Create a dict of depicted ObjId with frequency as value
    # Would have to concider PhoSystematikS if present
    oDict = {}
    for k, v in A.photoD.iteritems():
        objIds = v[u'PhoObjId']
        if len(objIds) > 0:
            objIds = objIds.split(';')
            for o in objIds:
                if o in oDict.keys():
                    oDict[o] = oDict[o]+1
                else:
                    oDict[o] = 1

    # create new mapping
    landDict, ortDict, techDict = makePlaceAndMaterial(A, oDict)  # ObjMultiple
    ord1Dict, ord2Dict, gruppDict = makeObjKeywords(A, oDict)  #
    keywords = makeKeywords(A)  # Stichworth
    photographers = makePhotographers(A)  # photo
    exhibitPlaces = makeExhibitPlaces(A, oDict)  # Ausstelung
    events = makeEvents(A, oDict)  # Ereignis
    people = makePeople(A, oDict)  # Kuenstler

    # combine with data from old mapping
    # need to handle unused mappings separately
    techDict = simpleCombine(A.materialC, techDict, addEmpty=True)
    landDict = simpleCombine(A.placesC, landDict)
    ortDict = simpleCombine(A.placesC, ortDict)
    exhibitPlaces = simpleCombine(A.placesC, exhibitPlaces)
    ord1Dict = simpleCombine(A.objCatC, ord1Dict)
    ord2Dict = simpleCombine(A.objCatC, ord2Dict)
    gruppDict = simpleCombine(A.objCatC, gruppDict)
    keywords = combineKeywords(A.stichC, keywords)
    photographers = combinePhotographers(A.photographers, photographers)  # TODO:Change once externalised
    events = combineEvents(A.ereignisC, A.ereignisLinkC, events)
    people = combinePeople(A.peopleLinkC, A.peopleCreatC, A.peopleCatC, people)

    # the following are needed to preserve old but unused mappings
    emptyPlaces = simpleEmpty(A.placesC, [landDict, ortDict, exhibitPlaces])
    emptyObjCats = simpleEmpty(A.objCatC, [ord1Dict, ord2Dict, gruppDict])

    # output
    # needes to be adapted to sort by 'freq' value and deal with more complex
    # needs to consider categories/link formats etc. Needs to consider multi valued
    # put 'freq==0' under a new heading

    # create target if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    # several dicts per file
    # Places
    f = codecs.open(u'%s/Places.txt' % out_path, 'w', 'utf8')
    intro = u'<!--From: %s - col: ausOrt-->\n' % CSV_FILES[u'ausstellung'] \
          + u'<!--From: %s for OmuTypS = Tillverkningsland -->\n' % CSV_FILES[u'objMultiple'] \
          + u'<!--From: %s for OmuTypS = Tillverkningsort-->\n' % CSV_FILES[u'objMultiple'] \
          + u'Set commonsconnection of irrelevant places to "-"\n\n' \
          + u'===Place|Frequency|Commonsconnection===\n'
    f.write(intro)
    f.write(u'\n====exhibit places====\n')
    simpleWrite(f, exhibitPlaces, label=u'name=Place|other=Commons connection')
    f.write(u'\n====origin-Countries====\n')
    simpleWrite(f, landDict, label=u'name=Place|other=Commons connection')
    f.write(u'\n====origin-cities====\n')
    simpleWrite(f, ortDict, label=u'name=Place|other=Commons connection')
    f.write(u'\n====Preserved mappings====\n')
    simpleWrite(f, emptyPlaces, label=u'name=Place|other=Commons connection')
    f.close()
    print u'Created %s/Places.txt' % out_path
    # ObjKeywords
    f = codecs.open(u'%s/ObjKeywords.txt' % out_path, 'w', 'utf8')
    intro = u'<!--From: %s -->\n' % CSV_FILES[u'objDaten'] \
          + u'These are the keywords used to describe the objects ' \
          + u'themselves. Classification is used for all items whereas ' \
          + u'group is only used at HWY.\n\n' \
          + u'when possible ord1 will be used instead of the more ' \
          + u'generic ord2.\n\n' \
          + u'Multile categores are separated by a "/"\n' \
          + u'===Keyword|frequency|commonscategory===\n'
    f.write(intro)
    f.write(u'\n====class: ord1====\n')
    simpleWrite(f, ord1Dict, label=u'category=', other_tag=u'category')
    f.write(u'\n====class: ord2====\n')
    simpleWrite(f, ord2Dict, label=u'category=', other_tag=u'category')
    f.write(u'\n====class: HWY-grupp====\n')
    simpleWrite(f, gruppDict, label=u'category=', other_tag=u'category')
    f.write(u'\n====Preserved mappings====\n')
    simpleWrite(f, emptyObjCats, label=u'category=', other_tag=u'category')
    f.close()
    print u'Created %s/ObjKeywords.txt' % out_path
    # one dict per file
    writeMaterials(u'%s/Materials.txt' % out_path, techDict)  # Materials
    writeKeywords(u'%s/Keywords.txt' % out_path, keywords)  # Keywords
    writeEvents(u'%s/Events.txt' % out_path, events)  # Events
    writePeople(u'%s/People.txt' % out_path, people)  # People
    writePhotographers(u'%s/Photographers.txt' % out_path, people)  # Photographers


def makePlaceAndMaterial(A, oDict):
    '''
    Populate mapping-tables for Places-land / Places-ort / Materials
    Analysis of objMultiple
    '''
    landDict = {}
    ortDict = {}
    techDict = {}
    mat_techTypes = [u'Material', u'Material och teknik', u'Teknik']
    ortType = u'Tillverkningsort'
    landType = u'Tillverkningsland'
    for k, v in oDict.iteritems():
        mul = A.objD[k][u'mulId']
        if len(mul) > 0:
            mul = mul.split(';')
            for m in mul:
                typ = A.multiD[m][u'OmuTypS']
                value = A.multiD[m][u'OmuInhalt01M']
                # val_cmt = A.multiD[m][u'OmuBemerkungM']
                if len(value) == 0:
                    continue
                elif typ in mat_techTypes:
                    if value in techDict.keys():
                        techDict[value] = techDict[value]+v
                    else:
                        techDict[value] = v
                elif typ in landType:
                    if value in landDict.keys():
                        landDict[value] = landDict[value]+v
                    else:
                        landDict[value] = v
                elif typ in ortType:
                    if value in ortDict.keys():
                        ortDict[value] = ortDict[value]+v
                    else:
                        ortDict[value] = v
    # print len(landDict), len(ortDict), len(techDict)
    return landDict, ortDict, techDict


def writeMaterials(filename, dDict):
    '''
    output materials in Commons format
    '''
    # set-up
    header = u'{{user:Lokal Profil/LSH2|name=Technique/material|technique=}}\n'
    row = u'{{User:Lokal Profil/LSH3\n' \
        + u'|name      = %s\n' \
        + u'|frequency = %d\n' \
        + u'|technique = %s\n' \
        + u'}}\n'
    footer = u'|}\n'
    intro = u'<!--From: %s -->\n' % CSV_FILES[u'objMultiple'] \
          + u'commonsconnection is the relevant parameter for ' \
          + u'{{tl|technique}}. Don\'t forget to add a translation in ' \
          + u'Swedish at [[Template:Technique/sv]]\n\n' \
          + u'Set commonsconnection of irrelevant technique/material ' \
          + u'to "-".\n\n' \
          + u'===technique/material|frequency|commonsconnection===\n'
    # output
    once = True
    f = codecs.open(filename, 'w', 'utf8')
    f.write(intro)
    f.write(header)
    for key, val in sortedBy(dDict):
        if once and val[u'freq'] == 0:
            once = False
            f.write(footer)
            f.write(u'\n===Preserved mappings===\n')
            f.write(header)
        f.write(row % (key, val[u'freq'], val[u'connect']))
    f.write(footer)
    f.close()
    print u'Created %s' % filename


def makeObjKeywords(A, oDict):
    '''
    Populate mapping-tables for ObjKeywords
    Analysis of classification
    '''
    ord1Dict = {}
    ord2Dict = {}
    gruppDict = {}
    for k, v in oDict.iteritems():
        classification = A.objD[k][u'ObjSystematikS']
        grupp = A.objD[k][u'ObjReferenzNrS']
        if len(grupp) > 1:
            if grupp in gruppDict.keys():
                gruppDict[grupp] = gruppDict[grupp]+1
            else:
                gruppDict[grupp] = 1
        # ord1 OR ord1 (ord2, ord3) OR ord1.1 (ord2.1, ord3.1), ord1.2 (ord2.2, ord3.2)
        if len(classification) > 0:
            if u'(' not in classification:
                if classification in ord1Dict.keys():
                    ord1Dict[classification] = ord1Dict[classification]+1
                else:
                    ord1Dict[classification] = 1
                # parts = classification.split(',')
                # for p in parts:
                #   if p in ord1Dict.keys(): ord1Dict[p] = ord1Dict[p]+1
                #   else: ord1Dict[p] = 1
            else:
                delar = classification.split(')')
                for d in delar:
                    if len(d) < 2:
                        continue
                    if '(' in d:
                        pos = d.find('(')
                        ord1 = d[:pos].strip(', ')
                        ord2s = d[pos+1:].split(',')
                        ord2 = ord2s[len(ord2s)-1].strip()  # keep only last word
                        if ord1 in ord1Dict.keys():
                            ord1Dict[ord1] = ord1Dict[ord1]+1
                        else:
                            ord1Dict[ord1] = 1
                        if ord2 in ord2Dict.keys():
                            ord2Dict[ord2] = ord2Dict[ord2]+1
                        else:
                            ord2Dict[ord2] = 1
    # print len(ord1Dict), len(ord2Dict), len(gruppDict)
    return ord1Dict, ord2Dict, gruppDict


def makePhotographers(A):
    '''
    Populate mapping-tables for Photographers
    Analysis of photo
    '''
    photographers = {}
    for k, v in A.photoD.iteritems():
        art = u'%s %s' % (v[u'AdrVorNameS'], v[u'AdrNameS'])
        if art in photographers.keys():
            photographers[art] += 1
        elif art.strip() != u'':
            photographers[art] = 1
    return photographers


def combinePhotographers(oldDict, newDict):
    '''
    Enrich mapping by previously done mapping
    newDict has freq parameter
    oldDict has name: (creator, category)
    TODO: check that this still works once Photographers are externalised
    '''
    comboDict = {}
    # add made mappings to new frequencies
    for k, v in newDict.iteritems():
        comboDict[k] = {u'freq': v, u'creator': u'', u'category': u''}
        if k in oldDict.keys():
            creator, category = oldDict[k]
            if creator is not None:
                comboDict[k][u'creator'] = creator
            if category is not None:
                comboDict[k][u'category'] = category
            del oldDict[k]
    # add any previous mapping
    for k, v in oldDict.iteritems():
        creator, category = oldDict[k]
        if creator is not None or category is not None:
            if creator is None:
                creator = u''
            if category is None:
                category = u''
            newDict[k] = {u'freq': 0, u'creator': creator, u'category': category}
    return comboDict


def writePhotographers(filename, dDict):
    '''
    output photographers in Commons format
    '''
    # set-up
    header = u'{{user:Lokal Profil/LSH2|name=Photographer|creator=|category=}}\n'
    row = u'{{User:Lokal Profil/LSH3\n' \
        + u'|name      = %s\n' \
        + u'|frequency = %d\n' \
        + u'|creator   = %s\n' \
        + u'|category  = %s\n' \
        + u'}}\n'
    footer = u'|}\n'
    intro = u'<!--From: %s -->\n\n' % CSV_FILES[u'photo']
    # output
    once = True
    f = codecs.open(filename, 'w', 'utf8')
    f.write(intro)
    f.write(header)
    for key, val in sortedBy(dDict):
        if once and val[u'freq'] == 0:
            once = False
            f.write(footer)
            f.write(u'\n===Preserved mappings===\n')
            f.write(header)
        f.write(row % (key, val[u'freq'], val[u'creator'], val[u'cat']))
    f.write(footer)
    f.close()
    print u'Created %s' % filename


def makeKeywords(A):
    '''
    Populate mapping-tables for Keywords
    Analysis of stichwords
    '''
    # Create a dict of depicted StichId with frequency as value
    # Working from the trimmed file means each phoId has already been
    # verified to exist. If PhoSystematikS is present then building trim
    # would have to concider this.
    keywords = {}
    phoIds = []  # to make sure all phoIds really are present
    for k, v in A.stichD.iteritems():
        descr = v[u'StiSynonymS']
        key = v[u'StiBezeichnungS']
        if descr == u'':
            descr = u'-'
        if key not in keywords.keys():
            keywords[key] = {u'descr': [], u'freq': 0}
        if descr not in keywords[key][u'descr']:
            keywords[key][u'descr'].append(descr)
        keywords[key][u'freq'] += 1
        # for debugging
        if v[u'PhoId'] not in phoIds:
            phoIds.append(v[u'PhoId'])
    # debug
    for k in A.photoD.keys():
        k = k.split(':')[0]
        if k in phoIds:
            phoIds.remove(k)
    if len(phoIds) != 0:
        print u'Stichwort_trim still contains unused phoIds'
    return keywords


def combineKeywords(oldDict, newDict):
    '''
    Enrich mapping by previously done mapping
    newDict has freq and descr parameters
    oldDict has None or list of categories
    '''
    # add made mappings to new frequencies
    for k, v in newDict.iteritems():
        newDict[k][u'cat'] = u''
        if k in oldDict.keys():
            if oldDict[k] is not None:
                newDict[k][u'cat'] = oldDict[k]
            del oldDict[k]

    # add any previous mapping
    for k, v in oldDict.iteritems():
        if v is not None:
            newDict[k] = {u'freq': 0, u'cat': v, u'descr': u'-'}

    return newDict


def writeKeywords(filename, dDict):
    '''
    output keywords in Commons format
    '''
    # set-up
    header = u'{{user:Lokal Profil/LSH2|category=}}\n'
    row = u'{{User:Lokal Profil/LSH3\n' \
        + u'|name      = %s\n' \
        + u'|more      = %s\n' \
        + u'|frequency = %d\n' \
        + u'|category  = %s\n' \
        + u'}}\n'
    footer = u'|}\n'
    intro = u'<!--From: %s -->\n' % CSV_FILES[u'stichwort'] \
          + u'Set commonsconnection of irrelevant keywords to "-"\n\n' \
          + u'Multiple categories are separated by "/"\n' \
          + u'===Keyword|frequency|description|commonsconnection===\n'
    # output
    once = True
    f = codecs.open(filename, 'w', 'utf8')
    f.write(intro)
    f.write(header)
    for key, val in sortedBy(dDict):
        if once and val[u'freq'] == 0:
            once = False
            f.write(footer)
            f.write(u'\n===Preserved mappings===\n')
            f.write(header)
        f.write(row % (key, val[u'descr'], val[u'freq'], '/'.join(val[u'cat'])))
    f.write(footer)
    f.close()
    print u'Created %s' % filename


def makeExhibitPlaces(A, oDict):
    '''
    Populate mapping-tables for Exhibit places
    Analysis of Austellung
    '''
    # oDict gives frequency of each objId
    # A.objD[k][u'ausId'] gives the exhibit id(s) of each object
    # A.aussD[k][u'AusOrtS'] gives the place

    # get frequency for each exhibit
    exhibits = {}
    for k, v in oDict.iteritems():
        ausIds = A.objD[k][u'ausId']
        if len(ausIds) != 0:
            ausIds = ausIds.split(';')
            for a in ausIds:
                if a in exhibits.keys():
                    exhibits[a] += v
                else:
                    exhibits[a] = v

    # get frequency for each place
    places = {}
    for k, v in exhibits.iteritems():
        place = A.aussD[k][u'AusOrtS']
        if place in places.keys():
            places[place] += v
        else:
            places[place] = v
    return places


def makeEvents(A, oDict):
    '''
    Populate mapping-tables for Events
    Analysis of Ereignis
    '''
    # oDict gives frequency of each objId
    # A.objD[k][u'ergId'] gives the exhibit id(s) of each object
    # A.ereignisD[k][u'ErgKurztitelS'] gives the title
    # A.ereignisD[k][u'ErgArtS'] gives the wikilink

    # get frequency for each exhibit
    eventFreq = {}
    for k, v in oDict.iteritems():
        ergIds = A.objD[k][u'ergId']
        if len(ergIds) != 0:
            ergIds = ergIds.split(';')
            for e in ergIds:
                if e in eventFreq.keys():
                    eventFreq[e] += v
                else:
                    eventFreq[e] = v

    # get frequency for each place
    events = {}
    for k, v in eventFreq.iteritems():
        title = A.ereignisD[k][u'ErgKurztitelS']
        link = A.ereignisD[k][u'ErgArtS']
        if title in events.keys():
            events[title][u'freq'] += v
            if link != events[title][u'link']:
                print u'Found two events with title but different links %s' % k
        else:
            events[title] = {u'link': link, u'freq': v}
    return events


def combineEvents(oldCatDict, oldLinkDict, newDict):
    '''
    Enrich mapping by previously done mapping
    newDict has freq and link parameters
    oldDict is split into
    oldCatDict list of categories
    oldLinkDict a link written ":sv:A link"
    Note that link can exist both in new and old but new uses "sv:A_link"
    '''
    for k, v in newDict.iteritems():
        newDict[k][u'cat'] = u''
        if k in oldCatDict.keys():  # assume key list is same in both
            if oldCatDict[k] is not None:
                newDict[k][u'cat'] = oldCatDict[k]
            if oldLinkDict[k] is not None:
                link = oldLinkDict[k][1:].replace(' ', '_')
                if link != newDict[k][u'link']:
                    # check if the same, otherwise use old
                    if len(newDict[k][u'link']) != 0:
                        print u'Eregnis: replaced %s by %s' % (newDict[k][u'link'], link)
                    newDict[k][u'link'] = link
            del oldCatDict[k]  # no need to delete oldLinkDict if we iterate over cat

    # add any previous mapping
    for k, v in oldCatDict.iteritems():
        cat = v
        link = oldLinkDict[k]
        if cat is not None or link is not None:
            if cat is None:
                cat = u''
            if link is None:
                link = u''
            newDict[k] = {u'freq': 0, u'cat': cat, u'link': link}

    return newDict


def writeEvents(filename, dDict):
    '''
    output events in Commons format
    '''
    # set-up
    header = u'{{user:Lokal Profil/LSH2|name=Event|link=Wikipedia-link|category=}}\n'
    row = u'{{User:Lokal Profil/LSH3\n' \
        + u'|name      = %s\n' \
        + u'|frequency = %d\n' \
        + u'|link      = %s\n' \
        + u'|category  = %s\n' \
        + u'}}\n'
    footer = u'|}\n'
    intro = u'<!--From: %s -->' % CSV_FILES[u'ereignis'] \
          + u'\'\'wikipedia-link\'\' are used for descriptive texts ' \
          + u'whereas \'\'commonsconnection\'\' is a relevant category ' \
          + u'on commons.\n\n' \
          + u'Set commonsconnection of irrelevant events to "-"\n\n' \
          + u'Multiple categories are separated by "/"\n\n' \
          + u'*död/begravning: [[:Category:Funeral of X of Sweden]]\n' \
          + u'*kröning: [[:Category:Coronation of X of Sweden]]\n' \
          + u'*bröllop: [[:Category:Wedding of X and Y of Sweden]]\n' \
          + u'===Event|Frequency|wikipedia-link|Commonsconnection===\n'
    # output
    once = True
    f = codecs.open(filename, 'w', 'utf8')
    f.write(intro)
    f.write(header)
    for key, val in sortedBy(dDict):
        if once and val[u'freq'] == 0:
            once = False
            f.write(footer)
            f.write(u'\n===Preserved mappings===\n')
            f.write(header)
        f.write(row % (key, val[u'freq'], val[u'link'], '/'.join(val[u'cat'])))
    f.write(footer)
    f.close()
    print u'Created %s' % filename


def makePeople(A, oDict):
    '''
    Populate mapping-tables for People
    Analysis of Kuenstler
    '''
    # oDict gives frequency of each objId
    # A.objD[k][u'role:roleCmt:kueId'] gives the id(s) of each object
    # Here we need to do some filtering on roles
    # A.kuenstlerD[k] gives the info
    roleBlacklist = ROLE_BLACKLIST

    # get frequency and role for each person
    personFreq = {}
    for k, v in oDict.iteritems():
        personIds = A.objD[k][u'role:roleCmt:kueId']
        if len(personIds) != 0:
            personIds = personIds.split(u';')
            for p in personIds:
                role, roleCmt, kueId = p.split(u':')
                if role not in roleBlacklist:
                    if kueId in personFreq.keys():
                        personFreq[kueId] += v
                    else:
                        personFreq[kueId] = v

    # get info for each person
    people = {}
    for k, v in personFreq.iteritems():
        # construct a description
        # name (job, years) place
        info = {u'fName': A.kuenstlerD[k][u'KueVorNameS'],
                u'lName': A.kuenstlerD[k][u'KueNameS'],
                u'birth': A.kuenstlerD[k][u'KudJahrVonL'],
                u'death': A.kuenstlerD[k][u'KudJahrBisL'],
                u'land': A.kuenstlerD[k][u'KudLandS'],
                u'place': A.kuenstlerD[k][u'KudOrtS'],
                u'job': A.kuenstlerD[k][u'KueFunktionS']
                }
        name = (u'%s %s' % (info[u'fName'], info[u'lName'])).strip()
        dates = u'%s-%s' % (info[u'birth'], info[u'death'])
        if dates == u'-':
            dates = u''
        place = (u'%s, %s' % (info[u'place'], info[u'land'])).strip(u' ,')
        dateJob = (u'%s, %s' % (info[u'job'], dates)).strip(u' ,')
        if len(dateJob) > 0:
            dateJob = u'(%s) ' % dateJob
        descr = (u'%s %s%s' % (name, dateJob, place)).strip()
        people[k] = {u'freq': v, u'descr': descr}
    return people


def combinePeople(oldLink, oldCreat, oldCat, newDict):
    '''
    Enrich mapping by previously done mapping
    newDict has freq and descr parameters
    oldDict is split into
    oldCat a category
    oldLink a link written ":sv:A link"
    oldCreat a creator template
    Note that link can exist bot in new and old but new uses "sv:A_link"
    '''
    for k, v in newDict.iteritems():
        newDict[k].update({u'cat': u'', u'creator': u'', u'link': u''})
        if k in oldLink.keys():  # assume key list is same in both
            if oldLink[k] is not None:
                newDict[k][u'link'] = oldLink[k]
            if oldCreat[k] is not None:
                newDict[k][u'creator'] = oldCreat[k]
            if oldCat[k] is not None:
                newDict[k][u'cat'] = oldCat[k]
            del oldLink[k]

    # add any previous mapping
    for k, v in oldLink.iteritems():
        link = v
        cat = oldCat[k]
        creator = oldCreat[k]
        if cat is not None or link is not None or creator is not None:
            if cat is None:
                cat = u''
            if link is None:
                link = u''
            if creator is None:
                creator = u''
            newDict[k] = {u'freq': 0,
                          u'descr': u'',
                          u'cat': cat,
                          u'link': link,
                          u'creator': creator
                          }
    return newDict


def writePeople(filename, dDict):
    '''
    output People in Commons format
    '''
    # set-up
    header = u'{{user:Lokal Profil/LSH2|name=Name <small>(kueId)</small>' \
           + u'|link=Wikipedia-link|creator=|category=}}\n'
    row = u'{{User:Lokal Profil/LSH3\n' \
        + u'|name      = %s\n' \
        + u'|more      = %s\n' \
        + u'|frequency = %d\n' \
        + u'|link      = %s\n' \
        + u'|creator   = %s\n' \
        + u'|category  = %s\n' \
        + u'}}\n'
    footer = u'|}\n'
    intro = u'<!--From: %s -->\n' % CSV_FILES[u'kuenstler'] \
          + u'\'\'wikipedia-link\'\' is used for descriptive texts whereas ' \
          + u'creator is a creator template on commons and ' \
          + u'\'\'commoncat\'\' is a relevant category on commons.\n\n' \
          + u'Set commonsconnection of irrelevant events to "-". ' \
          + u'Note that creator is only relevant for artists.\n\n' \
          + u'===kueId|frequency|name|wikipedia-link|creator|commoncat===\n'
    # output
    once = True
    f = codecs.open(filename, 'w', 'utf8')
    f.write(intro)
    f.write(header)
    for key, val in sortedBy(dDict):
        if once and val[u'freq'] == 0:
            once = False
            f.write(footer)
            f.write(u'\n===Preserved mappings===\n')
            f.write(header)
        f.write(row % (key, val[u'descr'], val[u'freq'], val[u'link'], val[u'creator'], val[u'cat']))
    f.write(footer)
    f.close()
    print u'Created %s' % filename


def simpleCombine(oldDict, newDict, addEmpty=False):
    '''
    Enrich mapping by previously done mapping
    simple connection files (word|frequency|connection) are dicts where
    the value is either the connection or None (for either blank or -)
    Previously made mappings are retained even if no frequency
    TODO: figure out a way of retaining "-" info (by passing extra parameter to readConnections
    param addEmpty: Adds any remaining items in oldDict to combo with freq=0
    '''
    # Working on a local copy allows us to use the
    # same connection file for many combinations
    oldDict = oldDict.copy()

    comboDict = {}
    # add made mappings to new frequencies
    for k, v in newDict.iteritems():
        comboDict[k] = {u'freq': newDict[k], u'connect': u''}
        if k in oldDict.keys():
            if oldDict[k] is not None:
                comboDict[k][u'connect'] = oldDict[k]
            del oldDict[k]

    # add any previous mapping
    if addEmpty:
        for k, v in oldDict.iteritems():
            if v is not None:
                comboDict[k] = {u'freq': 0, u'connect': v}

    return comboDict


def simpleEmpty(oldDict, newDicts):
    '''
    Returns a simple dictionary of all frequency 0 objects
    I.e. remainign objects once other keys have been stripped
    '''
    emptyDict = {}
    # collect all used keys
    keys = []
    for d in newDicts:
        keys += d.keys()
    # find all remaining mappings
    for k, v in oldDict.iteritems():
        if k not in keys and v is not None:
            emptyDict[k] = {u'freq': 0, u'connect': v}

    return emptyDict


def simpleWrite(f, dDict, label=u'other=Commons connection', other_tag=u'other'):
    '''
    Outputs a simple mapping in the standard form
    '''
    # set-up
    header = u'{{user:Lokal Profil/LSH2|%s}}\n' % label
    row = u'{{User:Lokal Profil/LSH3\n' \
        + u'|name      = %s\n' \
        + u'|frequency = %d\n' \
        + u'|%s     = %s\n' \
        + u'}}/n'
    footer = u'|}\n'
    # output
    f.write(header)
    for key, val in sortedBy(dDict):
        f.write(row % (key, val[u'freq'], other_tag, val[u'connect']))
    f.write(footer)


def sortedBy(dDict, sortkey=u'freq'):
    '''
    Given a dictionary this returns a list of the keys orderd
    by decreasing value of the sortkey
    '''
    return sorted(dDict.iteritems(), key=lambda (k, v): (v[sortkey], k), reverse=True)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_makeMappings.py in_path out_path\n' \
        + u'\tin_path (optional):the relative pathname to relevant \n' \
        + u'connections directory. Defaults to "%s"' % IN_PATH \
        + u'\tout_path (optional):the relative pathname to the target \n' \
        + u'directory. Defaults to "%s"' % OUT_PATH
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 2:
        run(in_path=argv[0], out_path=argv[1])
    else:
        print usage
# EoF
