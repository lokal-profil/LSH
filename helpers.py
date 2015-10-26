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
import urllib2  # needed by urldecodeUTF8()
import re  # neeeded by external2internalLink()
import sys  # needed by convertFromCommandline()
import locale  # needed by convertFromCommandline()


def csvFileToDict(filename, keyCol, headerCheck, unique=True, keep=None,
                  lists=None, delimiter='|', listDelimiter=';', codec='utf-8'):
    """
    Opens a given encoded csv file and returns a dict of dicts, using
    the header row for keys
    :param filename: the file to open
    :param keyCol: the (label of the) column to use as a key in the dict
                   str or tuple of strs to combine
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
    lines = codecs.open(filename, 'r', codec).read().split('\n')
    header = lines.pop(0).split(delimiter)

    # verify header == headerCheck (including order)
    if headerCheck.split(delimiter) != header:
        raise MyError("Header missmatch")

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
        if len(l) == 0:
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
    Saves a dict as csv file given a header string encoding the columns
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


def urldecodeUTF8(url):
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


def external2internalLink(url, project='wikipedia'):
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


def convertFromCommandline(s):
    """
    Converts a string read from the commandline to a standard unicode
    format.
    :param s: string to convert
    :return: str
    """
    return s.decode(sys.stdin.encoding or
                    locale.getpreferredencoding(True))


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
