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
#   Add filenames
from common import Common as common
import codecs
import urllib
import urllib2
from json import loads

OUT_PATH = u'connections'

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
        table, contents, lead_in = common.findUnit(contents, header_t, u'|}')
        if not table:
            break
        while(True):
            unit, table, dummy = common.findUnit(table, row_t, u'}}', brackets={u'{{': u'}}'})
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
                part, unit, dummy = common.findUnit(unit, u'|', u'\n', brackets={u'[[': u']]', u'{{': u'}}'})
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


def run(out_path=OUT_PATH):
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

if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_listscraper.py out_path\n' \
        + u'\tout_path (optional):the relative pathname to the target \n' \
        + u'directory. Defaults to "%s"' % OUT_PATH
    argv = sys.argv[1:]
    if len(argv) == 0:
        run()
    elif len(argv) == 1:
        run(out_path=argv[0])
    else:
        print usage
# EoF
