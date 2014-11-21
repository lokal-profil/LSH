#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Cleanup
# TODO: Remove run method
# Make findMissing ta parametern purge, om sant skriv inte ut utan purga var och en av de identifierade filerna
# vänta mellan purges
#
import WikiApi as wikiApi
import config as config
import codecs

# strings indicating a file belongs to the upload
IDENTIFIERS = (u'Livrustkammaren', u'Skoklosters', u'Hallwylska')


def run(filename):
    '''
    Vet inte om denna behövs. Möjligen kan den byggas om, med förklaring,
    så att Broken... efter att "rätt namn har stoppats in" kan köras
    '''
    f = codecs.open(filename, 'r', 'utf8')
    lines = f.read().split('\n')

    changed = []
    for l in lines:
        if len(l) == 0:
            continue
        oldName = u'%s.tif' % l[:-4]
        changed.append({'new': l, 'old': oldName})

    comApi = wikiApi.WikiApi.setUpApi(user=config.username, password=config.password, site=config.site)

    while len(changed) > 0:
        active = changed.pop()
        links = comApi.getImageUsage(u'File:%s' % active['old'], iunamespace=6)
        if links:
            pages = comApi.getPage(links)
            for name, contents in pages.iteritems():
                contentsNew = contents.replace(active['old'], active['new'])
                # whilst we are here replace any others
                for c in changed:
                    contentsNew = contentsNew.replace(c['old'], c['new'])
                if contents == contentsNew:
                    print 'no change for %s' % name
                else:
                    comApi.editText(name, contentsNew, u'Fixing broken filelinks from [[Commons:Batch_uploading/LSH|batch upload]]', minor=True, bot=True, nocreate=True, userassert=None)


def purgeBrokenLinks():
    api = WikiApiHotfix.setUpApi(user=config.username, password=config.password, site=config.site)

    # find which images point to (potentially) missing files
    pages = api.getCategoryMembers(categoryname=u'Category:Files with broken file links', cmnamespace=6)
    count = 0
    for page in pages:
        if any(i in page for i in IDENTIFIERS):
            count += 1
            api.purgeImageLinks(page=page, forcelinkupdate=True)
    print u'Found %d pages with broken links' % count


def findMissingImages():
    api = WikiApiHotfix.setUpApi(user=config.username, password=config.password, site=config.site)
    f = codecs.open(u'BrokenFileLinks.csv', 'w', 'utf8')

    # find which images point to (potentially) missing files
    pages = api.getCategoryMembers(categoryname=u'Category:Files with broken file links', cmnamespace=6)

    # find which images are refered to
    missing = []
    count = 0
    for page in pages:
        if any(i in page for i in IDENTIFIERS):
            count += 1
            missing = missing + api.getMissingImages(page)
    missing = list(set(missing))
    print u'Found %d missing files in %d broken pages' % (len(missing), count)

    for m in missing:
        if any(i in m for i in IDENTIFIERS):
            f.write(u'%s\n' % m)
        else:
            print m
    f.close()


def findAllMissing(infile=u'data/filenames.csv'):
    '''
    Goes through the filenames file and checks each name for existence
    '''
    comApi = wikiApi.WikiApi.setUpApi(user=config.username, password=config.password, site=config.site)

    f = codecs.open(infile, 'r', 'utf8')
    lines = f.read().split('\n')
    f.close()

    f = codecs.open(u'AllMissingFiles.csv', 'w', 'utf8')
    f.write(u'%s\n' % lines.pop(0))

    files = {}
    for l in lines:
        if len(l) == 0:
            continue
        PhoId, MulId, MulPfadS, MulDateiS, filename, ext = l.split('|')
        files[u'File:%s.%s' % (filename, ext)] = l

    print u'Found %d filenames' % len(files)

    fileInfos = comApi.getPageInfo(files.keys())
    for name, info in fileInfos.iteritems():
        if 'missing' in info.keys():
            f.write(u'%s\n' % files[name])
    f.close()


class WikiApiHotfix(wikiApi.WikiApi):
    '''Extends the WikiApi class with post_upload specific methods'''

    def getMissingImages(self, page, debug=False):
        '''
        Returns a list of all images linked to from a page where the
        given image does not exist
        :param page: The page to look at, incl. any namespace prefix
        :param iunamespace: namespace to limit the search to (0=main, 6=file)
        :return: list of pagenames
        '''
        # print "Fetching getMissingImages: " + page
        members = []
        # action=query&prop=images&format=json&imlimit=1&titles=File%3AFoo.jpg&generator=images&gimlimit=100
        jsonr = self.httpPOST("query", [('prop', 'images'),
                                        ('titles', page.encode('utf-8')),
                                        ('imlimit', '1'),
                                        ('generator', 'images'),
                                        ('gimlimit', '100')])

        if debug:
            print u'getMissingImages() page:%s \n' % page
            print jsonr

        # "query":{"pages":{"-1":{"ns":6,"title":"File:Axelgeh\u00e4ng - Livrustkammaren - 42925.tif","missing":""}
        for page in jsonr['query']['pages']:
            if int(page) < 0:
                page = jsonr['query']['pages'][page]
                # if 'missing' in page.keys():
                members.append(page['title'])

        # print  "Fetching getMissingImages: " + page + "...complete"
        return members

    def purgeLinks(self, page, forcelinkupdate=True, debug=False):
        '''
        Triggers a purge (and link update) for the given page
        :param page: The page to look at, incl. any namespace prefix
        :param forcelinkupdate: for links table to be updated
        '''
        # action=query&prop=images&format=json&imlimit=1&titles=File%3AFoo.jpg&generator=images&gimlimit=100
        jsonr = self.httpPOST("purge", [('forcelinkupdate', ''),
                                        ('titles', page.encode('utf-8'))])

        if debug:
            print u'purgeImageLinks() page:%s \n' % page
            print jsonr

        if 'batchcomplete' not in jsonr.keys():
            print u'Some trouble occured while purging'
            print jsonr
