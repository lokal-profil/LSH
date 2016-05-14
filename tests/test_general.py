#!/usr/bin/python
# -*- coding: UTF-8  -*-
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


def sortAnythingListlike(row, colDelimiter='|', listDelimiter=';'):
    """
    Given a csv row. Look for list-like things and sort them
    :param row: text to parse
    :param colDelimiter: delimiter for separating columns
    :param listDelimiter: delimiter used in lists
    :return: str
    """
    parts = row.split(colDelimiter)
    for i, e in enumerate(parts):
        components = e.split(listDelimiter)
        parts[i] = listDelimiter.join(sorted(components))
    return colDelimiter.join(parts)


def getContents(filename, path):
    """
    Opens a file and returns the contents
    :param filename: the filename to open
    :param path: path to the filename
    :return: str
    """
    filename = os.path.join(path, filename)
    f = codecs.open(filename, 'r', 'utf-8')
    return f.read()


def getLines(filename, path):
    """
    Opens a file and returns the containing lines
    :param filename: the filename to open
    :param path: path to the filename
    :return: list
    """
    return getContents(filename, path).split('\n')


def getCleanFileTree(startpath):
    """
    Returns os.walk but with the root scrubbed from the output
    :param startpath: path to start walk at
    :return: list
    """
    tree = []
    for root, dirs, files in os.walk(startpath):
        root = root.replace(startpath, '')
        tree.append((root, dirs, files))
    return tree


def getFiles(path, fileExts):
    """
    Returns all filenames in a directory with a given extension(s)
    :param path: path to directory to llok in
    :param fileExts: str|tuple of file endings (incl. ".")
    :return: list
    """
    if isinstance(fileExts, (str, unicode)):
        fileExts = (fileExts, )

    requestedFiles = []
    for filename in os.listdir(path):
        if os.path.splitext(filename)[1].lower() in fileExts:
            requestedFiles.append(filename)
    return requestedFiles


class TestGeneral(unittest.TestCase):

    """
    Testing suite for the general steps involved in the upload preparation.

    This only tests the big overall functions rather than any individual ones.
    Furthermore it is primarily intended to check if a code change leads to
    a change in the output, rather than if the output is actually correct.
    """

    def assertEqualUpToOrder(self, a, b):
        """
        compares two lists and checks that they are equal, up to the order
        of the lines
        :param a: a list
        :param b: a list
        """
        diff1 = set(a) - set(b)
        diff2 = set(b) - set(a)
        num = len(diff1) + len(diff2)
        if num != 0:
            raise AssertionError("Lists differ by %d entries" % num)

    def assertEqualUpToOrderWithLists(self, a, b):
        """
        compares two lists and checks that they are equal, up to the order
        of the lines, and the order of any lists
        :param a: a list
        :param b: a list
        """
        diff_old = list(set(a) - set(b))
        diff_new = list(set(b) - set(a))
        for i, e in enumerate(diff_old):
            diff_old[i] = sortAnythingListlike(e)
        for i, e in enumerate(diff_new):
            diff_new[i] = sortAnythingListlike(e)
        self.assertEqualUpToOrder(diff_new, diff_old)

    def assertFileStructure(self, expected_dir, temp_dir):
        """Compare the file strucuture of two directories."""
        expected = getCleanFileTree(expected_dir)
        actual = getCleanFileTree(temp_dir)
        try:
            self.assertEquals(expected, actual)
        except AssertionError as e:
            e.message = "Tree structure differs: %s" % e.message
            raise

    def assertFileContents(self, expected_dir, temp_dir, exts):
        """Compare file contents for all files in two directories.
        :param exts: file ending string or tuple of such
        """
        # check info file contents
        files = getFiles(expected_dir, exts)
        for f in files:
            expected = getContents(f, expected_dir)
            actual = getContents(f, temp_dir)
            try:
                self.assertEquals(expected, actual)
            except AssertionError as e:
                e.message = "File contents differ for %s: %s" % (f, e.message)
                raise

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
            expected = getLines(f, DIR_DATA)
            actual = getLines(f, DIR_TMP)
            try:
                self.assertEqualUpToOrderWithLists(expected, actual)
            except AssertionError:
                print u'test_crunch failed for %s' % f
                raise

    def test_mappings(self):
        """
        Checks that creating the mappings gives the right results
        """
        files = (
            'Events.txt', 'Keywords.txt', 'Materials.txt', 'ObjKeywords.txt',
            'People.txt', 'Photographers.txt', 'Places.txt')
        Mappings.CSV_CONFIG = CSV_CONFIG  # override default in a dirty way
        Mappings.run(in_path=DIR_OLD_CONNECTIONS,
                     out_path=DIR_TMP, data_path=DIR_DATA)
        for f in files:
            expected = getLines(f, DIR_MAPPINGS)
            actual = getLines(f, DIR_TMP)
            try:
                self.assertEqualUpToOrderWithLists(expected, actual)
            except AssertionError:
                print u'test_mappings failed for %s' % f
                raise

    def test_filenames(self):
        """
        Checks that creating filenames gives the right results
        @toDO: Add something triggering <span>
        """
        Filenames.run(folder=DIR_DATA, mapping=DIR_TMP, outfolder=DIR_TMP)

        # test mapping
        f = 'Filenames.txt'
        expected = getLines(f, DIR_MAPPINGS)
        actual = getLines(f, DIR_TMP)
        try:
            self.assertEqualUpToOrder(expected, actual)
        except AssertionError:
            print u'test_filenames failed for %s' % f
            raise

        # test data
        f = u'filenames.csv'
        expected = getLines(f, DIR_DATA)
        actual = getLines(f, DIR_TMP)
        try:
            self.assertEqualUpToOrder(expected, actual)
        except AssertionError:
            print u'test_filenames failed for %s' % f
            raise

    def test_listscraper(self):
        """
        Checks that scraping lists gives the right results
        """
        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_LISTSCRAPE_INPUT, DIR_TMP)

        # run test
        Listscraper.run(outPath=DIR_TMP, dataPath=DIR_TMP,
                        mappingsPath=DIR_TMP, commonsPrefix=COMMONS_PREFIX)

        # check file structure
        self.assertFileStructure(DIR_LISTSCRAPE_OUTPUT, DIR_TMP)

        # check info file contents
        self.assertFileContents(DIR_LISTSCRAPE_OUTPUT, DIR_TMP,
                                ('.csv', '.txt'))

    def test_moveHits(self):
        """
        Checks that finding and moving images gives the right results
        """
        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_IMAGES_FOLDERS_INPUT, DIR_TMP)
        shutil.copyfile(os.path.join(DIR_DATA, u'filenames.noExts.csv'),
                        os.path.join(DIR_TMP, u'filenames.csv'))

        # run test
        filenameFile = os.path.join(DIR_TMP, u'filenames.csv')
        Prep.moveHits(DIR_TMP, filenameFile)

        # check file structure
        self.assertFileStructure(DIR_IMAGES_FOLDERS_OUTPUT, DIR_TMP)

        # test extension data
        expected = getLines(u'filenames.Exts.csv', DIR_DATA)
        actual = getLines(u'filenames.csv', DIR_TMP)
        try:
            self.assertEqualUpToOrder(expected, actual)
        except AssertionError:
            print u'test_moveHits failed for filenames.csv'
            raise

    def test_makeInfoAndRename(self):
        """
        Checks that creating filenames gives the right results
        """
        # copy with Exts filename file to filenames.csv
        shutil.copyfile(os.path.join(DIR_DATA, u'filenames.Exts.csv'),
                        os.path.join(DIR_DATA, u'filenames.csv'))

        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_IMAGES, DIR_TMP)

        # run test
        filenameFile = os.path.join(DIR_DATA, u'filenames.csv')
        Prep.makeAndRename(DIR_TMP, dataDir=DIR_DATA,
                           connectionsDir=DIR_CONNECTIONS,
                           filenameFile=filenameFile, batchCat=u'2015-11')

        # check file structure
        self.assertFileStructure(DIR_IMAGES_INFO, DIR_TMP)
        # check info file contents
        self.assertFileContents(DIR_IMAGES_INFO, DIR_TMP, '.txt')

        # clean up
        # copy with NoExts filename file back
        shutil.copyfile(os.path.join(DIR_DATA, u'filenames.noExts.csv'),
                        os.path.join(DIR_DATA, u'filenames.csv'))

    def test_makeNegatives(self):
        """
        Checks that creating negatives gives the right results
        """
        # copy mock files to temporary folder since these are changed
        shutil.copytree(DIR_NEGATIVES_INPUT, DIR_TMP)

        # run test
        Prep.negatives(DIR_TMP)
        # check file structure
        self.assertFileStructure(DIR_NEGATIVES_OUTPUT, DIR_TMP)
        # check info file contents
        self.assertFileContents(DIR_NEGATIVES_OUTPUT, DIR_TMP, '.txt')
