#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Tool for scraping existing wiki lists from commons and
# storing these as correctly formated local files
#
# TODO:
#   Proper commenting
#   Import improvements from batchUploadTools
#   General cleanup
#
from common import Common
import helpers
from helpers import output
import py_filenames as Filenames  # reuse methods for cleaning and outputting
# from py_filenames import cleanName  # removes dissalowed characters etc.
import codecs
import os

OUT_PATH = u'connections'
DATA_PATH = u'data'
MAPPING_FOLDER = u'mappings'
COMMONS_PREFIX = u'Commons:Batch uploading/LSH'


def parseEntries(contents):
    """
    Return entries listed in given wikipage.

    :param contents: wikicode of page with lists
    :return: list of entry-dict items
    """
    units = []
    header_t = u'{{user:Lokal Profil/LSH2'
    row_t = u'{{User:Lokal Profil/LSH3'
    while(True):
        table, contents, lead_in = Common.findUnit(contents, header_t, u'|}')
        if not table:
            break
        while(True):
            unit, table, dummy = Common.findUnit(table, row_t, u'}}',
                                                 brackets={u'{{': u'}}'})
            if not unit:
                break
            params = {u'name': '',
                      u'more': '',
                      u'frequency': '',
                      u'technique': '',
                      u'creator': '',
                      u'link': '',
                      u'category': '',
                      u'other': ''
                      }
            while(True):
                part, unit, dummy = Common.findUnit(
                    unit, u'|', u'\n', brackets={u'[[': u']]', u'{{': u'}}'})
                if not part:
                    break
                if u'=' in part:
                    part = part.replace(u'<small>', '').replace(u'</small>', '')
                    part = part.strip(' \n\t')
                    # can't use split as coord uses second equality sign
                    pos = part.find(u'=')
                    key = part[:pos].strip()
                    value = part[pos + 1:].strip()
                    if value:
                        if (key) in params.keys():
                            params[key] = value.split(u'/')
                        else:
                            print u'Unrecognised parameter: %s = %s' \
                                  % (key, value)
            units.append(params.copy())
            # end units
        # end tables
    return units


def formatOutput(units, page):
    """
    @TODO:
    reubuild so that this uses helpers.dictToCsvFile(filename, d, header)
    this then sets header and rowformat makes the dict
    needed:
    # add header (or drop header requirement in helpers.dictToCsvFile)
    # drop * prefix in csv (requires followup in MakeInfo, at least)
    """
    txt = u''
    for u in units:
        txt += u'%s\n' % rowFormat(u, page)
    return txt


def rowFormat(u, page):
    mapping = {'link': u"[[%s]]",
               'creator': u"[[Creator:%s]]",
               'category': u"[[:Category:%s]]",
               'technique': u"%s",
               'name': u"%s",
               'more': u"%s",
               'frequency': u"%s",
               'other': u"%s"
               }
    for k, v in u.iteritems():
        if not v:
            u[k] = ''
        elif len(v) == 1:
            if v[0] == '-':
                u[k] = '-'
            else:
                u[k] = mapping[k] % v[0]
                if k == 'other':
                    u[k] = u[k].replace('|', '{{!}}')
        else:
            txt = ''
            for vv in v:
                if vv == '-':
                    txt = u'%s-;' % txt
                else:
                    txt = u'%s%s;' % (txt, mapping[k] % vv)
            if k == 'other':
                txt = txt.replace('|', '{{!}}')
            u[k] = txt[:-1]
    # now choose output format
    if page == 'People':
        return u'*%s|%s|%s|%s|%s|%s' % (u['more'], u['frequency'],
                                        u['name'], u['link'],
                                        u['creator'], u['category'])
    elif page == 'Events':
        return u'*%s|%s|%s|%s' % (u['name'], u['frequency'],
                                  u['link'], u['category'])
    elif page == 'ObjKeywords':
        return u'*%s|%s|%s' % (u['name'], u['frequency'], u['category'])
    elif page == 'Keywords':
        return u'*%s|%s|%s|%s' % (u['name'], u['frequency'],
                                  u['more'], u['category'])
    elif page == 'Materials':
        return u'*%s|%s|%s' % (u['name'], u['frequency'], u['technique'])
    elif page == 'Places':
        return u'*%s|%s|%s' % (u['name'], u['frequency'], u['other'])
    elif page == 'Photographers':
        return u'*%s|%s|%s|%s' % (u['name'], u['frequency'],
                                  u['creator'], u['category'])


def parseFilenameEntries(contents):
    """
    Given the contents of the filenames wikipage this returns improved
    entries together with a list of all encountered phoIds
    :param contents: wikicode to parse
    :return: (list, list)
    """
    units = []
    allEntries = []
    contents = contents.split(u'\n')
    for line in contents:
        if not line.startswith(u'| '):
            continue
        elif len(line.split(u'||')) != 3:
            print u'Line starting right but with too few units: %s' % line
            continue
        else:
            parts = line.split(u'||')
            phoId = parts[0][len(u'| '):].strip()
            allEntries.append(phoId)
            if parts[2].strip():  # if filename was improved
                generated = parts[1].replace(u'<span style="color:red">', u'') \
                                    .replace(u'</span>', u'') \
                                    .strip()
                improved = Filenames.cleanup_routine(parts[2])
                if improved and (generated != improved):  # if actually changed
                    units.append({u'phoId': phoId,
                                  u'generated': generated,
                                  u'improved': improved})
    return units, allEntries


def run(outPath=None, dataPath=None, mappingsPath=None,
        commonsPrefix=None, configPath=u'config.json'):
    """
    Define a list of pages and output files
    where page has the format Commons:Batch uploading/LSH/*
    and outputfile the format: commons-*.csv
    """
    # set defaults unless overridden
    outPath = outPath or OUT_PATH
    dataPath = dataPath or DATA_PATH
    mappingsPath = mappingsPath or MAPPING_FOLDER
    commonsPrefix = commonsPrefix or COMMONS_PREFIX

    pages = {u'People': u'People',
             u'Events': u'Events',
             u'ObjKeywords': u'ObjKeywords',
             u'Keywords': u'Keywords',  # stichwort
             u'Materials': u'Materials',
             u'Places': u'Places',
             u'Photographers': u'Photographers'
             }
    # create out_path if it doesn't exist
    if not os.path.isdir(outPath):
        os.mkdir(outPath)

    # fetch, parse and save each page
    comApi = helpers.openConnection(configPath)
    for k, v in pages.iteritems():
        comPage = u'%s/%s' % (commonsPrefix, k)
        contents = comApi.getPage(comPage)
        units = parseEntries(contents[comPage])
        outdata = formatOutput(units, k)
        outFile = os.path.join(outPath, u'commons-%s.csv' % v)
        out = codecs.open(outFile, 'w', 'utf8')
        out.write(outdata)
        out.close()
        output(u'Created %s' % outFile)

    # need to do filenames differently
    mappingFile = os.path.join(mappingsPath, u'Filenames.txt')
    comPage = u'%s/Filenames' % commonsPrefix
    contents = comApi.getPage(comPage)

    # identify changes
    units, allEntries = parseFilenameEntries(contents[comPage])
    if units:
        # load old filenames
        filenamesHeader = 'PhoId|MulId|MulPfadS|MulDateiS|filename|ext'
        filenamesFile = os.path.join(dataPath, u'filenames.csv')
        oldFilenames = helpers.csvFileToDict(filenamesFile, 'PhoId',
                                             filenamesHeader)
        for unit in units:
            pho_id = unit[u'phoId']
            if pho_id not in oldFilenames.keys():
                print u'could not find id in old: %s, %s' % \
                      (pho_id, unit[u'generated'])
                exit(1)
            old_desc = oldFilenames[pho_id][u'filename']
            # newDesc = oldDesc.replace(unit[u'generated'], unit[u'improved'])
            # a safer implementation where new description is appended to
            # old ending. I.e. "- Museum - idNo"
            new_desc = u'%s %s' % (unit[u'improved'],
                                   splitFilename(old_desc)[1])
            if old_desc == new_desc:
                # indicator that commons file may not having been updated which
                # may cause more complex problems which are hard to test for
                print u'did you run the updater a second time without ' \
                      u'first updating the filenames table on Commons?'
                exit(1)
            oldFilenames[pho_id][u'filename'] = new_desc

        # overwrite old filenames and old mapping
        # new filename.csv file w. header
        helpers.dictToCsvFile(filenamesFile, oldFilenames, filenamesHeader)
        # new Commons mapping file needs a dict with all descriptions
        mapping_dict = {}
        for phoId, v in oldFilenames.iteritems():
            descr = splitFilename(v[u'filename'])[0]
            mapping_dict[phoId] = {'descr': descr}

        Filenames.commonsOutput(mapping_dict, mappingFile, allEntries)
        output(u'Updated %s and produced a new mappingfile %s. Please upload '
               u'the new one to Commons.' % (filenamesFile, mappingFile))


def splitFilename(txt):
    """
    Given a filename of the format "Descr - Museum - ID" split this to
    return a tuple (Descr, - Museum - ID)
    :param txt: the text to parse
    :return: (str, str)
    """
    descr = txt[:txt.rfind('-', 0, txt.rfind('-'))].strip()
    rest = txt[txt.rfind('-', 0, txt.rfind('-')):].strip()
    return (descr, rest)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_listscraper.py out_path data_path\n' \
            u'\tout_path (optional):the relative pathname to the target ' \
            u'directory. Defaults to "%s"\n' \
            u'\tdata_path (optional):the relative pathname to the data ' \
            u'directory. Defaults to "%s"' % (OUT_PATH, DATA_PATH)
    argv = sys.argv[1:]
    if not argv:
        run()
    elif len(argv) == 2:
        argv[0] = helpers.convertFromCommandline(argv[0])
        argv[1] = helpers.convertFromCommandline(argv[1])
        run(outPath=argv[0], dataPath=argv[1])
    else:
        print usage
# EoF
