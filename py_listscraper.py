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
        if not table: break
        while(True):
            unit, table, dummy = common.findUnit(table, row_t, u'}}', brackets={u'{{': u'}}'})
            if not unit: break
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
                if not part: break
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
    intro = {u'People': u'<!--From: kuenstler_1.2.csv -->\n\'\'wikipedia-link\'\' is used for descriptive texts whereas creator is a creator template on commons and \'\'commoncat\'\' is a relevant category on commons.\n\nSet commonsconnection of irrelevant events to "-". Note that creator is only relevant for artists\n\n===kueId|frequency|name|wikipedia-link|creator|commoncat===\n',
             u'Events': u'<!--From: Ereignis_1.1.csv -->\n\'\'wikipedia-link\'\' are used for descriptive texts whereas \'\'commonsconnection\'\' is a relevant category on commons.\n\nSet commonsconnection of irrelevant events to "-"\n\nMultiple categories are separated by ";"\n\n*död/begravning: [[:Category:Funeral of X of Sweden]]\n*kröning: [[:Category:Coronation of X of Sweden]]\n*bröllop:[[:Category:Wedding of X and Y of Sweden]]\n===Event|Frequency|wikipedia-link|Commonsconnection===\n',
             u'Keywords': u'<!--From: Photo_stichwort_1.2.csv -->\nSet commonsconnection of irrelevant keywords to "-"\n\nMultiple categories are separated by ";"\n===Keyword|frequency|description|commonsconnection===\n',
             u'ObjKeywords': u'These are the keywords used to describe the objects themselves. Classification is used for all items whereas group is only used at HWY.\n\nwhen possible ord1 will be used instead of the more generic ord2.\n===*Keyword|frequency|commonscategory===\n',
             u'Materials': u'<!--From: ObjMultiple_1.2.csv -->\ncommonsconnection is the relevant parameter for {{technique}}. Don\'t forget to add a translation in Swedish at [[Template:Technique/sv]]\n\nSet commonsconnection of irrelevant technique/material to "-".\n\n===technique/material|frequency|commonsconnection===\n',
             u'Places': u'<!--From: Ausstellung_1.1.csv - col: ausOrt-->\nSet commonsconnection of irrelevant places to "-"\n\nMultiple entries are separated by ";"\n===Place|Frequency|Commonsconnection===\n',
             u'Photographers':  u'<!--From: photo_1.2.csv -->\n===Photographers===\n'
             }
    txt = intro[page]
    for u in units:
        txt = u'%s%s\n' % (txt, rowFormat(u, page))
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


def run(out_path=u'connections'):
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
