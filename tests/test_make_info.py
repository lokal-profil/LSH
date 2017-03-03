#!/usr/bin/python
# -*- coding: UTF-8  -*-
import unittest
import mock
from py_MakeInfo import (
    MakeInfo,
    ImageInfo
)


class TestEmptyValueFormater(unittest.TestCase):
    """Test ImageInfo.format_empty_value_parameter()."""

    def test_format_empty_value_parameter_with_empty(self):
        expected = u'|parameter= \n'
        param = 'parameter'
        self.assertEqual(ImageInfo.format_empty_value_parameter(param, ''),
                         expected)
        self.assertEqual(ImageInfo.format_empty_value_parameter(param, []),
                         expected)
        self.assertEqual(ImageInfo.format_empty_value_parameter(param, None),
                         expected)

    def test_format_empty_value_parameter_with_value(self):
        expected = u'|parameter= value\n'
        self.assertEqual(
            ImageInfo.format_empty_value_parameter('parameter', 'value'),
            expected)


class TestMultiValueFormater(unittest.TestCase):
    """Test ImageInfo.format_multi_value_parameter()."""

    def test_format_multi_value_parameter_with_empty(self):
        expected = u'|parameter= \n'
        param = 'parameter'
        self.assertEqual(ImageInfo.format_multi_value_parameter(param, ''),
                         expected)
        self.assertEqual(ImageInfo.format_multi_value_parameter(param, []),
                         expected)
        self.assertEqual(ImageInfo.format_multi_value_parameter(param, None),
                         expected)

    def test_format_multi_value_parameter_with_single(self):
        expected = u'|parameter= value\n'
        self.assertEqual(
            ImageInfo.format_multi_value_parameter('parameter', ['value', ]),
            expected)

    def test_format_multi_value_parameter_with_multiple(self):
        expected = u'|parameter= * val1\n* val2\n* val3\n'
        value = ['val1', 'val2', 'val3']
        self.assertEqual(
            ImageInfo.format_multi_value_parameter('parameter', value),
            expected)

    def test_format_multi_value_parameter_with_multiple_and_creator(self):
        expected = u'|parameter= * val1\n{{Creator:val2}}\n* val3\n'
        value = ['val1', '{{Creator:val2}}', 'val3']
        self.assertEqual(
            ImageInfo.format_multi_value_parameter('parameter', value),
            expected)


class TestFormatDepicted(unittest.TestCase):
    """Test ImageInfo.format_depicted()."""

    def test_format_depicted_with_empty(self):
        expected = u''
        value = []
        self.assertEqual(ImageInfo.format_depicted(value),
                         expected)

    def test_format_depicted_with_single(self):
        expected = u'{{depicted person|p1|style=plain text}}\n'
        value = ['p1', ]
        self.assertEqual(ImageInfo.format_depicted(value),
                         expected)

    def test_format_depicted_with_few(self):
        expected = u'{{depicted person|p1|p2|p3|style=plain text}}\n'
        value = ['p1', 'p2', 'p3']
        self.assertEqual(ImageInfo.format_depicted(value),
                         expected)

    def test_format_depicted_with_max(self):
        expected = u'{{depicted person|p1|p2|p3|p4|p5|p6|p7|p8|p9|style=plain text}}\n'
        value = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9']
        self.assertEqual(ImageInfo.format_depicted(value),
                         expected)

    def test_format_depicted_with_many(self):
        expected = u'{{depicted person|p1|p2|p3|p4|p5|p6|p7|p8|p9|style=plain text}}\n' \
                   u'{{depicted person|p10|style=plain text}}\n'
        value = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']
        self.assertEqual(ImageInfo.format_depicted(value),
                         expected)

    def test_format_depicted_with_single_and_inv_nr(self):
        expected = u'{{depicted person|p1|style=plain text|comment=invNr}}\n'
        value = ['p1', ]
        self.assertEqual(ImageInfo.format_depicted(value, inv_nr='invNr'),
                         expected)

    def test_format_depicted_with_empty_and_inv_nr(self):
        expected = u''
        value = []
        self.assertEqual(ImageInfo.format_depicted(value, inv_nr='invNr'),
                         expected)

    def test_format_depicted_with_few_and_inv_nr(self):
        expected = u'{{depicted person|p1|p2|p3|style=plain text|comment=invNr}}\n'
        value = ['p1', 'p2', 'p3']
        self.assertEqual(ImageInfo.format_depicted(value, inv_nr='invNr'),
                         expected)

    def test_format_depicted_with_many_and_inv_nr(self):
        expected = u'{{depicted person|p1|p2|p3|p4|p5|p6|p7|p8|p9|style=plain text|comment=invNr}}\n' \
                   u'{{depicted person|p10|style=plain text|comment=invNr}}\n'
        value = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10']
        self.assertEqual(ImageInfo.format_depicted(value, inv_nr='invNr'),
                         expected)


class TestFormatCategory(unittest.TestCase):
    """Test ImageInfo.format_category()"""

    def setUp(self):
        self.caption = u'A caption'
        self.image_info = ImageInfo()
        self.image_info.categories = []

    def assert_same_category_content(self, actual, expected):
        """Assert that a category block is same, up to order of its entries."""
        actual_lines = actual.split('\n')
        expected_lines = expected.split('\n')
        # check first line
        self.assertEqual(actual_lines[0], expected_lines[0])
        # check contents of rest irrespective of order
        self.assertItemsEqual(actual_lines[1:], expected_lines[1:])

    def test_format_category_empty(self):
        expected_text = ''
        expected_printed = []
        self.assertEqual(
            self.image_info.format_category(self.caption, []),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)

    def test_format_category_single(self):
        expected_text = u'\n<!--A caption-->\n' \
                        u'[[Category:Cat]]\n'
        expected_printed = ['Cat']
        categories = ['Cat']
        self.assertEqual(
            self.image_info.format_category(self.caption, categories),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)

    def test_format_category_duplicate(self):
        """Ensure internal duplicates are not outputted."""
        expected_text = u'\n<!--A caption-->\n' \
                        u'[[Category:Cat]]\n'
        expected_printed = ['Cat']
        categories = ['Cat', 'Cat']
        self.assertEqual(
            self.image_info.format_category(self.caption, categories),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)

    def test_format_category_reprint(self):
        """Ensure already outputted categories are not re-outputted."""
        expected_text = ''
        expected_printed = ['Cat']
        self.image_info.categories = ['Cat']
        categories = ['Cat', ]
        self.assertEqual(
            self.image_info.format_category(self.caption, categories),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)

    def test_format_category_multiple(self):
        expected_text = u'\n<!--A caption-->\n' \
                        u'[[Category:Cat1]]\n' \
                        u'[[Category:Cat2]]\n' \
                        u'[[Category:Cat3]]\n'
        expected_printed = ['Cat1', 'Cat2', 'Cat3']
        categories = ['Cat1', 'Cat2', 'Cat3']
        self.assert_same_category_content(
            self.image_info.format_category(self.caption, categories),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)

    def test_format_category_with_prefix(self):
        expected_text = u'\n<!--A caption-->\n' \
                        u'[[Category:Prefix-Cat1]]\n' \
                        u'[[Category:Prefix-Cat2]]\n'
        expected_printed = ['Cat1', 'Cat2']
        categories = ['Cat1', 'Cat2']
        prefix = u'Prefix-'
        self.assert_same_category_content(
            self.image_info.format_category(self.caption, categories,
                                            prefix=prefix),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)

    def test_format_category_no_de_duplication(self):
        expected_text = u'\n<!--A caption-->\n' \
                        u'[[Category:Cat1]]\n' \
                        u'[[Category:Cat2]]\n'
        expected_printed = []
        categories = ['Cat1', 'Cat1', 'Cat2']
        self.assert_same_category_content(
            self.image_info.format_category(self.caption, categories,
                                            de_duplicate=False),
            expected_text)
        self.assertItemsEqual(self.image_info.categories, expected_printed)


class TestProcessCategories(unittest.TestCase):
    """Test ImageInfo.process_categories()."""

    def setUp(self):
        self.image_info = ImageInfo()
        self.image_info.meta_categories = []
        self.image_info.obj_data = dict.fromkeys(
            [u'cat_event', u'cat_artist', u'cat_depicted', u'cat_obj'])

    def runAsserts(self, expected_output, expected_cats, expected_meta_cats):
        """Hide complicated paths needed for asserts."""
        expected_output = '\n%s\n' % expected_output  # make input easier
        self.assertEqual(self.image_info.categories_as_text, expected_output)
        self.assertItemsEqual(self.image_info.categories, expected_cats)
        self.assertItemsEqual(self.image_info.meta_categories,
                              expected_meta_cats)

    def test_process_categories_only_meta_adds_meta(self):
        """Only meta triggers "without cats", and is not added to cats."""
        expected_output = \
            '<!--Maintanance categories-->\n'\
            '[[Category:Media contributed by LSH: without any categories]]\n'\
            '[[Category:Media contributed by LSH: meta_1]]'
        expected_cats = []
        expected_meta_cats = ['meta_1', 'without any categories']
        self.image_info.meta_categories = ['meta_1']
        self.image_info.process_categories(None, None),
        self.runAsserts(expected_output, expected_cats, expected_meta_cats)

    def test_process_categories_only_photographer_adds_meta(self):
        """Only photographer triggers "without cats", but is added to cats."""
        expected_output = \
            '<!--Photographer category-->\n' \
            '[[Category:cat_photographer]]\n\n' \
            '<!--Maintanance categories-->\n'\
            '[[Category:Media contributed by LSH: without any categories]]'
        expected_cats = ['cat_photographer']
        expected_meta_cats = ['without any categories']
        self.image_info.process_categories(None, 'cat_photographer'),
        self.runAsserts(expected_output, expected_cats, expected_meta_cats)

    def test_process_categories_stich_cats(self):
        """Stich does not triggers "without cats", but is added to cats."""
        expected_output = \
            '<!--Photograph categories-->\n'\
            '[[Category:stich_1]]\n'\
            '[[Category:stich_2]]'
        expected_cats = ['stich_1', 'stich_2']
        expected_meta_cats = []
        self.image_info.process_categories(['stich_1', 'stich_2'], None),
        self.runAsserts(expected_output, expected_cats, expected_meta_cats)

    def test_process_categories_all_obj_data(self):
        """Test full obj_data category structure."""
        expected_output = \
            '<!--Event categories-->\n'\
            '[[Category:event_1]]\n\n'\
            '<!--Artist categories-->\n'\
            '[[Category:artist_1]]\n\n'\
            '<!--Depicted categories-->\n'\
            '[[Category:depicted_1]]\n\n'\
            '<!--Object categories-->\n'\
            '[[Category:obj_2]]\n'\
            '[[Category:obj_1]]'
        expected_cats = ['event_1', 'artist_1', 'depicted_1', 'obj_1', 'obj_2']
        expected_meta_cats = []
        self.image_info.obj_data = {
            u'cat_event': ['event_1'],
            u'cat_artist': ['artist_1'],
            u'cat_depicted': ['depicted_1'],
            u'cat_obj': ['obj_1', 'obj_2']
        }
        self.image_info.process_categories(None, None),
        self.runAsserts(expected_output, expected_cats, expected_meta_cats)


class TestMakeGallery(unittest.TestCase):
    """Test MakeInfo.make_gallery()."""

    def setUp(self):
        self.title = u'galleryTitle'
        self.printed = []

    def assert_same_gallery_content(self, actual, expected):
        """Assert that gallery is same, up to order its entries."""
        actual_lines = actual.split('\n')
        expected_lines = expected.split('\n')
        # check first and last line
        self.assertEqual(actual_lines[0], expected_lines[0])
        self.assertEqual(actual_lines[-1], expected_lines[-1])
        # check contents of rest irrespective of order
        self.assertItemsEqual(actual_lines[1:-1], expected_lines[1:-1])

    def test_make_gallery_empty(self):
        expected_gallery = ''
        expected_printed = []
        self.assertEqual(MakeInfo.make_gallery(self.title, [], self.printed),
                         expected_gallery)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_gallery_single(self):
        expected_gallery = u'\n<gallery caption="galleryTitle">\n' \
                           u'File:foo.jpg\n' \
                           u'</gallery>'
        expected_printed = ['foo.jpg']
        files = ['foo.jpg']
        self.assertEqual(
            MakeInfo.make_gallery(self.title, files, self.printed),
            expected_gallery)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_gallery_duplicate(self):
        """Ensure internal duplicates are not outputted."""
        expected_gallery = u'\n<gallery caption="galleryTitle">\n' \
                           u'File:foo.jpg\n' \
                           u'</gallery>'
        expected_printed = ['foo.jpg']
        files = ['foo.jpg', 'foo.jpg']
        self.assertEqual(
            MakeInfo.make_gallery(self.title, files, self.printed),
            expected_gallery)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_gallery_reprint(self):
        """Ensure already outputted images are not re-outputted."""
        expected_gallery = ''
        expected_printed = ['foo.jpg']
        self.printed = ['foo.jpg']
        files = ['foo.jpg', ]
        self.assertEqual(
            MakeInfo.make_gallery(self.title, files, self.printed),
            expected_gallery)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_gallery_multiple(self):
        expected_gallery = u'\n<gallery caption="galleryTitle">\n' \
                           u'File:foo1.jpg\n' \
                           u'File:foo2.jpg\n' \
                           u'File:foo3.jpg\n' \
                           u'</gallery>'
        expected_printed = ['foo1.jpg', 'foo2.jpg', 'foo3.jpg']
        files = ['foo1.jpg', 'foo2.jpg', 'foo3.jpg']
        self.assert_same_gallery_content(
            MakeInfo.make_gallery(self.title, files, self.printed),
            expected_gallery)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_gallery_captions(self):
        expected_gallery = u'\n<gallery caption="galleryTitle">\n' \
                           u'File:foo1.jpg|The foo\n' \
                           u'File:foo2.jpg|The bar\n' \
                           u'</gallery>'
        expected_printed = ['foo1.jpg', 'foo2.jpg']
        files = ['foo1.jpg', 'foo2.jpg']
        captions = {u'foo1.jpg': u'The foo',
                    u'foo2.jpg': u'The bar'}
        self.assert_same_gallery_content(
            MakeInfo.make_gallery(self.title, files, self.printed,
                                  captions=captions),
            expected_gallery)
        self.assertItemsEqual(self.printed, expected_printed)


class TestFormatPerson(unittest.TestCase):
    """Test MakeInfo.format_person()."""

    def setUp(self):
        self.mock_info = mock.create_autospec(MakeInfo)
        self.cat_meta = []
        self.kuenstler = None
        self.reset_kuenstler_params()

        self.mock_info.kuenstlerD = {'123': self.kuenstler}
        self.mock_info.peopleCreatC = {}
        self.mock_info.peopleLinkC = {}

    def unset_kuenstler_params(self, params=None):
        """Removes the given parameters from self.kuenstler."""
        if not params:
            params = self.kuenstler.keys()
        for p in params:
            self.kuenstler[p] = ''

    def reset_kuenstler_params(self, params=None):
        """Re-add the given parameters to self.kuenstler."""
        kuenstler = {
            'KueVorNameS': 'FirstName',
            'KueNameS': 'LastName',
            'KudJahrVonL': 'BirthYear',
            'KudJahrBisL': 'DeathYear',
            'KueFunktionS': 'Profession',
            'KudOrtS': 'City',
            'KudLandS': 'Country'
        }
        if not params:
            self.kuenstler = kuenstler.copy()
        else:
            for p in params:
                self.kuenstler[p] = kuenstler[p]

    def test_format_person_empty_returns_empty(self):
        expected_name = ''
        expected_cat_meta = []
        self.unset_kuenstler_params()
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_full_info(self):
        expected_name = 'FirstName LastName (Profession, BirthYear-DeathYear) ' \
                        'City, Country'
        expected_cat_meta = []

        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_only_name(self):
        expected_name = 'FirstName LastName'
        expected_cat_meta = []

        self.unset_kuenstler_params(
            ['KudJahrVonL', 'KudJahrBisL', 'KueFunktionS',
             'KudOrtS', 'KudLandS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_no_bracket(self):
        expected_name = 'FirstName LastName, City, Country'
        expected_cat_meta = []

        self.unset_kuenstler_params(
            ['KudJahrVonL', 'KudJahrBisL', 'KueFunktionS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_no_place(self):
        expected_name = 'FirstName LastName (Profession, BirthYear-DeathYear)'
        expected_cat_meta = []

        self.unset_kuenstler_params(
            ['KudOrtS', 'KudLandS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_various_brackets(self):
        """Test various variations of bracket contents."""
        expected_cat_meta = []

        # all
        expected_name = '(Profession, BirthYear-DeathYear)'
        self.unset_kuenstler_params(
            ['KueVorNameS', 'KueNameS', 'KudOrtS', 'KudLandS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Profession only
        expected_name = '(Profession)'
        self.unset_kuenstler_params(['KudJahrVonL', 'KudJahrBisL'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Year only
        expected_name = '(BirthYear-DeathYear)'
        self.unset_kuenstler_params(['KueFunktionS'])
        self.reset_kuenstler_params(['KudJahrVonL', 'KudJahrBisL'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Birth year range only
        expected_name = '(BirthYear-)'
        self.unset_kuenstler_params(['KudJahrBisL'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Death year range only
        expected_name = '(-DeathYear)'
        self.unset_kuenstler_params(['KudJahrVonL'])
        self.reset_kuenstler_params(['KudJahrBisL'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Year range and profession only
        expected_name = '(Profession, -DeathYear)'
        self.reset_kuenstler_params(['KueFunktionS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Assert none of these added to cat_meta
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_various_places_appendix(self):
        """Test various variations of place appendix."""
        expected_cat_meta = []

        # all
        expected_name = 'City, Country'
        self.unset_kuenstler_params(
            ['KueVorNameS', 'KueNameS', 'KudJahrVonL', 'KudJahrBisL',
             'KueFunktionS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # City only
        expected_name = 'City'
        self.unset_kuenstler_params(['KudLandS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Country only
        expected_name = 'Country'
        self.unset_kuenstler_params(['KudOrtS'])
        self.reset_kuenstler_params(['KudLandS'])
        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)

        # Assert none of these added to cat_meta
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_matching_creator(self):
        expected_name = '{{Creator:Some template}}'
        expected_cat_meta = []
        self.mock_info.peopleCreatC = {'123': 'Creator:Some template'}

        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta,
                                   creative=True),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_matching_creator_not_creative(self):
        expected_name = 'FirstName LastName (Profession, BirthYear-DeathYear) ' \
                        'City, Country'
        expected_cat_meta = []
        self.mock_info.peopleCreatC = {'123': 'Creator:Some template'}

        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_trigger_cat_meta(self):
        expected_name = 'FirstName LastName (Profession, BirthYear-DeathYear) ' \
                        'City, Country'
        expected_cat_meta = ['unmatched creator']
        self.mock_info.peopleCreatC = {'123': ''}

        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta,
                                   creative=True),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_matching_link(self):
        expected_name = '[[:sv:Some link|FirstName LastName]]'
        expected_cat_meta = []
        self.mock_info.peopleLinkC = {'123': ':sv:Some link'}

        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)

    def test_format_person_creator_over_link(self):
        """Test that creator template is prioritised over link."""
        expected_name = '{{Creator:Some template}}'
        expected_cat_meta = []
        self.mock_info.peopleCreatC = {'123': 'Creator:Some template'}
        self.mock_info.peopleLinkC = {'123': ':sv:Some link'}

        self.assertEqual(
            MakeInfo.format_person(self.mock_info, '123', self.cat_meta,
                                   creative=True),
            expected_name)
        self.assertItemsEqual(self.cat_meta, expected_cat_meta)
