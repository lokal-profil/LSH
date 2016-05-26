#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Class containing instructions for making info templates
#
# @ToDo:
# data files should not be hardcoded
# Add an init which calls readInLibraries & readConnections
#    Note that this would likely cause issues with py_analyseCSVdata
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
        self.obj_data = None

    @staticmethod
    def make_empty_obj_data():
        """Make obj_data dict with all values initialised to None or False."""
        obj_data = dict.fromkeys(
            [u'invNr', u'title', u'description', u'date', u'source', u'artist',
             u'manufacturer', u'owner', u'depicted', u'death_year',
             u'exhibits', u'orig_event', u'place', u'title_orig', u'title_en',
             u'material_tech', u'signature', u'dimensions', u'related',
             u'cat_meta', u'cat_event', u'cat_artist', u'cat_depicted',
             u'cat_obj'])
        obj_data[u'multiple'] = False
        return obj_data

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

        If values is empty this returns an empty parameter.
        Creator templates does not deal well with preceding '*', hence the
        special handling of these.
        """
        text = u'|%s= ' % param
        if values and len(values) == 1:
            text += u'%s\n' % values[0]
        elif values:
            for v in values:
                if v.startswith('{{Creator:'):
                    text += u'%s\n' % v
                else:
                    text += u'* %s\n' % v
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

        # load some abbreviations
        self.lic = MakeInfo.load_license_abbreviations()
        self.source = MakeInfo.load_source_abbreviations()

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
        self.massC = MakeInfo.load_dimension_mappings()
        self.multi_mappings = MakeInfo.make_multimedia_type_input_mappings()

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
        image_info.obj_ids, image_info.obj_data = self.handle_obj_ids(phoInfo, image_info, cat_meta)

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
        # format output
        if not orig_stich:
            orig_stich = u''
        else:
            orig_stich = ', '.join(orig_stich)
        return orig_stich, cat_stich

    def handle_obj_ids(self, pho_info, image_info, cat_meta):
        """Handle data extracted through ObjIds for the photo.

        Returns list of obj_ids and obj_data object and updates the source
        of the passed image_info.
        """
        obj_ids = helpers.split_multi_valued(pho_info[u'PhoObjId'])
        obj_data = None

        # Deal with info from objIds
        if not obj_ids:  # do nothing
            cat_meta.append(u'no objects')
            obj_data = ImageInfo.make_empty_obj_data()
        elif len(obj_ids) == 1:
            # cat_meta.append(u'one object')
            obj_ids = obj_ids[0]
            obj_data = self.handle_single_obj_id(obj_ids, cat_meta)
            # use object source instead since this contains SKObok info
            if obj_data[u'source']:
                image_info.source = obj_data[u'source']
        else:
            # cat_meta.append(u'many objects')
            obj_data = self.handle_multiple_obj_ids(obj_ids, image_info.source)
            obj_data[u'multiple'] = True

        return obj_ids, obj_data

    def handle_single_obj_id(self, obj_id, cat_meta):
        """Handle the case where there is a single associated obj_id.

        Returns obj_data and adds to cat_meta.
        """
        obj_data = self.infoFromObject(obj_id)
        if obj_data[u'cat_meta']:
            cat_meta += obj_data[u'cat_meta']

        return obj_data

    def handle_multiple_obj_ids(self, obj_ids, source):
        """Handle the case where there are multiple associated objIds."""
        many_data = {}
        for obj_id in obj_ids:
            many_data[obj_id] = self.infoFromObject(obj_id)
        # dict.fromkeys doesn't allow initialisation with []
        obj_data = ImageInfo.make_empty_obj_data()
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

        return obj_data

    @staticmethod
    def handle_categories(cat_meta, cat_stich, cat_photographer, obj_data):
        """Combine categories into a single text block."""
        # Categories need de-duplidication
        categories = u''
        printed_cats = []  # ensure same category isn't outputted twice
        if cat_stich:
            categories += MakeInfo.make_category(
                u'Photograph categories', cat_stich, printed_cats)
        if obj_data[u'cat_event']:
            categories += MakeInfo.make_category(
                u'Event categories', obj_data[u'cat_event'], printed_cats)
        if obj_data[u'cat_artist']:
            categories += MakeInfo.make_category(
                u'Artist categories', obj_data[u'cat_artist'], printed_cats)
        if obj_data[u'cat_depicted']:
            categories += MakeInfo.make_category(
                u'Depicted categories', obj_data[u'cat_depicted'],
                printed_cats)
        if obj_data[u'cat_obj']:
            categories += MakeInfo.make_category(
                u'Object categories', obj_data[u'cat_obj'], printed_cats)

        # before cat_photographer since these are a type of meta categories
        if not printed_cats:
            cat_meta.append(u'without any categories')
        if cat_photographer:
            categories += MakeInfo.make_category(
                u'Photographer category', [cat_photographer, ], printed_cats)
        if cat_meta:
            categories += MakeInfo.make_category(
                u'Maintanance categories', cat_meta, printed_cats,
                prefix=u'Media contributed by LSH: ')

        return categories, printed_cats

    def make_see_also(self, pho_info, obj_data):
        """Make a see_also galleries."""
        see_also = u''
        printed_pics = []  # ensure image does not appear in both galleries
        same_object = helpers.split_multi_valued(pho_info[u'same_object'])
        if same_object:
            see_also += self.output_same_object(same_object, printed_pics)
        if obj_data[u'related']:
            see_also += self.output_related(obj_data[u'related'], printed_pics)
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
        return MakeInfo.make_gallery(gallery_title, filenames, printed_pics)

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
        return MakeInfo.make_gallery(gallery_title, filenames,
                                     printed_pics, captions=captions)

    def infoFromObject(self, objId):
        """Return a dictionary of information based on an objId."""
        objInfo = self.objD[objId]
        data = ImageInfo.make_empty_obj_data()
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
        std_date = Common.std_date(date)
        if std_date is None:
            cat_meta.append(u'malformated year')
        else:
            date = std_date
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

        data[u'orig_event'] = orig_event = []
        data[u'cat_event'] = cat_event = []
        for e in events:
            event_key = self.ereignisD[e][u'ErgKurztitelS']
            # map to actual category
            if self.ereignisC.get(event_key):
                for ec in self.ereignisC[event_key]:
                    cat_event.append(ec)
            elif event_key in self.ereignisC.keys():
                data[u'cat_meta'].append(u'unmatched event')
            if self.ereignisLinkC.get(event_key):
                orig_event.append(u'[[%s|%s]]'
                                  % (self.ereignisLinkC[event_key],
                                     event_key))
            else:
                orig_event.append(event_key)

    def handle_related(self, related, data):
        """Add related objects to data if present."""
        # skip on empty
        if not related:
            return

        data[u'related'] = []
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
                    data[u'related'].append((pho_mull, v[1]))

    def handle_roles(self, roles, data):
        """Add person related objects to data if present."""
        # skip on empty
        if not roles:
            return

        # set-up
        data['artist'] = artist = []
        data['manufacturer'] = manufacturer = []
        data['owner'] = owner = []
        data['depicted'] = depicted = []
        data['cat_artist'] = cat_artist = []
        data['cat_depicted'] = cat_depicted = []

        # process all roles
        for r in roles:
            role, role_cmt, kue_id = r.split(':')
            if role_cmt in self.role_mappings['bad_cmts'] or \
                    role not in self.role_mappings['ok_roles']:
                continue

            # format name
            name = self.format_person(
                kue_id, data[u'cat_meta'],
                role in self.role_mappings['creative_roles'])
            if role in self.rolesC.keys():
                name = u'%s: %s' % (self.rolesC[role], name)

            # store as right type
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
                    # we only care about when the last person died
                    if data[u'death_year']:
                        death_year = max(data[u'death_year'], int(death_year))
                    data[u'death_year'] = death_year

            # add artist category
            if role in self.role_mappings['creative_roles'] and \
                    self.peopleCatC.get(kue_id):
                cat_artist.append(self.peopleCatC[kue_id])

    def handle_obj_categories(self, group, classification, data):
        """Add object categories to data from group and classification."""
        # objcategories from group and classification
        data[u'cat_obj'] = cat_obj = []

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
                if self.objCatC.get(classification):
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
                            if self.objCatC.get(ord2):
                                for sc in self.objCatC[ord2]:
                                    cat_obj.append(sc)
                            elif ord2 in self.objCatC.keys():
                                data[u'cat_meta'].append(u'unmatched objKeyword')

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
        data[u'dimensions'] = MakeInfo.dimensionCruncher(dims, data[u'cat_meta'])

    def multiCruncher(self, mulId, data):
        """Add info via mulId to data, if present."""
        # TODO: Re-factor
        # skip on empty
        if not mulId:
            return

        tOrt = []
        tLand = []
        title_en = set()
        title_orig = set()
        material_tech = set()
        sign = set()
        for m in mulId:
            typ = self.multiD[m][u'OmuTypS'].lower()
            value = self.multiD[m][u'OmuInhalt01M'].strip()
            val_cmt = self.multiD[m][u'OmuBemerkungM'].strip()
            if typ in self.multi_mappings['ok_types'] and value:
                if not val_cmt or val_cmt == value:
                    val_cmt = None
                if typ in self.multi_mappings['signature_types']:
                    if val_cmt:
                        value = u'%s [%s]' % (value, val_cmt)
                    sign.add(value)
                elif typ in self.multi_mappings['material_tech_types']:
                    value = value.lower()
                    if self.materialC.get(value):
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
                elif typ == u'titel (engelsk)' and value != data[u'title']:
                    if val_cmt:
                        value = u'%s (%s)' % (value, val_cmt)
                    title_en.add(value)
                elif typ == u'titel' and value != data[u'title']:
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
        # TODO: Re-factor
        # @toDo: make sure named parameters are used for size (incl. unit). See if "part=" was added
        # check if all are simply formatted
        length_units = [u'm', u'dm', u'cm', u'mm']
        weight_units = [u'g', u'kg']
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
                    if unit not in weight_units:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    if prefix:
                        prefix = u' (%s)' % prefix
                    if ca:
                        ca = u'{{circa}} '
                    returns.append(u'%s{{weight|%s|%s}}%s'
                                   % (ca, unit, num, prefix))
                else:
                    if unit not in length_units:
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
                    if unit not in weight_units:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    returns.append(u'%s{{weight|%s|%s}}%s'
                                   % (ca, unit, num, prefix))
                else:
                    if unit not in length_units:
                        cat_meta.append(u'dim-with weird units|%s%s in %s'
                                        % (debug, role, unit))
                    returns.append(u'%s{{size|unit=%s|%s=%s}}%s'
                                   % (ca, unit, role, num, prefix))
        else:  # ill formated
            cat_meta.append(u'dim-with unformated dimensions')
            for d in dims:
                returns.append(u'%s: %s' % (d[0], d[1]))
        return returns

    # formatting output
    def format_person(self, kueId, cat_meta, creative=False):
        """Create formatted string for an identified artist/person (kuenstler).

        If no creator templates or links/categories are present then the
        full format used is:
        FirstName LastName (profession, birth_year-death_year) city, country
        """
        # return creator template if appropriate and one is known
        if creative and self.peopleCreatC.get(kueId):
            return u'{{%s}}' % self.peopleCreatC[kueId]
        elif creative and kueId in self.peopleCreatC.keys():
            cat_meta.append(u'unmatched creator')

        kuenstler = self.kuenstlerD[kueId]
        name = u'%s %s' % (kuenstler[u'KueVorNameS'], kuenstler[u'KueNameS'])
        name = name.strip()
        # return a link, if one is known
        if self.peopleLinkC.get(kueId):
            return u'[[%s|%s]]' % (self.peopleLinkC[kueId], name)

        # format profession, year bracket
        birth_year = kuenstler[u'KudJahrVonL']
        death_year = kuenstler[u'KudJahrBisL']
        profession = kuenstler[u'KueFunktionS']
        years = ''
        if birth_year or death_year:
            years = u'%s-%s' % (birth_year, death_year)
        bracket = u'%s, %s' % (profession, years)
        if years or profession:
            bracket = u' (%s) ' % bracket.strip(', ')

        # format city, country appendix
        city = kuenstler[u'KudOrtS']
        country = kuenstler[u'KudLandS']
        place = u'%s, %s' % (city, country)
        place = place.strip(', ')

        out = u'%s%s%s' % (name, bracket, place)
        return out.strip(', ')

    @staticmethod
    def make_gallery(gallery_title, filenames, printed, captions=None):
        """
        Given a list of objects add the corresponding images to a gallery.

        Also adds newly printed images to the printed list.
        :param gallery_title: Gallery title
        :param filenames: list of (Commons) filenames
        :param printed: list of previously printed images
        :param captions: a {filename: caption} dict. Defaults to None
        :return: str
        """
        # check for duplicates
        filenames = list(set(filenames))  # remove internal duplicates
        for p in printed:
            if p in filenames:
                filenames.remove(p)
        printed += filenames

        # escape if all were dupes
        if not filenames:
            return ''

        # output
        text = u'\n<gallery caption="%s">\n' % gallery_title
        if captions is not None:
            for filename in filenames:
                text += u'File:%s|%s\n' % (filename, captions[filename])
        else:
            text += u'File:%s\n' % '\nFile:'.join(filenames)
        text += u'</gallery>'
        return text

    @staticmethod
    def make_category(caption, categories, printed, prefix=u''):
        """Given a list of objects add the corresponding images to a gallery.

        Also adds newly printed categories to the printed list.
        :param caption: Comment preceding category block
        :param categories: list of (Commons) categories
        :param printed: list of previously printed images
        :param prefix: a prefix to add to each category name
        :return: str
        """
        # check for duplicates and escape if all were dupes
        categories = list(set(categories))  # remove internal duplicates
        for p in printed:
            if p in categories:
                categories.remove(p)
        printed += categories

        # escape if all were dupes
        if not categories:
            return ''

        # output
        text = u'\n<!--%s-->\n' % caption
        if prefix:
            for c in categories:
                text += u'[[Category:%s%s]]\n' % (prefix, c)
        else:
            text += u'[[Category:%s]]\n' % ']]\n[[Category:'.join(categories)
        return text

    @staticmethod
    def load_dimension_mappings():
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
        """Load various role mappings for later use."""
        # Todo. Consider replacing by external json mapping
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
    def make_multimedia_type_input_mappings():
        """Load various multimedia/mulid mappings for later use."""
        # Todo. Consider replacing by external json mapping
        multi_types = {
            'material_tech_types': [
                u'material', u'material och teknik', u'teknik'],
            'signature_types': [
                u'signatur/påskrift', u'signering', u'signatur'],
            'other_allowed_types': [
                u'tillverkningsort', u'tillverkningsland', u'titel (engelsk)',
                u'titel']
        }

        # set up useful groupings
        multi_types['ok_types'] = multi_types['material_tech_types'] + \
            multi_types['signature_types'] + multi_types['other_allowed_types']
        return multi_types

    @staticmethod
    def load_license_abbreviations():
        """Set up known mappings for Commons license templates."""
        # Todo. Consider replacing by external json mapping
        return {
            u'CC BY-SA': u'CC-BY-SA',
            u'CC0': u'CC0',
            u'Public Domain': u'PD'
        }

    @staticmethod
    def load_source_abbreviations():
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
