#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Methods comonly shared by the LSH classes
#
# @crunchRedux fork of common.py
# @ToDo: Reuse the common common.py and split off anything LSH specific
#
import codecs
import os
import json  # needed by loadJsonConfig
import urllib2  # needed by urldecode_utf8()
import re  # neeeded by external_2_internal_link()
import sys  # needed by convertFromCommandline()
import locale  # needed by convertFromCommandline()
import WikiApi as wikiApi  # needed by openConnection()

VERBOSE = True


def openConnection(configPath, apiClass=wikiApi.WikiApi, verbose=None):
    """
    Open a connection to Commons using the specified config file and apiClass
    :param configPath: path to config.json file
    :param apiClass: apiClass to open a connection with
                     (default: wikiApi.WikiApi)
    :param verbose: set to override global VERBOSE
    :return: wikiApi
    """
    # read in Verbose (cannot use GLOBAL as function default if it changes)
    if verbose is None:
        verbose = VERBOSE

    # load config
    config = loadJsonConfig(configPath)

    # open connections
    scriptIdentity = u'LSHUploader/%s' % config['version']
    wApi = apiClass.setUpApi(user=config['username'],
                             password=config['password'],
                             site=config['com_site'],
                             scriptidentify=scriptIdentity,
                             verbose=verbose)
    return wApi


def open_and_read_file(filename, codec='utf-8'):
    """
    Open and read a file using the provided codec.

    Automatically closes the file on return.

    :param filename: the file to open
    :param codec: the used encoding (defaults to "utf-8")
    """
    with codecs.open(filename, 'r', codec) as f:
        return f.read()


def open_and_write_file(filename, text, codec='utf-8'):
    """
    Open and write to a file using the provided codec.

    Automatically closes the file on return.

    :param filename: the file to open
    :param text: the text to output to the file
    :param codec: the used encoding (defaults to "utf-8")
    """
    with codecs.open(filename, 'w', codec) as f:
        f.write(text)


def open_csv_file(filename, delimiter='|', codec='utf-8'):
    """
    Open a csv file and returns the header row plus following lines.

    :param filename: the file to open
    :param delimiter: the used delimiter (defaults to "|")
    :param codec: the used encoding (defaults to "utf-8")
    :return: tuple(array(str), array(str))
    """
    lines = open_and_read_file(filename, codec).split('\n')
    header = lines.pop(0).split(delimiter)
    return header, lines


def csvFileToDict(filename, keyCol, headerCheck, unique=True, keep=None,
                  lists=None, delimiter='|', listDelimiter=';', codec='utf-8'):
    """
    Open a csv file and returns a dict of dicts, using the header row for keys.

    :param filename: the file to open
    :param keyCol: the (label of the) column to use as a key in the dict
                   str or tuple of strs to combine (with a ":")
    :param headerCheck: a string to check against the header row
    :param unique: if we require that the keys are unique
    :param keep: tuple of columns to keep (defaults to None=all)
    :param lists: tuple of columns to treat as lists (defaults to None=none)
    :param delimiter: the used delimiter (defaults to "|")
    :param listDelimiter: the used delimiter when encountering a list
    :param codec: the used encoding (defaults to "utf-8")
    :return: dict
    """
    if not unique:
        raise NotImplementedError("Please Implement csvFileToDict with "
                                  "unique=False")
    if not isinstance(keyCol, (tuple, str, unicode)):
        raise MyError('keyCol must be tuple or str')

    # load and parse file
    header, lines = open_csv_file(filename, delimiter=delimiter, codec=codec)

    # verify header == headerCheck (including order)
    if headerCheck.split(delimiter) != header:
        raise MyError("Header missmatch.\nExpected: %s\nFound:%s"
                      % (headerCheck, delimiter.join(header)))

    # convert txt key to numeric key
    try:
        keyColNum = None
        if isinstance(keyCol, tuple):
            keyColNum = []
            for key in keyCol:
                keyColNum.append(header.index(key))
            keyColNum = tuple(keyColNum)
        else:
            keyColNum = header.index(keyCol)
    except ValueError:
        raise MyError("keyCol not found in header")

    # set up columns to keep
    cols = None
    if keep is None:
        cols = dict.fromkeys(header)
    else:
        # check all keepers in header
        if any(k not in header for k in keep):
            raise MyError("All 'keep'-columns must be in header")
        cols = dict.fromkeys(keep)
    for c in cols.keys():
        cols[c] = header.index(c)

    # set up listify columns
    listify = {}
    if lists is not None:
        # check all columns in header
        if any(k not in header for k in lists):
            raise MyError("All 'lists'-columns must be in header")
        listify = dict.fromkeys(lists)
    for c in listify.keys():
        listify[c] = header.index(c)

    # load to dict
    d = {}
    for l in lines:
        if not l:
            continue
        parts = l.split(delimiter)

        # set key
        key = None
        if isinstance(keyColNum, tuple):
            keys = []
            for keyNum in keyColNum:
                keys.append(parts[keyNum].strip())
            key = ':'.join(keys)
        else:
            key = parts[keyColNum].strip()

        # check uniqueness
        if key in d.keys() and unique:
            raise MyError("Non-unique key found: %s" % key)

        d[key] = {}
        for k, v in cols.iteritems():
            if k in listify.keys():
                d[key][k] = parts[v].strip().split(listDelimiter)
            else:
                d[key][k] = parts[v].strip()

    return d


def dictToCsvFile(filename, d, header, delimiter='|', listDelimiter=';',
                  codec='utf-8'):
    """
    Save a dict as csv file given a header string encoding the columns.

    :param filename: the target file
    :param d: the dictionary to convert
    :param header: a string giving parameters to output and their order
    :param delimiter: the used delimiter (defaults to "|")
    :param listDelimiter: the used delimiter when encountering a list
    :param codec: the used encoding (defaults to "utf-8")
    :return: None
    """
    # load file and write header
    f = codecs.open(filename, 'w', codec)
    f.write(u'%s\n' % header)

    # find keys to compare with header
    cols = d.iteritems().next()[1].keys()
    header = header.split(delimiter)

    # verify all header fields are present
    if any(h not in cols for h in header):
        raise MyError("Header missmatch")

    # output rows
    for k, v in d.iteritems():
        row = []
        for h in header:
            if isinstance(v[h], list):
                row.append(listDelimiter.join(v[h]))
            else:
                row.append(v[h])
        f.write(u'%s\n' % delimiter.join(row))

    # close
    f.close()


def promptManualUpdate(d, tmpFile, tmpHeader, keyCol):
    """
    @crunchRedux
    Given a dict ask the user if a manual update is needed.
    *If yes:
        write dict as csv in a temporary file, prompt user again then read the
        file back in as a dict and return
    *If no: return untouched dict
    :param d: path to photo data file
    :param tmpFile: temporary file to write to
    :param tmpHeader: headerCheck for temporary file
    :param keyCol: column (label) to use as key for reading back temporary file
    :return: dict
    """
    if not VERBOSE:
        return d
    while True:
        choice = raw_input(u"Does the file need to be manually updated? "
                           u"[Y/N]:")
        if choice.lower() == 'y':
            dictToCsvFile(tmpFile, d, tmpHeader)
            print u"Open the temporary file (%s), make any changes " \
                  u"and save" % tmpFile
            raw_input(u"Press enter when done")
            d = csvFileToDict(tmpFile, keyCol, tmpHeader)

            # delete temporary file
            os.remove(tmpFile)

            break
        elif choice.lower() == 'n':
            break
        print "Unrecognised input (%s), try again" % choice
    return d


def urldecode_utf8(url):
    """
    Given a utf8 unicode urlencoded url this returns the correct,
    utf8 encoded, unquoted url. E.g:
        u'http://Prinsessan_Eug%C3%A9nie_av_Sverige_och_Norge'
        becomes
        u'http://Prinsessan_Eug\xe9nie_av_Sverige_och_Norge'
    @ToDo: Put in standard common.py
    :param url: url to decode
    :return: str
    """
    return urllib2.unquote(url.encode('ascii')).decode('utf8')


def external_2_internal_link(url, project='wikipedia'):
    """
    Given an external link to wikipedia this returns a wikified
    interwikilink. E.g.
        https://sv.wikipedia.org/wiki/Helan_går
        becomes
        [[:sv:Helan går]]
    :param url: url to decode
    :return: str
    """
    pattern = r'http(s)?://([^\.]*).%s.org/wiki/([^$]*)' % project
    url2 = re.sub(pattern, r'[[:\2:\3]]', url)
    if url2 != url:  # if successfully matched
        url = url2.replace('_', ' ')
    return url


def split_multi_valued(value, delimiter=';'):
    """Split value if not empty."""
    if value:
        value = value.split(delimiter)
    return value


def is_int(s):
    """
    Tests if a string is an integer
    :param s: test string
    :return: bool
    """
    try:
        int(s)
        return True
    except (ValueError, TypeError):
        return False


def sortedBy(d, sortkey=u'freq'):
    """
    Given a dictionary where each entry is in turn a dict, this returns
    a list of the keys orderd by decreasing value of the sortkey
    (key in the inner dict)
    :param d: dictionary to sort
    :param sortkey: key in inner dict to sort by
    :return: list
    """
    return sorted(d.iteritems(),
                  key=lambda (k, v): (v[sortkey], k),
                  reverse=True)


def findFiles(path, fileExts, subdir=True):
    """
    Identify all files with a given extension in a given directory
    :param path: path to directory to look in
    :param fileExts: tuple of allowed file extensions (case insensitive)
    :param subdir: whether subdirs should also be searched
    :return: list of paths to found files
    """
    files = []
    subdirs = []
    for filename in os.listdir(path):
        if os.path.splitext(filename)[1].lower() in fileExts:
            files.append(os.path.join(path, filename))
        elif os.path.isdir(os.path.join(path, filename)):
            subdirs.append(os.path.join(path, filename))
    if subdir:
        for subdir in subdirs:
            files += findFiles(path=subdir, fileExts=fileExts)
    return files


def loadJsonConfig(filename=u'config.json'):
    """
    Load and return json config file as a dict.
    Looks in local directory first.
    If file isn't there then looks in user directory.
    If file is in neither location then error is raised
    :param filename: name of json config file
    :return: dict
    """
    try:
        f = open(filename, 'r')
        config = json.load(f)
        f.close()
    except IOError as e:
        if e.errno == 2:  # file not found
            path = os.getenv("HOME")
            f = open(os.path.join(path, filename), 'r')
            config = json.load(f)
            f.close()
        else:
            raise
    return config


def convertFromCommandline(s):
    """
    Converts a string read from the commandline to a standard unicode
    format.
    :param s: string to convert
    :return: str
    """
    return s.decode(sys.stdin.encoding or
                    locale.getpreferredencoding(True))


def output(text):
    """
    A wrapper to only print text if VERBOSE is True
    :param text: text to print
    :return: None
    """
    if VERBOSE:
        print text


def verboseInput(text):
    """
    A wrapper to only prompt if VERBOSE is True
    :param text: text to print
    :return: str
    """
    if VERBOSE:
        return raw_input(text).strip()


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
