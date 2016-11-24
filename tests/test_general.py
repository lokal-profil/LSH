#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Should ideally beexcluded from contributing to coverage.
#
import codecs
import os
import py_crunchCSVData as Crunch
import py_makeMappings as Mappings
import py_filenames as Filenames
import py_prepUpload as Prep
import py_listscraper as Listscraper
import shutil
import unittest
CSV_CONFIG = u'tests/mock_data/csv_config.json'
DIR_CLEAN = u'tests/mock_data/clean_csv'
DIR_DATA = u'tests/mock_data/data'
DIR_MAPPINGS = u'tests/mock_data/mappings'
DIR_OLD_CONNECTIONS = u'tests/mock_data/old_connections'
DIR_CONNECTIONS = u'tests/mock_data/connections'
DIR_LISTSCRAPE_INPUT = u'tests/mock_data/listscrape/input'
DIR_LISTSCRAPE_OUTPUT = u'tests/mock_data/listscrape/output'
DIR_IMAGES = u'tests/mock_data/images'
DIR_IMAGES_FOLDERS_INPUT = u'tests/mock_data/image_folders/input'
DIR_IMAGES_FOLDERS_OUTPUT = u'tests/mock_data/image_folders/output'
DIR_IMAGES_INFO = u'tests/mock_data/images_info'
DIR_NEGATIVES_INPUT = u'tests/mock_data/negatives/input/'
DIR_NEGATIVES_OUTPUT = u'tests/mock_data/negatives/output/'
COMMONS_PREFIX = u'User:LSHuploadBot/testdata'
DIR_TMP = u'tests/tmp'


def sort_anything_list_like(row, col_delim='|', list_delim=';'):
    """
    Look for list-like things and sort them given a csv.

    :param row: text to parse
    :param col_delim: delimiter for separating columns
    :param list_delim: delimiter used in lists
    :return: str
    """
    parts = row.split(col_delim)
    for i, e in enumerate(parts):
        components = e.split(list_delim)
        parts[i] = list_delim.join(sorted(components))
    return col_delim.join(parts)


def get_contents(filename, path):
    """
    Open a file and returns the contents.

    :param filename: the filename to open
    :param path: path to the filename
    :return: str
    """
    filename = os.path.join(path, filename)
    f = codecs.open(filename, 'r', 'utf-8')
    return f.read()


def get_lines(filename, path):
    """
    Open a file and returns the containing lines.

    :param filename: the filename to open
    :param path: path to the filename
    :return: list
    """
    return get_contents(filename, path).split('\n')


def get_clean_file_tree(startpath):
    """
    Return os.walk but with the root scrubbed from the output.

    :param startpath: path to start walk at
    :return: list
    """
    tree = []
    for root, dirs, files in os.walk(startpath):
        root = root.replace(startpath, '')
        tree.append((root, dirs, files))
    return tree


def get_files(path, file_exts):
    """
    Return all filenames in a directory with a given extension(s).

    :param path: path to directory to llok in
    :param fileExts: str|tuple of file endings (incl. ".")
    :return: list
    """
    if isinstance(file_exts, (str, unicode)):
        file_exts = (file_exts, )

    requested_files = []
    for filename in os.listdir(path):
        if os.path.splitext(filename)[1].lower() in file_exts:
            requested_files.append(filename)
    return requested_files


class TestGeneral(unittest.TestCase):

    """
    Testing suite for the general steps involved in the upload preparation.

    This only tests the big overall functions rather than any individual ones.
    Furthermore it is primarily intended to check if a code change leads to
    a change in the output, rather than if the output is actually correct.
    """

    def assert_items_equal_with_lists(self, a, b):
        """
        Compare two lists and checks that they are equal, up to the order
        of the lines, and the order of any lists.

        :param a: a list
        :param b: a list
        """
        diff_old = list(set(a) - set(b))
        diff_new = list(set(b) - set(a))
        for i, e in enumerate(diff_old):
            diff_old[i] = sort_anything_list_like(e)
        for i, e in enumerate(diff_new):
            diff_new[i] = sort_anything_list_like(e)
        self.assertItemsEqual(diff_new, diff_old)

    def assert_file_structure_equal(self, expected_dir, temp_dir):
        """Compare the file strucuture of two directories."""
        expected = get_clean_file_tree(expected_dir)
        actual = get_clean_file_tree(temp_dir)
        self.longMessage = True
        self.assertEquals(expected, actual, msg="File structure differs")

    def assert_file_contents_equal(self, expected_dir, temp_dir, exts):
        """Compare file contents for all files in two directories.

        :param exts: file ending string or tuple of such
        """
        # self.maxDiff = None # toggle to gett full diff
        # check info file contents
        files = get_files(expected_dir, exts)
        for f in files:
            expected = get_contents(f, expected_dir)
            actual = get_contents(f, temp_dir)
            self.assertEquals(expected, actual,
                              msg="File contents differ for %s" % f)

    def tearDown(self):
        # clean up
        shutil.rmtree(DIR_TMP)

    def test_crunch(self):
        """Check that crunching the files gives the right results."""
        files = (
            'photo_multimedia_etc.csv', 'stichwort_trim.csv',
            'objMass_trim.csv', 'objMultiple_trim.csv', 'objDaten_etc.csv',
            'ausstellung_trim.csv', 'ereignis_trim.csv', 'kuenstler_trim.csv',
            'photoAll.csv')
        Crunch.helpers.VERBOSE = False  # otherwise crunch stops at prompt
        Crunch.run(in_path=DIR_CLEAN, out_path=DIR_TMP)
        for f in files:
            expected = get_lines(f, DIR_DATA)
            actual = get_lines(f, DIR_TMP)
            try:
                self.assert_items_equal_with_lists(expected, actual)
            except AssertionError:
                print u'test_crunch failed for %s' % f
                raise

    def test_mappings(self):
        """Check that creating the mappings gives the right results."""
        files = (
            'Events.txt', 'Keywords.txt', 'Materials.txt', 'ObjKeywords.txt',
            'People.txt', 'Photographers.txt', 'Places.txt')
        Mappings.CSV_CONFIG = CSV_CONFIG  # override default in a dirty way
        Mappings.run(in_path=DIR_OLD_CONNECTIONS,
                     out_path=DIR_TMP, data_path=DIR_DATA)
        for f in files:
            expected = get_lines(f, DIR_MAPPINGS)
            actual = get_lines(f, DIR_TMP)
            try:
                self.assert_items_equal_with_lists(expected, actual)
            except AssertionError:
                print u'test_mappings failed for %s' % f
                raise

    def test_filenames(self):
        """
        Check that creating filenames gives the right results.

        @toDO: Add something triggering <span>
        """
        Filenames.run(folder=DIR_DATA, mapping=DIR_TMP, outfolder=DIR_TMP)

        # test mapping
        f = 'Filenames.txt'
        expected = get_lines(f, DIR_MAPPINGS)
        actual = get_lines(f, DIR_TMP)
        try:
            self.assertItemsEqual(expected, actual)
        except AssertionError:
            print u'test_filenames failed for %s' % f
            raise

        # test data
        f = u'filenames.csv'
        expected = get_lines(f, DIR_DATA)
        actual = get_lines(f, DIR_TMP)
        try:
            self.assertItemsEqual(expected, actual)
        except AssertionError:
            print u'test_filenames failed for %s' % f
            raise

    def test_listscraper(self):
        """Check that scraping lists gives the right results."""
        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_LISTSCRAPE_INPUT, DIR_TMP)

        # run test
        Listscraper.run(outPath=DIR_TMP, dataPath=DIR_TMP,
                        mappingsPath=DIR_TMP, commonsPrefix=COMMONS_PREFIX)

        # check file structure
        self.assert_file_structure_equal(DIR_LISTSCRAPE_OUTPUT, DIR_TMP)

        # check info file contents
        self.assert_file_contents_equal(DIR_LISTSCRAPE_OUTPUT, DIR_TMP,
                                        ('.csv', '.txt'))

    def test_move_hits(self):
        """Check that finding and moving images gives the right results."""
        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_IMAGES_FOLDERS_INPUT, DIR_TMP)
        shutil.copyfile(os.path.join(DIR_DATA, u'filenames.noExts.csv'),
                        os.path.join(DIR_TMP, u'filenames.csv'))

        # run test
        filename_file = os.path.join(DIR_TMP, u'filenames.csv')
        Prep.moveHits(DIR_TMP, filename_file)

        # check file structure
        self.assert_file_structure_equal(DIR_IMAGES_FOLDERS_OUTPUT, DIR_TMP)

        # test extension data
        expected = get_lines(u'filenames.Exts.csv', DIR_DATA)
        actual = get_lines(u'filenames.csv', DIR_TMP)
        try:
            self.assertItemsEqual(expected, actual)
        except AssertionError:
            print u'test_moveHits failed for filenames.csv'
            raise

    def test_make_info_and_rename(self):
        """Check that creating filenames gives the right results."""
        # copy with Exts filename file to filenames.csv
        shutil.copyfile(os.path.join(DIR_DATA, u'filenames.Exts.csv'),
                        os.path.join(DIR_DATA, u'filenames.csv'))

        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_IMAGES, DIR_TMP)

        # run test
        filename_file = os.path.join(DIR_DATA, u'filenames.csv')
        Prep.makeAndRename(DIR_TMP, batch_cat=u'2015-11',
                           data_dir=DIR_DATA, connections_dir=DIR_CONNECTIONS,
                           filename_file=filename_file)

        # check file structure
        self.assert_file_structure_equal(DIR_IMAGES_INFO, DIR_TMP)
        # check info file contents
        self.assert_file_contents_equal(DIR_IMAGES_INFO, DIR_TMP, '.info')

        # clean up
        # copy with NoExts filename file back
        shutil.copyfile(os.path.join(DIR_DATA, u'filenames.noExts.csv'),
                        os.path.join(DIR_DATA, u'filenames.csv'))

    def test_make_negatives(self):
        """Check that creating negatives gives the right results."""
        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_NEGATIVES_INPUT, DIR_TMP)

        # run test
        Prep.negatives(DIR_TMP)
        # check file structure
        self.assert_file_structure_equal(DIR_NEGATIVES_OUTPUT, DIR_TMP)
        # check info file contents
        self.assert_file_contents_equal(DIR_NEGATIVES_OUTPUT, DIR_TMP, '.info')
