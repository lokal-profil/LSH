#!/usr/bin/python
# -*- coding: UTF-8  -*-
import unittest
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


class TestMakeCategory(unittest.TestCase):
    """Test MakeInfo.make_category()"""

    def setUp(self):
        self.caption = u'A caption'
        self.printed = []

    def assert_same_category_content(self, actual, expected):
        """Assert that a category block is same, up to order its entries."""
        actual_lines = actual.split('\n')
        expected_lines = expected.split('\n')
        # check first line
        self.assertEqual(actual_lines[0], expected_lines[0])
        # check contents of rest irrespective of order
        self.assertItemsEqual(actual_lines[1:], expected_lines[1:])

    def test_make_category_empty(self):
        expected_category = ''
        expected_printed = []
        self.assertEqual(
            MakeInfo.make_category(self.caption, [], self.printed),
            expected_category)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_category_single(self):
        expected_category = u'\n<!--A caption-->\n' \
                            u'[[Category:Cat]]\n'
        expected_printed = ['Cat']
        categories = ['Cat']
        self.assertEqual(
            MakeInfo.make_category(self.caption, categories, self.printed),
            expected_category)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_category_duplicate(self):
        """Ensure internal duplicates are not outputted."""
        expected_category = u'\n<!--A caption-->\n' \
                            u'[[Category:Cat]]\n'
        expected_printed = ['Cat']
        categories = ['Cat', 'Cat']
        self.assertEqual(
            MakeInfo.make_category(self.caption, categories, self.printed),
            expected_category)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_category_reprint(self):
        """Ensure already outputted categories are not re-outputted."""
        expected_category = ''
        expected_printed = ['Cat']
        self.printed = ['Cat']
        categories = ['Cat', ]
        self.assertEqual(
            MakeInfo.make_category(self.caption, categories, self.printed),
            expected_category)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_category_multiple(self):
        expected_category = u'\n<!--A caption-->\n' \
                            u'[[Category:Cat1]]\n' \
                            u'[[Category:Cat2]]\n' \
                            u'[[Category:Cat3]]\n'
        expected_printed = ['Cat1', 'Cat2', 'Cat3']
        categories = ['Cat1', 'Cat2', 'Cat3']
        self.assert_same_category_content(
            MakeInfo.make_category(self.caption, categories, self.printed),
            expected_category)
        self.assertItemsEqual(self.printed, expected_printed)

    def test_make_category_with_prefix(self):
        expected_category = u'\n<!--A caption-->\n' \
                            u'[[Category:Prefix-Cat1]]\n' \
                            u'[[Category:Prefix-Cat2]]\n'
        expected_printed = ['Cat1', 'Cat2']
        categories = ['Cat1', 'Cat2']
        prefix = u'Prefix-'
        self.assert_same_category_content(
            MakeInfo.make_category(self.caption, categories, self.printed,
                                   prefix=prefix),
            expected_category)
        self.assertItemsEqual(self.printed, expected_printed)
