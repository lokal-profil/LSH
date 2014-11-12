#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Tool for scraping existing wiki lists from commons and
# storing these as correctly formated local files
# How to use:
#   just use "run()"
#
# TODO:
#   Rebuild using WikiApi
#   Propper commenting
from common import Common
import codecs
import urllib
import urllib2
from json import loads

OUT_PATH = u'connections'
DATA_PATH = u'data'


def getPage(page, verbose=False):
    '''
    Queries the commons API to return the contents of a given page
    @ input: page to look at
    @ output: contents of page
    '''
    wikiurl = u'https://commons.wikimedia.org'
    apiurl = '%s/w/api.php' % wikiurl
    urlbase = '%s?action=query&prop=revisions&format=json&rvprop=content&rvlimit=1&titles=' % apiurl
    url = urlbase+urllib.quote(page.encode('utf-8'))
    if verbose:
        print url
    req = urllib2.urlopen(url)
    j = loads(req.read())
    req.close()
    pageid = j['query']['pages'].keys()[0]
    if pageid == u'-1':
        print 'no entry for "%s"' % page
        return None
    else:
        content = j['query']['pages'][pageid]['revisions'][0]['*']
        return content


def parseEntries(contents):
    '''
    Given the contents of a wikipage this returns the entries listed in it
    input: wikicode
    @ output: list of entry-dict items
    '''
    units = []
    header_t = u'{{user:Lokal Profil/LSH2'
    row_t = u'{{User:Lokal Profil/LSH3'
    while(True):
        table, contents, lead_in = Common.findUnit(contents, header_t, u'|}')
        if not table:
            break
        while(True):
            unit, table, dummy = Common.findUnit(table, row_t, u'}}', brackets={u'{{': u'}}'})
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
                part, unit, dummy = Common.findUnit(unit, u'|', u'\n', brackets={u'[[': u']]', u'{{': u'}}'})
                if not part:
                    break
                if u'=' in part:
                    part = part.replace(u'<small>', '').replace(u'</small>', '')
                    part = part.strip(' \n\t')
                    # can't use split as coord uses second equality sign
                    pos = part.find(u'=')
                    key = part[:pos].strip()
                    value = part[pos+1:].strip()
                    if len(value) > 0:
                        if (key) in params.keys():
                            params[key] = value.split(u'/')
                        else:
                            print u'Unrecognised parameter: %s = %s' % (key, value)
            units.append(params.copy())
            # end units
        # end tables
    return units


def formatOutput(units, page):
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
        return u'*%s|%s|%s|%s|%s|%s' % (u['more'], u['frequency'], u['name'], u['link'], u['creator'], u['category'])
    elif page == 'Events':
        return u'*%s|%s|%s|%s' % (u['name'], u['frequency'], u['link'], u['category'])
    elif page == 'ObjKeywords':
        return u'*%s|%s|%s' % (u['name'], u['frequency'], u['category'])
    elif page == 'Keywords':
        return u'*%s|%s|%s|%s' % (u['name'], u['frequency'], u['more'], u['category'])
    elif page == 'Materials':
        return u'*%s|%s|%s' % (u['name'], u['frequency'], u['technique'])
    elif page == 'Places':
        return u'*%s|%s|%s' % (u['name'], u['frequency'], u['other'])
    elif page == 'Photographers':
        return u'*%s|%s|%s|%s' % (u['name'], u['frequency'], u['creator'], u['category'])


def parseFilenameEntries(contents):
    '''
    Given the contents of the filenames wikipage this returns improved entries
    input: wikicode
    @ output: list of changed entries-dict items
    '''
    units = []
    contents = contents.split(u'\n')
    for line in contents:
        if not line.startswith(u'| '):
            continue
        elif len(line.split(u'||')) != 3:
            print u'Line starting right but with too few units: %s' % line
            continue
        else:
            parts = line.split(u'||')
            if len(parts[2].strip()) > 0:  # if filename was improved
                phoId = parts[0][len(u'| '):].strip()
                generated = parts[1].replace(u'<span style="color:red">', u'') \
                                    .replace(u'</span>', u'') \
                                    .strip()
                improved = parts[2].strip()
                if generated != improved:  # if actually changed
                    units.append({u'phoId': phoId,
                                  u'generated': generated,
                                  u'improved': improved})
    return units


def run(out_path=OUT_PATH, data_path=DATA_PATH):
    import os
    # Define a list of pages and output files
    # where page has the format Commons:Batch uploading/LSH/*
    # and outputfile the format: commons-*.csv
    pages = {u'People': u'People',
             u'Events': u'Events',
             u'ObjKeywords': u'ObjKeywords',
             u'Keywords': u'Keywords',  # stichwort
             u'Materials': u'Materials',
             u'Places': u'Places',
             u'Photographers': u'Photographers'
             }
    # create out_path if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    # fetch, parse and save each page
    for k, v in pages.iteritems():
        contents = getPage(u'Commons:Batch uploading/LSH/%s' % k)
        units = parseEntries(contents)
        output = formatOutput(units, k)
        out = codecs.open(u'%s/commons-%s.csv' % (out_path, v), 'w', 'utf8')
        out.write(output)
        out.close()
        print u'Created %s/commons-%s.csv' % (out_path, v)

    # need to do filenames differently
    contents = getPage(u'Commons:Batch uploading/LSH/Filenames')
    units = parseFilenameEntries(contents)  # identify changes
    if len(units) > 0:
        # load old filenames
        oldfile = u'%s/filenames.csv' % data_path
        oldFilenames = Common.file_to_dict(oldfile, idcol=0)
        for unit in units:
            if not unit[u'phoId'] in oldFilenames.keys():
                print u'could not find id in old: %s, %s' % (unit[u'phoId'], unit[u'generated'])
                exit(1)
            oldDesc = oldFilenames[unit[u'phoId']][u'filename']
            newDesc = oldDesc.replace(unit[u'generated'], unit[u'improved'])
            if oldDesc == newDesc:  # this is most often caused by commons file not having been updated
                print u'did you run the updater a second time without first updating the filenamestable on Commons?'
                exit(1)
            oldFilenames[unit[u'phoId']][u'filename'] = newDesc
        # overwrite old filenames
        out = codecs.open(oldfile, 'w', 'utf8')
        out.write(u'PhoId|MulId|MulPfadS|MulDateiS|filename|ext\n')
        for k, v in oldFilenames.iteritems():
            out.write(u'%s|%s|%s|%s|%s|%s\n' % (v[u'PhoId'], v[u'MulId'],
                      v[u'MulPfadS'], v[u'MulDateiS'], v[u'filename'],
                      v[u'ext']))
        out.close()
        print u'Updated %s' % oldfile

if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_listscraper.py out_path data_path\n' \
        + u'\tout_path (optional):the relative pathname to the target \n' \
        + u'directory. Defaults to "%s"' % OUT_PATH \
        + u'\tdata_path (optional):the relative pathname to the data \n' \
        + u'directory. Defaults to "%s"' % DATA_PATH
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 2:
        argv[0] = argv[0].decode(sys.getfilesystemencoding())  # str to unicode
        argv[1] = argv[1].decode(sys.getfilesystemencoding())  # str to unicode
        run(out_path=argv[0], data_path=argv[1])
    else:
        print usage
# EoF
