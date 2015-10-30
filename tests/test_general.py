#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# A testing suite for the general steps involved in the upload preparation
# This only tests the big overall functions rather than any individual ones.
# Furthermore it is primarily intended to check if a code change leads to
# a change in the output, rather than if the output is actually correct.
#
import codecs
import os
import py_crunchCSVData as Crunch
import py_makeMappings as Mappings
import py_filenames as Filenames
import py_prepUpload as Prep
import shutil
import helpers
DIR_CLEAN = u'tests/mock_data/clean_csv'
DIR_DATA = u'tests/mock_data/data'
DIR_MAPPINGS = u'tests/mock_data/mappings'
DIR_OLD_CONNECTIONS = u'tests/mock_data/old_connections'
DIR_CONNECTIONS = u'tests/mock_data/connections'
DIR_IMAGES = u'tests/mock_data/images'
DIR_IMAGES_FOLDERS_INPUT = u'tests/mock_data/image_folders/input'
DIR_IMAGES_FOLDERS_OUTPUT = u'tests/mock_data/image_folders/output'
DIR_IMAGES_INFO = u'tests/mock_data/images_info'
DIR_NEGATIVES_INPUT = u'tests/mock_data/negatives/input/'
DIR_NEGATIVES_OUTPUT = u'tests/mock_data/negatives/output/'
DIR_TMP = u'tests/tmp'


def areEqualUpToOrder(a, b):
    """
    compares two lists and checks that they are equal, up to the order
    of the lines
    :param a: a list
    :param b: a list
    :returns: bool
    """
    diff1 = set(a) - set(b)
    diff2 = set(b) - set(a)
    return (len(diff1) + len(diff2)) == 0


def areEqualUpToOrderWithLists(a, b):
    """
    compares two lists and checks that they are equal, up to the order
    of the lines, and the order of any lists
    :param a: a list
    :param b: a list
    :returns: bool
    """
    diff_old = list(set(a) - set(b))
    diff_new = list(set(b) - set(a))
    for i in range(len(diff_old)):
        diff_old[i] = sortAnythingListlike(diff_old[i])
    for i in range(len(diff_new)):
        diff_new[i] = sortAnythingListlike(diff_new[i])
    return areEqualUpToOrder(diff_new, diff_old)


def sortAnythingListlike(row, colDelimiter='|', listDelimiter=';'):
    """
    Given a csv row. Look for list-like things and sort them
    :param row: text to parse
    :param colDelimiter: delimiter for separating columns
    :param listDelimiter: delimiter used in lists
    :returns: str
    """
    parts = row.split(colDelimiter)
    for i in range(len(parts)):
        components = parts[i].split(listDelimiter)
        parts[i] = listDelimiter.join(sorted(components))
    return colDelimiter.join(parts)


def getContents(filename, path):
    """
    Opens a file and returns the contents
    :param filename: the filename to open
    :param path: path to the filename
    :returns: str
    """
    filename = os.path.join(path, filename)
    f = codecs.open(filename, 'r', 'utf-8')
    return f.read()


def getLines(filename, path):
    """
    Opens a file and returns the containing lines
    :param filename: the filename to open
    :param path: path to the filename
    :returns: list
    """
    return getContents(filename, path).split('\n')


def getCleanFileTree(startpath):
    """
    Returns os.walk but with the root scrubbed from the output
    :param startpath: path to start walk at
    :returns: list
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
    :param fileExts: str|tupple of file endings (incl. ".")
    :returns: list
    """
    if isinstance(fileExts, (str, unicode)):
        fileExts = (fileExts, )

    requestedFiles = []
    for filename in os.listdir(path):
        if os.path.splitext(filename)[1].lower() in fileExts:
            requestedFiles.append(filename)
    return requestedFiles


def test_crunch(func):
    """
    Check that crunching the files gives the right results
    """
    files = ('photo_multimedia_etc.csv', 'stichwort_trim.csv',
             'objMass_trim.csv', 'objMultiple_trim.csv', 'objDaten_etc.csv',
             'ausstellung_trim.csv', 'ereignis_trim.csv', 'kuenstler_trim.csv',
             'photoAll.csv')
    func(in_path=DIR_CLEAN, out_path=DIR_TMP)
    for f in files:
        expected = getLines(f, DIR_DATA)
        actual = getLines(f, DIR_TMP)
        if not areEqualUpToOrderWithLists(expected, actual):
            print u'test_crunch failed for %s' % f

    # clean up
    shutil.rmtree(DIR_TMP)


def test_mappings(func):
    """
    Checks that creating the mappings gives the right results
    """
    files = ('Events.txt', 'Keywords.txt', 'Materials.txt', 'ObjKeywords.txt',
             'People.txt', 'Photographers.txt', 'Places.txt')
    func(in_path=DIR_OLD_CONNECTIONS, out_path=DIR_TMP, data_path=DIR_DATA)
    for f in files:
        expected = getLines(f, DIR_MAPPINGS)
        actual = getLines(f, DIR_TMP)
        if not areEqualUpToOrderWithLists(expected, actual):
            print u'test_mappings failed for %s' % f

    # clean up
    shutil.rmtree(DIR_TMP)


def test_filenames(func):
    """
    Checks that creating filenames gives the right results
    """
    func(folder=DIR_DATA, mapping=DIR_TMP, outfolder=DIR_TMP)

    # test mapping
    f = 'Filenames.txt'
    expected = getLines(f, DIR_MAPPINGS)
    actual = getLines(f, DIR_TMP)
    if not areEqualUpToOrder(expected, actual):
        print u'test_filenames failed for %s' % f

    # test data
    f = u'filenames.csv'
    expected = getLines(f, DIR_DATA)
    actual = getLines(f, DIR_TMP)
    if not areEqualUpToOrder(expected, actual):
        print u'test_filenames failed for %s' % f

    # clean up
    shutil.rmtree(DIR_TMP)


def test_moveHits(func):
    """
    Checks that finding and moving images gives the right results
    """
    # copy mock files to temporary folder since these are changed
    shutil.copytree(DIR_IMAGES_FOLDERS_INPUT, DIR_TMP)
    shutil.copyfile(os.path.join(DIR_DATA, u'filenames.noExts.csv'),
                    os.path.join(DIR_TMP, u'filenames.csv'))

    # run test
    filenameFile = os.path.join(DIR_TMP, u'filenames.csv')
    func(DIR_TMP, filenameFile)

    expected = getCleanFileTree(DIR_IMAGES_FOLDERS_OUTPUT)
    actual = getCleanFileTree(DIR_TMP)
    if not expected == actual:
        print u'test_moveHits failed for tree'

    # test extension data
    expected = getLines(u'filenames.Exts.csv', DIR_DATA)
    actual = getLines(u'filenames.csv', DIR_TMP)
    if not areEqualUpToOrder(expected, actual):
        print u'test_moveHits failed for filenames.csv'

    # clean up
    shutil.rmtree(DIR_TMP)


def test_makeInfoAndRename(func):
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
    func(DIR_TMP, data_dir=DIR_DATA, connections_dir=DIR_CONNECTIONS,
         filename_file=filenameFile, batchCat=u'2015-11')

    # check file structure
    expected = getCleanFileTree(DIR_IMAGES_INFO)
    actual = getCleanFileTree(DIR_TMP)
    if not expected == actual:
        print u'test_makeInfoAndRename failed for tree'

    # check info file contents
    files = getFiles(DIR_IMAGES_INFO, '.txt')
    for f in files:
        expected = getContents(f, DIR_IMAGES_INFO)
        actual = getContents(f, DIR_TMP)
        if not expected == actual:
            print u'test_makeInfoAndRename failed for %s' % f

    # clean up
    # copy with NoExts filename file back
    shutil.copyfile(os.path.join(DIR_DATA, u'filenames.noExts.csv'),
                    os.path.join(DIR_DATA, u'filenames.csv'))
    shutil.rmtree(DIR_TMP)


def test_makeNegatives(func):
    """
    Checks that creating negatives gives the right results
    """
    # copy mock files to temporary folder since these are changed
    shutil.copytree(DIR_NEGATIVES_INPUT, DIR_TMP)

    # run test
    func(DIR_TMP)

    # check file structure
    expected = getCleanFileTree(DIR_NEGATIVES_OUTPUT)
    actual = getCleanFileTree(DIR_TMP)
    if not expected == actual:
        print u'test_makeNegatives failed for tree'

    # check info file contents
    files = getFiles(DIR_NEGATIVES_OUTPUT, '.txt')
    for f in files:
        expected = getContents(f, DIR_NEGATIVES_OUTPUT)
        actual = getContents(f, DIR_TMP)
        if not expected == actual:
            print u'test_makeNegatives failed for %s' % f

    # clean up
    shutil.rmtree(DIR_TMP)


# run tests
helpers.VERBOSE = False
test_crunch(Crunch.run)
test_mappings(Mappings.run)
test_filenames(Filenames.run)
test_moveHits(Prep.moveHits)
test_makeInfoAndRename(Prep.makeAndRename)
test_makeNegatives(Prep.negatives)
