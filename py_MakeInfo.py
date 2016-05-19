#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Class containing instructions for making info templates
#
# @ToDo:
# data files should not be hardcoded
# Make many small functions instead of the current behemoths
# Add an init which calls readInLibraries & readConnections
#
# Set up an infoObject which in turn contains the makeTemplate function
#
# Replace to following:
# bla = []
# ...
# if bla
#   data[bla] = bla
# With:
# data[bla] = bla = [] (whenever end consumer doesn't explicitly look for "bla not in data.keys()"
#
import codecs
import os
import helpers
from common import Common


class ImageInfo(object):

    """Structured store of the processed info of an image."""

    def __init__(self):
        """Initialise the image info store with the appropriate fields."""
        self.wikiname = None
        self.orig_file = None
        self.photo_license = None
        self.photo_id = None
        self.source = None
        self.orig_descr = None
        self.photographer = None
        self.orig_stich = None
        self.obj_ids = None
        self.see_also = None
        self.categories = None
        self.obj_data = ImageInfo.make_empty_obj_data()

    @staticmethod
    def make_empty_obj_data():
        """Make obj_data dict with all values initialised to None or False."""
        return {
            u'invNr': None,
            u'title': None,
            u'description': None,
            u'date': None,
            u'source': None,
            u'artist': None,
            u'manufacturer': None,
            u'owner': None,
            u'depicted': None,
            u'death_year': None,
            u'exhibits': None,
            u'orig_event': None,
            u'place': None,
            u'title_orig': None,
            u'title_en': None,
            u'material_tech': None,
            u'signature': None,
            u'dimensions': None,
            u'related': None,
            u'cat_meta': None,
            u'cat_event': None,
            u'cat_artist': None,
            u'cat_depicted': None,
            u'cat_obj': None,
            u'multiple': False
        }

    def make_template(self, preview=False):
        """Output a {{LSH artwork}} for the current ImageInfo object."""
        # event (orig_event)
        text = u''
        if preview:
            text += u'%s\n' % self.wikiname
        text += u'{{LSH artwork\n'
        text += ImageInfo.format_multi_value_parameter(
            'artist', self.obj_data['artist'])
        if self.obj_data['manufacturer']:
            text += ImageInfo.format_multi_value_parameter(
                'manufacturer', self.obj_data['manufacturer'])
        text += u'|title= '
        if self.obj_data['title_orig'] or self.obj_data['title_en']:
            titlar = u'{{Title\n'
            if self.obj_data['title_orig']:
                titlar += u'|%s\n' % self.obj_data['title_orig'][0]
            if self.obj_data['title_en']:
                titlar += u'|en = %s\n' % self.obj_data['title_en'][0]
            if self.obj_data['title']:
                titlar += u'|sv = %s\n' % self.obj_data['title']
            text += titlar + u'}}\n'
        elif self.obj_data['title']:
            text += u'{{Title|%s}}\n' % self.obj_data['title']
        # if title_orig or title_en:
        #     if title_orig: text += u'%s\n' % title_orig[0]
        #     if title: text += u'{{sv|%s}}\n' % title
        #     if title_en: text += u'{{en|%s}}\n' % title_en[0]
        # elif title: text += u'%s\n' % title
        else:
            text += u'\n'
        text += u'|description= '
        if self.obj_data['depicted']:
            if self.obj_data['multiple']:
                for dep in self.obj_data['depicted']:
                    inv_nr_dep = dep[0]
                    # depList = dep[1]
                    text += ImageInfo.format_depicted(
                        self.obj_data['depicted'], inv_nr=inv_nr_dep)
            else:
                text += ImageInfo.format_depicted(self.obj_data['depicted'])
        if self.obj_data['description']:
            text += u'{{sv|1=%s}}\n' % self.obj_data['description']
        else:
            text += u'%s\n' % self.orig_descr
        text += u'|original caption= %s' % self.orig_descr
        if self.orig_stich:
            text += u'<br/>\n\'\'\'Nyckelord\'\'\': %s\n' % self.orig_stich
        else:
            text += u'\n'
        if self.obj_data['orig_event']:
            text += ImageInfo.format_multi_value_parameter(
                'event', self.obj_data['orig_event'])
        text += u'|date= '
        if self.obj_data['multiple'] and self.obj_data['date']:
            text += u'\n* %s\n' % '\n* '.join(self.obj_data['date'])
        elif self.obj_data['date']:
            text += u'%s\n' % self.obj_data['date']
        else:
            text += u'\n'
        text += u'|medium= '
        if self.obj_data['material_tech']:
            text += u'%s\n' % u' - '.join(self.obj_data['material_tech'])
        else:
            text += u'\n'
        text += ImageInfo.format_multi_value_parameter(
            'dimensions', self.obj_data['dimensions'])
        text += u'|source= %s\n' % self.source
        text += ImageInfo.format_multi_value_parameter(
            'provenance', self.obj_data['owner'])
        text += ImageInfo.format_multi_value_parameter(
            'exhibition', self.obj_data['exhibits'])
        text += ImageInfo.format_multi_value_parameter(
            'inscriptions', self.obj_data['signature'])
        text += ImageInfo.format_multi_value_parameter(
            'place of origin', self.obj_data['place'])
        text += u'|original filename= %s\n' % self.orig_file
        if self.obj_data['multiple']:
            text += u'|object-multiple= \n* %s\n' % '\n* '.join(self.obj_data['invNr'])
        else:
            text += u'|object-id= %s\n' % self.obj_ids
            text += u'|inventory number= %s\n' % self.obj_data['invNr']
        text += u'|photo-id= %s\n' % self.photo_id
        text += u'|photo-license= %s\n' % self.photo_license
        text += u'|photographer= %s\n' % self.photographer
        text += ImageInfo.format_empty_value_parameter(
            'deathyear', self.obj_data['death_year'])
        text += u'|other_versions= %s\n' % self.see_also
        if preview:
            text += u'}}<pre>\n%s</pre>\n' % self.categories
        else:
            text += u'}}\n%s' % self.categories
        return text.replace(u'<!>', u'<br/>')

    @staticmethod
    def format_empty_value_parameter(param, value):
        """Format a template parameter which can be empty."""
        text = u'|%s= ' % param
        if value:
            text += u'%s\n' % value
        else:
            text += u'\n'
        return text

    @staticmethod
    def format_multi_value_parameter(param, values):
        """Format a template parameter which can be multi-valued.

        If values is empty this returns an empty parameter
        """
        text = u'|%s= ' % param
        if values:
            if len(values) > 1:
                text += u'* '
            text += u'%s\n' % '\n* '.join(values)
        else:
            text += u'\n'
        return text

    @staticmethod
    def format_depicted(depicted, inv_nr=None):
        """Format list of people with {{depicted person}} templates."""
        max_people = 9  # max entries in a single template
        ending = u'style=plain text'
        if inv_nr:
            ending = u'%s|comment=%s' % (ending, inv_nr)
        text = u''
        while depicted:
            text += u'{{depicted person|%s|%s}}\n' \
                    % ('|'.join(depicted[:max_people]), ending)
            depicted = depicted[max_people:]
        return text


class MakeInfo(object):

    """Store of shared data used by all ImageInfo generation."""

    def __init__(self, flog=None, flog_name=None):
        u"""Initialise object with a logfile.

        :param flog: a file object to use as log file
        :param flogName: filename of logfile, defaults to ¤MakeInfo.log
        """

        # list for storing e.g. id's between testruns
        # TODO consider scrapping this
        self.skiplist = []

        # logfile
        flog_name = flog_name or u'¤MakeInfo.log'
        self.flog = flog or codecs.open(flog_name, 'w', 'utf-8')

    def catTestBatch(self, pho_mull_list, data_dir, connections_dir,
                     outputPath=u'output', log=None):
        """Produce category statistics."""
        self.readInLibraries(folder=data_dir)
        self.readConnections(folder=connections_dir)
        if not log:
            log = codecs.open(
                os.path.join(outputPath, u'catStats2.csv'), 'w', 'utf-8')
        log.write(u'#RealCats/MetaCats|cat1;cat2...\n')
        count = 0
        for pho_mull in pho_mull_list:
            count += 1
            if pho_mull in self.skiplist:
                continue
            w_name, out = self.infoFromPhoto(pho_mull, testing=True)
            if out:
                log.write(out + '\n')
            if count % 1000 == 0:
                print count
            self.skiplist.append(pho_mull)

    def readInLibraries(self, verbose=False, careful=False, folder=u'data'):
        '''reads the given files into dictionaries'''
        self.photoD = Common.file_to_dict(os.path.join(folder, u'photo_multimedia_etc.csv'), idcol=[0, 1], verbose=verbose, careful=careful)
        self.stichD = Common.file_to_dict(os.path.join(folder, u'stichwort_trim.csv'), verbose=verbose, careful=careful)
        self.massD = Common.file_to_dict(os.path.join(folder, u'objMass_trim.csv'), verbose=verbose, careful=careful)
        self.multiD = Common.file_to_dict(os.path.join(folder, u'objMultiple_trim.csv'), verbose=verbose, careful=careful)
        self.objD = Common.file_to_dict(os.path.join(folder, u'objDaten_etc.csv'), verbose=verbose, careful=careful)
        self.aussD = Common.file_to_dict(os.path.join(folder, u'ausstellung_trim.csv'), verbose=verbose, careful=careful)
        self.ereignisD = Common.file_to_dict(os.path.join(folder, u'ereignis_trim.csv'), verbose=verbose, careful=careful)
        self.kuenstlerD = Common.file_to_dict(os.path.join(folder, u'kuenstler_trim.csv'), verbose=verbose, careful=careful)
        self.wikinameD = Common.file_to_dict(os.path.join(folder, u'filenames.csv'), idcol=[0, 1], verbose=verbose, careful=careful)
        self.photoAllD = Common.file_to_dict(os.path.join(folder, u'photoAll.csv'), idcol=[0, 5], verbose=verbose, careful=careful)

    def readConnections(self, verbose=False, keepskip=False, folder=u'connections'):
        '''reads the commons connections files into dictionaries'''
        self.stichC = Common.makeConnections(os.path.join(folder, u'commons-Keywords.csv'), start=u'[[:Category:', end=u']]', multi=True, verbose=verbose, keepskip=keepskip)
        self.placesC = Common.makeConnections(os.path.join(folder, u'commons-Places.csv'), addpipe=True, verbose=verbose, keepskip=keepskip)
        self.ereignisC = Common.makeConnections(os.path.join(folder, u'commons-Events.csv'), start=u'[[:Category:', end=u']]', multi=True, verbose=verbose, keepskip=keepskip)
        self.ereignisLinkC = Common.makeConnections(os.path.join(folder, u'commons-Events.csv'), useCol=2, start=u'[[', end=u']]', verbose=verbose, keepskip=keepskip)
        self.peopleLinkC = Common.makeConnections(os.path.join(folder, u'commons-People.csv'), useCol=3, start=u'[[', end=u']]', verbose=verbose, keepskip=keepskip)
        self.peopleCreatC = Common.makeConnections(os.path.join(folder, u'commons-People.csv'), useCol=4, start=u'[[', end=u']]', verbose=verbose, keepskip=keepskip)
        self.peopleCatC = Common.makeConnections(os.path.join(folder, u'commons-People.csv'), start=u'[[:Category:', end=u']]', verbose=verbose, keepskip=keepskip)
        self.materialC = Common.makeConnections(os.path.join(folder, u'commons-Materials.csv'), multi=True, verbose=verbose, keepskip=keepskip)
        self.objCatC = Common.makeConnections(os.path.join(folder, u'commons-ObjKeywords.csv'), start=u'[[:Category:', end=u']]', multi=True, verbose=verbose, keepskip=keepskip)
        self.photographerCreatC = Common.makeConnections(os.path.join(folder, u'commons-Photographers.csv'), useCol=2, start=u'[[', end=u']]', verbose=verbose, keepskip=keepskip)
        self.photographerCatC = Common.makeConnections(os.path.join(folder, u'commons-Photographers.csv'), start=u'[[:Category:', end=u']]', verbose=verbose, keepskip=keepskip)
        self.rolesC = MakeInfo.make_role_output_mappings()
        self.role_mappings = MakeInfo.make_role_input_mappings()
        self.massC = MakeInfo.makeDimensions()
        self.lic = MakeInfo.makeAbbrevLicense()
        self.source = MakeInfo.makeAbbrevSource()

    def infoFromPhoto(self, pho_mull, preview=True, testing=False):
        phoInfo = self.photoD[pho_mull]

        # skip any which don't have a filename
        if pho_mull not in self.wikinameD.keys():
            self.flog.write('No filename: %s\n' % pho_mull)
            return ('No filename: %s\n' % pho_mull, None)

        # temporary check
        if self.wikinameD[pho_mull][u'ext'] == u'':
            print u'Found a file without an extention!: %s' % pho_mull
            return ('file without an extention: %s\n' % pho_mull, None)

        # set up Info object
        image_info = ImageInfo()

        # maintanance categories
        cat_meta = []

        # collect info from Photo.csv
        image_info.wikiname = u'%s.%s' % (
            self.wikinameD[pho_mull][u'filename'],
            self.wikinameD[pho_mull][u'ext'])
        image_info.orig_file = self.wikinameD[pho_mull][u'MulDateiS']
        image_info.photo_license = self.lic[phoInfo[u'PhoAufnahmeortS']]
        image_info.photo_id = phoInfo[u'PhoId']
        image_info.source = self.source[phoInfo[u'PhoSwdS']]  # can be overridden by objData
        image_info.orig_descr = phoInfo[u'PhoBeschreibungM']
        image_info.photographer, cat_photographer = self.make_photographer(phoInfo)

        # category-stichwort
        image_info.orig_stich, cat_stich = self.handle_stichwort(phoInfo, cat_meta)

        # objId(s)
        # TODO pass this the image_info object instead and use already initialised obj_data
        image_info.obj_ids, image_info.obj_data, source = self.handle_obj_ids(phoInfo, image_info.source, cat_meta)

        # see also
        image_info.see_also = self.make_see_also(phoInfo, image_info.obj_data)

        # Combine categories
        # TODO: rename this format_categories and consider doing it in ImageInfo
        #       since it is related to outputting
        image_info.categories, printedCats = MakeInfo.handle_categories(
            cat_meta, cat_stich, cat_photographer, image_info.obj_data)

        if testing:
            catData = u'%r/%r|%s' % (len(printedCats) - len(cat_meta),
                                     len(cat_meta),
                                     ';'.join(printedCats))
            return (None, catData)

        text = image_info.make_template(preview=preview)
        return (image_info.wikiname, text)

    def make_photographer(self, pho_info):
        """Construct the photographer field and add photographer category."""
        photographer = u'%s %s' % (pho_info[u'AdrVorNameS'],
                                   pho_info[u'AdrNameS'])
        photographer = photographer.strip()
        cat_photographer = None

        if photographer:
            cat_photographer = self.photographerCatC[photographer]
            creator = self.photographerCreatC[photographer]
            if creator:
                photographer = u'[[%s|]]' % creator  # link photographer
        return photographer, cat_photographer

    def handle_stichwort(self, pho_info, cat_meta):
        """Isolate original stichwort and find mapped categories."""
        stich_ids = helpers.split_multi_valued(pho_info[u'PstId'])
        orig_stich = []
        cat_stich = []
        if stich_ids:
            for s in stich_ids:
                stich_key = self.stichD[s][u'StiBezeichnungS']
                orig_stich.append(stich_key)
                stich_key = stich_key.lower()
                # map to actual category
                if self.stichC.get(stich_key):
                    for sc in self.stichC[stich_key]:
                        cat_stich.append(sc)
                elif stich_key in self.stichC.keys():
                    cat_meta.append(u'unmatched keyword')
        if not cat_stich:
            cat_stich = None
        if not orig_stich:
            orig_stich = u''
        else:
            orig_stich = ', '.join(orig_stich)
        return orig_stich, cat_stich

    def handle_obj_ids(self, pho_info, source, cat_meta):
        """Handle data extracted through ObjIds for the photo."""
        obj_ids = helpers.split_multi_valued(pho_info[u'PhoObjId'])
        # objId(s)
        obj_data = ImageInfo.make_empty_obj_data()

        # Deal with info from objIds
        if not obj_ids:  # do nothing
            cat_meta.append(u'no objects')
        elif len(obj_ids) == 1:
            # cat_meta.append(u'one object')
            obj_ids = obj_ids[0]
            source = self.handle_single_obj_id(obj_ids, obj_data,
                                               source, cat_meta)
        else:
            # cat_meta.append(u'many objects')
            obj_data[u'multiple'] = True
            self.handle_multiple_obj_ids(obj_ids, obj_data, source)

        return obj_ids, obj_data, source

    def handle_single_obj_id(self, obj_id, obj_data, source, cat_meta):
        """Handle the case where there is a single associated objId.

        Returns source and populates objData and cat_meta.
        """
        obj_data = self.infoFromObject(obj_id, obj_data)
        # use object source instead since this contains SKObok info
        if obj_data[u'source']:
            source = obj_data[u'source']
        if obj_data[u'cat_meta']:
            cat_meta += obj_data[u'cat_meta']

        return source

    def handle_multiple_obj_ids(self, obj_ids, obj_data, source):
        """Handle the case where there are multiple associated objIds.

        Returns nothing but populates objData.
        """
        many_data = {}
        for obj_id in obj_ids:
            data_to_fill = dict.fromkeys([u'invNr', u'title', u'date',
                                          u'artist', u'cat_artist',
                                          u'manufacturer', u'depicted',
                                          u'cat_depicted', u'death_year',
                                          u'source'])
            # TODO: consider sending a make_empty_obj_data() instead
            many_data[obj_id] = self.infoFromObject(obj_id, data_to_fill)
        # dict.fromkeys doesn't allow initialisation with []
        obj_data.update({i: [] for i in (u'invNr', u'date', u'artist',
                                         u'cat_artist', u'manufacturer',
                                         u'depicted', u'cat_depicted')})

        # combine each object into main obj_data
        for k, v in many_data.iteritems():
            if v[u'title']:
                v[u'title'] = u' - %s' % v[u'title']
            # TODO: Consider sticking formatting string in own function
            obj_data[u'invNr'].append(u'{{LSH-link|%s|%s|%s}}%s'
                                      % (k, v[u'invNr'], source, v[u'title']))
            if v[u'date']:
                obj_data[u'date'].append(u'%s: %s' % (v[u'invNr'], v[u'date']))
            if v[u'artist']:
                for a in v[u'artist']:
                    obj_data[u'artist'].append(u'%s: %s' % (v[u'invNr'], a))
            if v[u'cat_artist']:
                obj_data[u'cat_artist'] += v[u'cat_artist']
            if v[u'manufacturer']:
                for m in v[u'manufacturer']:
                    obj_data[u'manufacturer'].append(u'%s: %s'
                                                     % (v[u'invNr'], m))
            if v[u'depicted']:  # note that this is different
                for d in v[u'depicted']:
                    obj_data[u'depicted'].append(u'%s: %s' % (v[u'invNr'], d))
            if v[u'cat_depicted']:
                obj_data[u'cat_depicted'] += v[u'cat_depicted']

    @staticmethod
    def handle_categories(cat_meta, cat_stich, cat_photographer, obj_data):
        """Combine categories into a single text block."""
        # Categories need de-duplidication
        categories = u''
        printed_cats = []
        if cat_stich:
            categories, printed_cats = MakeInfo.makeCategory(
                u'Photograph categories', cat_stich,
                printed=printed_cats, addTo=categories)
        if obj_data[u'cat_event']:
            categories, printed_cats = MakeInfo.makeCategory(
                u'Event categories', obj_data[u'cat_event'],
                printed=printed_cats, addTo=categories)
        if obj_data[u'cat_artist']:
            categories, printed_cats = MakeInfo.makeCategory(
                u'Artist categories', obj_data[u'cat_artist'],
                printed=printed_cats, addTo=categories)
        if obj_data[u'cat_depicted']:
            categories, printed_cats = MakeInfo.makeCategory(
                u'Depicted categories', obj_data[u'cat_depicted'],
                printed=printed_cats, addTo=categories)
        if obj_data[u'cat_obj']:
            categories, printed_cats = MakeInfo.makeCategory(
                u'Object categories', obj_data[u'cat_obj'],
                printed=printed_cats, addTo=categories)

        # before cat_photographer since these are a type of meta categories
        if not printed_cats:
            cat_meta.append(u'without any categories')
        if cat_photographer:
            categories, printed_cats = MakeInfo.makeCategory(
                u'Photographer category', [cat_photographer, ],
                printed=printed_cats, addTo=categories)
        if cat_meta:
            cat_meta = list(set(cat_meta))
            categories, printed_cats = MakeInfo.makeCategory(
                u'Maintanance categories', cat_meta,
                pre=u'Media contributed by LSH: ',
                printed=printed_cats, addTo=categories)

        return categories, printed_cats

    def make_see_also(self, pho_info, obj_data):
        """Make a see_also galleries."""
        see_also = u''
        printed_pics = []  # ensure an image does not appear in both galleries
        same_object = helpers.split_multi_valued(pho_info[u'same_object'])
        if same_object:
            gallery, printed_pics = self.output_same_object(
                same_object, printed_pics)
            see_also += gallery
        if obj_data[u'related']:
            gallery, printed_pics = self.output_related(
                obj_data[u'related'], printed_pics)
            see_also += gallery
        return see_also

    def output_same_object(self, same_object, printed_pics):
        """Make a gallery with other images of the same object."""
        gallery_title = u'Different images of same object'
        filenames = []
        for so in same_object:
            if so in self.photoAllD.keys():
                f_name = self.photoAllD[so]['PhoSystematikS']
                filenames.append(f_name)
            elif so in self.wikinameD.keys():
                f_name = u'%s.%s' % (self.wikinameD[so]['filename'],
                                     self.wikinameD[so]['ext'])
                filenames.append(f_name)
        return MakeInfo.makeGallery(gallery_title, filenames,
                                    printed_pics)

    def output_related(self, related_object, printed_pics):
        """Make a gallery with images of related objects."""
        gallery_title = u'Related objects'
        filenames = []
        captions = {}
        for ro, caption in related_object:
            if ro in self.photoAllD.keys():
                f_name = self.photoAllD[ro]['PhoSystematikS']
                filenames.append(f_name)
                captions[f_name] = caption
            elif ro in self.wikinameD.keys():
                f_name = u'%s.%s' % (self.wikinameD[ro]['filename'],
                                     self.wikinameD[ro]['ext'])
                filenames.append(f_name)
                captions[f_name] = caption
        return MakeInfo.makeGallery(gallery_title, filenames,
                                    printed_pics, captions=captions)

    def infoFromObject(self, objId, data):
        """Return a dictionary of information based on an objId."""
        objInfo = self.objD[objId]
        data[u'cat_meta'] = cat_meta = []

        # collect info from ObjDaten.csv
        data[u'source'] = source = self.source[objInfo[u'AufAufgabeS']]
        nyckelord = objInfo[u'ObjTitelOriginalS']  # titel/nyckelord
        kort = objInfo[u'ObjTitelWeitereM']  # kortbeskrivning
        invNr = objInfo[u'ObjInventarNrS']
        group = objInfo[u'ObjReferenzNrS'].lower()
        classification = objInfo[u'ObjSystematikS'].lower()
        date = objInfo[u'ObjDatierungS']
        description = objInfo[u'ObjReserve01M']

        # multi-valued columns need to be split first
        exhibits = helpers.split_multi_valued(objInfo[u'ausId'])
        related = helpers.split_multi_valued(objInfo[u'related'])
        events = helpers.split_multi_valued(objInfo[u'ergId'])
        roles = helpers.split_multi_valued(objInfo[u'role:roleCmt:kueId'])
        mulId = helpers.split_multi_valued(objInfo[u'mulId'])
        dimensions = helpers.split_multi_valued(objInfo[u'massId'])

        # InvNr. Note that Skokloster boksamling uses kort
        # Specifically Skokloster boksamling uses Signumno. instead of inv. no.
        if not invNr:
            invNr = kort
            data[u'invNr'] = u'SKO %s' % invNr  # don't want SKObok here
        else:
            data[u'invNr'] = u'%s %s' % (source, invNr)

        # Title
        if source == u'LRK':
            data[u'title'] = kort
        else:
            data[u'title'] = nyckelord

        # description
        if description:
            data[u'description'] = description

        # datering
        stdDate = Common.stdDate(date)
        if stdDate is None:
            cat_meta.append(u'malformated year')
        else:
            date = stdDate
        data[u'date'] = date

        # process and add to data
        self.handle_exhibits(exhibits, data)
        self.handle_events(events, data)
        self.multiCruncher(mulId, data)
        self.handle_dimensions(dimensions, data)
        self.handle_obj_categories(group, classification, data)
        self.handle_related(related, data)
        self.handle_roles(roles, data)

        return data
    # -----------------------------------------------------------------------------------------------

    def handle_exhibits(self, exhibits, data):
        """Add exhibits to data if present."""
        # skip on empty
        if not exhibits:
            return

        data[u'exhibits'] = []
        exhibit_dict = {}
        counter = 0
        for e in exhibits:
            counter += 1
            ex_name = self.aussD[e][u'AusTitelS']
            ex_place = self.aussD[e][u'AusOrtS']
            ex_year = self.aussD[e][u'std_year']
            if self.placesC.get(ex_place):
                ex_place = self.placesC[ex_place]
            elif ex_place in self.placesC.keys():
                data[u'cat_meta'].append(u'unmatched place')
            if ex_year:
                out = u'%s (%s) %s' % (ex_name, ex_year, ex_place)
            else:
                out = u'%s: %s' % (ex_name, ex_place)
            exhibit_dict['%s%r' % (ex_year, counter)] = out.strip(u': ')
        for key in sorted(exhibit_dict.iterkeys()):
            data[u'exhibits'].append(exhibit_dict[key])

    def handle_events(self, events, data):
        """Add events to data if present."""
        # skip on empty
        if not events:
            return

        orig_event = []
        cat_event = []
        for e in events:
            event_key = self.ereignisD[e][u'ErgKurztitelS']
            # map to actual category
            if event_key in self.ereignisC.keys() and \
                    self.ereignisC[event_key]:
                for ec in self.ereignisC[event_key]:
                    cat_event.append(ec)
            elif event_key in self.ereignisC.keys():
                data[u'cat_meta'].append(u'unmatched event')
            if event_key in self.ereignisLinkC.keys() and \
                    self.ereignisLinkC[event_key]:
                orig_event.append(u'[[%s|%s]]'
                                  % (self.ereignisLinkC[event_key],
                                     event_key))
            else:
                orig_event.append(event_key)
        if cat_event:
            data[u'cat_event'] = cat_event
        if orig_event:
            data[u'orig_event'] = orig_event

    def handle_related(self, related, data):
        """Add related objects to data if present."""
        # skip on empty
        if not related:
            return

        rel_list = []
        rel_dict = {}
        for r in related:
            if r not in self.objD.keys():
                # skip items without images in this batch or previously batches
                continue
            r_inv_nr = self.objD[r][u'ObjInventarNrS']
            r_source = self.source[self.objD[r][u'AufAufgabeS']]
            if not r_inv_nr:
                r_inv_nr = self.objD[r][u'ObjTitelWeitereM']
            r_inv_nr = u'%s %s' % (r_source, r_inv_nr)
            rel_dict[r] = ([], r_inv_nr)

        if rel_dict:
            # add assoicated filenames from current batch
            for r_pho_mull, r_photo in self.photoD.iteritems():
                # only use those with an unique objId, so no need to split
                r_obj_id = r_photo[u'PhoObjId']
                if r_obj_id in rel_dict.keys():
                    rel_dict[r_obj_id][0].append(r_pho_mull)
            # add assoicated filenames from previous uploads
            for r_pho_mull, r_photo in self.photoAllD.iteritems():
                # only use those with an unique objId, so no need to split
                r_obj_id = r_photo[u'PhoObjId']
                if r_obj_id in rel_dict.keys():
                    rel_dict[r_obj_id][0].append(r_pho_mull)
            for r, v in rel_dict.iteritems():
                if not v[0]:
                    continue
                for pho_mull in v[0]:
                    rel_list.append((pho_mull, v[1]))
            if rel_list:
                data[u'related'] = rel_list

    def handle_roles(self, roles, data):
        """Add person related objects to data if present."""
        # skip on empty
        if not roles:
            return

        # set-up
        artist = []
        manufacturer = []
        owner = []
        depicted = []
        cat_artist = []
        cat_depicted = []

        # process all roles
        for r in roles:
            role, role_cmt, kue_id = r.split(':')
            if role_cmt in self.role_mappings['bad_cmts']:
                continue
            if role in self.role_mappings['ok_roles']:
                name = self.formatKuenstler(
                    kue_id, data[u'cat_meta'],
                    role in self.role_mappings['creative_roles'])
                if role in self.rolesC.keys():
                    name = u'%s: %s' % (self.rolesC[role], name)
            if role in self.role_mappings['manufacturer']:
                manufacturer.append(name)
            elif role in self.role_mappings['owner']:
                owner.append(name)
            elif role in self.role_mappings['depicted']:
                depicted.append(name)
                if self.peopleCatC.get(kue_id):
                    cat_depicted.append(self.peopleCatC[kue_id])
            elif role in self.role_mappings['artist']:
                artist.append(name)
                death_year = self.kuenstlerD[kue_id][u'KudJahrBisL']
                if death_year:
                    if data[u'death_year']:
                        death_year = max(data[u'death_year'], int(death_year))
                    data[u'death_year'] = death_year
            if role in self.role_mappings['creative_roles'] and \
                    self.peopleCatC.get(kue_id):
                cat_artist.append(self.peopleCatC[kue_id])

        # store in data
        # TODO: check if final output differes between
        #       key not in data.keys() and data[key] == [] or data[key] == None
        #       if not then initialise as key = data[key] = []
        #       also in several other places
        if manufacturer:
            data['manufacturer'] = manufacturer
        if owner:
            data['owner'] = owner
        if depicted:
            data['depicted'] = depicted
        if artist:
            data['artist'] = artist
        if cat_artist:
            data['cat_artist'] = cat_artist
        if cat_depicted:
            data['cat_depicted'] = artist

    def handle_obj_categories(self, group, classification, data):
        """Add object categories to data from group and classification."""
        # objcategories from group and classification
        cat_obj = []
        # group if source == HWY
        if data[u'source'] == u'HWY' and group:
            if self.objCatC.get(group):
                for sc in self.objCatC[group]:
                    cat_obj.append(sc)
            elif group in self.objCatC.keys():
                data[u'cat_meta'].append(u'unmatched objKeyword')

        # classifiction for the others
        # note failiure for ord2 keywords containing a comma
        if classification:
            if u'(' not in classification:
                if classification in self.objCatC.keys() and \
                        self.objCatC[classification]:
                    for sc in self.objCatC[classification]:
                        cat_obj.append(sc)
                elif classification in self.objCatC.keys():
                    data[u'cat_meta'].append(u'unmatched objKeyword')
            else:
                # TODO: this can be done neater
                parts = classification.split(')')
                for p in parts:
                    if len(p) < 2:
                        continue
                    if '(' in p:
                        pos = p.find('(')
                        ord1 = p[:pos].strip(', ')
                        if self.objCatC.get(ord1):
                            for sc in self.objCatC[ord1]:
                                cat_obj.append(sc)
                        elif ord1 in self.objCatC.keys():
                            data[u'cat_meta'].append(u'unmatched objKeyword')
                        else:
                            ord2 = p[pos + 1:].split(',')
                            ord2 = ord2[-1].strip()  # keep only last word
                            if ord2 in self.objCatC.keys() and \
                                    self.objCatC[ord2]:
                                for sc in self.objCatC[ord2]:
                                    cat_obj.append(sc)
                            elif ord2 in self.objCatC.keys():
                                data[u'cat_meta'].append(u'unmatched objKeyword')

        # store in data
        if cat_obj:
            data[u'cat_obj'] = cat_obj

    def handle_dimensions(self, dimensions, data):
        """Add dimensions to data."""
        # skip on empty
        if not dimensions:
            return

        dims = []
        for d in dimensions:
            d_type = self.massD[d][u'ObmTypMasseS']
            if d_type not in self.massC.keys():
                continue  # filter on translatable values
            d_type = self.massC[d_type]
            d_value = self.massD[d][u'ObmMasseS']
            dims.append((d_type, d_value))

        # convert the list of tuples to a list of strings
        dims = MakeInfo.dimensionCruncher(dims, data[u'cat_meta'])
        if dims:
            data[u'dimensions'] = dims

    def multiCruncher(self, mulId, data):
        # skip on empty
        if not mulId:
            return

        tOrt = []
        tLand = []
        title_en = set()
        title_orig = set()
        material_tech = set()
        sign = set()
        # TODO externalise these
        mat_techTypes = [u'material', u'material och teknik', u'teknik']
        sigTypes = [u'signatur/påskrift', u'signering', u'signatur']
        okTypes = [u'tillverkningsort', u'tillverkningsland', u'titel (engelsk)',
                   u'titel'] + sigTypes + mat_techTypes
        for m in mulId:
            typ = self.multiD[m][u'OmuTypS'].lower()
            value = self.multiD[m][u'OmuInhalt01M'].strip()
            val_cmt = self.multiD[m][u'OmuBemerkungM'].strip()
            if typ in okTypes and len(value) > 0:
                if not val_cmt or val_cmt == value:
                    val_cmt = None
                if typ in sigTypes:
                    if val_cmt:
                        value = u'%s [%s]' % (value, val_cmt)
                    sign.add(value)
                elif typ in mat_techTypes:
                    value = value.lower()
                    if value in self.materialC.keys() and \
                            self.materialC[value]:
                        for sc in self.materialC[value]:
                            value = u'{{technique|%s}}' % sc
                            if val_cmt:
                                value = u'%s (%s)' % (value, val_cmt)
                            material_tech.add(value)
                    elif value in self.materialC.keys():
                        data[u'cat_meta'].append(u'unmatched material')
                elif typ == u'tillverkningsort':
                    if self.placesC.get(value):
                        value = self.placesC[value]
                    elif value in self.placesC.keys():
                        data[u'cat_meta'].append(u'unmatched place')
                    tOrt.append(value)
                elif typ == u'tillverkningsland':
                    if self.placesC.get(value):
                        value = self.placesC[value]
                    elif value in self.placesC.keys():
                        data[u'cat_meta'].append(u'unmatched place')
                    if val_cmt:
                        value = u'%s (%s)' % (value, val_cmt)
                    tLand.append(value)
                elif typ == u'titel (engelsk)':
                    if value != data[u'title']:
                        if val_cmt:
                            value = u'%s (%s)' % (value, val_cmt)
                        title_en.add(value)
                elif typ == u'titel':
                    if value != data[u'title']:
                        if val_cmt:
                            value = u'%s (%s)' % (value, val_cmt)
                        title_orig.add(value)
        # format and send to relevant field
        # this is were Connection-lookup shold be done add maintanance cat if lookup fails
        if sign:
            data[u'signature'] = list(sign)
        if material_tech:
            data[u'material_tech'] = list(material_tech)
        if title_en:
            data[u'title_en'] = list(title_en)
        if title_orig:
            data[u'title_orig'] = list(title_orig)
        if tOrt and tLand:
            places = set()
            if len(tOrt) == len(tLand):
                for i in range(0, len(tLand)):
                    place = '%s, %s' % (tOrt[i], tLand[i])
                    places.add(place)
            else:
                tOrt = '; '.join(set(tOrt))
                tLand = '; '.join(set(tLand))
                places.add(u'%s / %s' % (tOrt, tLand))
            data[u'place'] = list(places)
        elif tOrt:
            data[u'place'] = list(set(tOrt))
        elif tLand:
            data[u'place'] = list(set(tLand))

    @staticmethod
    def dimensionCruncher(dims, cat_meta, debug=''):
        '''takes a list of tuples and returns a list of strings'''
        # @toDo: make sure named parameters are used for size (incl. unit). See if "part=" was added
        # check if all are simply formatted
        lUnits = [u'm', u'dm', u'cm', u'mm']
        wUnits = [u'g', u'kg']
        returns = []  # list of strings
        types = []
        prefixes = []
        circas = []
        nice = True
        units = []
        nice_dims = []
        for d in dims:  # check if formating is "prefix number unit"
            ca = ''
            if d[1].endswith(u' c'):  # additional possible ending is "c" for circa
                ca = 'ca.'
                vals = d[1][:-2].replace('  ', ' ').split(' ')
            else:
                vals = d[1].replace('  ', ' ').split(' ')
            i = len(vals) - 2
            if i < 0:
                cat_meta.append(u'dim-without units|%s%s' % (debug, d[0]))
                nice = False
                break
            if not Common.is_number(vals[i].replace(',', '.')):
                nice = False
                break
            role, prefix, num, unit = (d[0], ' '.join(vals[:i]),
                                       vals[i].replace(',', '.'), vals[i + 1])
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
        if nice and len(units) == 1 and unique_r and \
                len(prefixes) < 2 and len(circas) == 1:
            # well formated and suitable for a single size template
            unit_size = ''
            prefix_size = ''
            circa_size = ''
            size = ''
            for d in nice_dims:
                role, prefix, num, unit, ca = d
                if role == u'weight':
                    if unit not in wUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    if prefix:
                        prefix = u' (%s)' % prefix
                    if ca:
                        ca = u'{{circa}} '
                    returns.append(u'%s{{weight|%s|%s}}%s'
                                   % (ca, unit, num, prefix))
                else:
                    if unit not in lUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    unit_size = unit
                    prefix_size = prefix
                    circa_size = ca
                    size = u'%s|%s=%s' % (size, role, num)
            if size:
                if prefix_size:
                    prefix_size = u' (%s)' % prefix_size
                if circa_size:
                    circa_size = u'{{circa}} '
                returns.append(u'%s{{size|unit=%s%s}}%s'
                               % (circa_size, unit_size, size, prefix_size))
        elif nice:
            # well formated but separate templates needed
            if nice_dims:
                cat_meta.append(u'dim-with multiple size templates')
            for d in nice_dims:
                role, prefix, num, unit, ca = d
                if prefix:
                    prefix = u' (%s)' % prefix
                if ca:
                    ca = u'{{circa}} '
                if role == u'weight':
                    if unit not in wUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    returns.append(u'%s{{weight|%s|%s}}%s'
                                   % (ca, unit, num, prefix))
                else:
                    if unit not in lUnits:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    returns.append(u'%s{{size|unit=%s|%s=%s}}%s'
                                   % (ca, unit, role, num, prefix))
        else:  # ill formated
            cat_meta.append(u'dim-with unformated dimensions')
            for d in dims:
                returns.append(u'%s: %s' % (d[0], d[1]))
        return returns

    # formating output
    def formatKuenstler(self, kueId, cat_meta, creative=False):
        if creative and \
                kueId in self.peopleCreatC.keys() and \
                self.peopleCreatC[kueId]:
            return u'{{%s}}' % self.peopleCreatC[kueId]
        elif creative and kueId in self.peopleCreatC.keys():
            cat_meta.append(u'unmatched creator')
        kuenstler = self.kuenstlerD[kueId]
        name = u'%s %s' % (kuenstler[u'KueVorNameS'], kuenstler[u'KueNameS'])
        if self.peopleLinkC.get(kueId):
            return u'[[%s|%s]]' % (self.peopleLinkC[kueId], name.strip())
        bYear = kuenstler[u'KudJahrVonL']
        dYear = kuenstler[u'KudJahrBisL']
        ort = kuenstler[u'KudOrtS']
        land = kuenstler[u'KudLandS']
        yrke = kuenstler[u'KueFunktionS']
        years = ''
        if bYear or dYear:
            years = u'%s-%s' % (bYear, dYear)
        bracket = u'%s, %s' % (yrke, years)
        if years or yrke:
            bracket = u' (%s) ' % bracket.strip(', ')
        place = u'%s%s' % (ort, land)
        if ort and land:
            place = u'%s, %s' % (ort, land)
        out = u'%s%s%s' % (name.strip(), bracket, place.strip())
        return out.strip()

    @staticmethod
    def makeGallery(galleryTitle, filenames, printed, captions=None):
        """
        Given a list of objects add the corresponding images to a gallery.

        Also adds printed images to the list of previously printed images
        :param galleryTitle: Gallery title
        :param filenames: list of (Commons) filenames
        :param printed: list previously printed images
        :param captions: a {filename: caption} dict. Defaults to None
        :return: str, list
        """
        # check for duplicates
        filenames = list(set(filenames))  # remove internal duplicates
        for p in printed:
            if p in filenames:
                filenames.remove(p)
        printed += filenames

        # escape if all were dupes
        if not filenames:
            return '', printed

        # output
        text = u'\n<gallery caption="%s">\n' % galleryTitle
        for filename in filenames:
            if captions is not None:
                text += u'File:%s|%s\n' % (filename, captions[filename])
            else:
                text += u'File:%s\n' % (filename)
        text += u'</gallery>'
        return text, printed

    @staticmethod
    def makeCategory(caption, lList, printed, addTo, pre=u''):
        # check for duplicates and escape if all were dupes
        lList = list(set(lList))  # remove internal duplicates
        for p in printed:
            if p in lList:
                lList.remove(p)
        printed += lList
        if not lList:
            return addTo, printed
        # output
        text = addTo + u'\n<!--%s-->\n' % caption
        for c in lList:
            text += u'[[Category:%s%s]]\n' % (pre, c)
        return text, printed

    @staticmethod
    def makeDimensions():
        """Set up known dimension mappings."""
        # Todo. Consider replacing by external json mapping
        # bredd should be breath but doesn't seem to exist
        # kanske = [u'kaliber', u'antal', u'Omkrets]
        return {
            u'Höjd': u'height',
            u'Bredd': u'width',
            u'Längd': u'length',
            u'Diameter': u'diameter',
            u'Djup': u'depth',
            u'Tjocklek': u'thickness',
            u'Vikt': u'weight',
            u'Vidd': u'width'
        }

    @staticmethod
    def make_role_output_mappings():
        """Set up known role output mappings."""
        # Todo. Consider replacing by external json mapping
        return {
            u'Författare': u'{{Occupation|author}}',
            u'Gravör': u'{{Occupation|engraver}}',
            u'Kompositör': u'{{Occupation|composer}}'
        }

    @staticmethod
    def make_role_input_mappings():
        """Loads various role mappings for later use.

        TODO: load this from an external json instead.
        """
        roles = {
            'artist': [
                u'Konstnär', u'Upphovsman', u'Författare', u'Kompositör'],
            'manufacturer': [u'Tillverkare', u'Gravör'],
            'owner': [u'Ägare', ],
            'depicted': [u'Avbildning av', u'Avbildning'],
            'bad_cmts': [u'av kopia', ]
        }

        # set up useful groupings
        roles['ok_roles'] = roles['artist'] + roles['manufacturer'] + \
            roles['owner'] + roles['depicted']
        roles['creative_roles'] = roles['artist'] + roles['manufacturer']
        return roles

    @staticmethod
    def makeAbbrevLicense():
        """Set up known mappings for Commons license templates."""
        # Todo. Consider replacing by external json mapping
        return {
            u'CC BY-SA': u'CC-BY-SA',
            u'CC0': u'CC0',
            u'Public Domain': u'PD'
        }

    @staticmethod
    def makeAbbrevSource():
        """Set up known mappings for Commons license templates.

        The last two are for objects.
        """
        # Todo. Consider replacing by external json mapping
        return {
            u'Livrustkammaren': u'LRK',
            u'Skoklosters slott': u'SKO',
            u'Hallwylska museet': u'HWY',
            u'': u'LSH',
            u'LRK dubletter': u'LRK',
            u'Skoklosters slotts boksamling': u'SKObok'
        }
