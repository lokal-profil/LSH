#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Post upload library
# TODO: Batch purges
#
import WikiApi as wikiApi
import helpers
import codecs
import os

# strings indicating a file belongs to the upload
IDENTIFIERS = (u'Livrustkammaren', u'Skoklosters', u'Hallwylska', u'LSH')
POST_DIR = u'postAnalysis'
BROKEN_LINKS_FILE = os.path.join(POST_DIR, u'BrokenFileLinks.csv')
MISSING_FILES_FILE = os.path.join(POST_DIR, u'AllMissingFiles.csv')
DATA_DIR = u'data'
FILENAME_FILE = os.path.join(DATA_DIR, u'filenames.csv')
LSH_EXPORT_FILE = os.path.join(POST_DIR, u'FileLinkExport.csv')


def purgeBrokenLinks(configPath=u'config.json'):
    api = helpers.openConnection(configPath, apiClass=WikiApiHotfix)

    # find which images point to (potentially) missing files
    # Todo: Package them in batches of 10/25? before purging
    pages = api.getCategoryMembers(categoryname=u'Category:Files with broken file links', cmnamespace=6)
    count = 0
    for page in pages:
        if any(i in page for i in IDENTIFIERS):
            count += 1
            api.purgeLinks(page=page, forcelinkupdate=True)
            if count % 250 == 0:
                print count
    print u'Found %d pages with broken links' % count


def findMissingImages(configPath=u'config.json'):
    '''
    Goes through any LSH images with broken file links to identify the
    missing images
    '''
    # create targetdirectory if it doesn't exist
    if not os.path.isdir(POST_DIR):
        os.mkdir(POST_DIR)

    api = helpers.openConnection(configPath, apiClass=WikiApiHotfix)
    f = codecs.open(BROKEN_LINKS_FILE, 'w', 'utf8')

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
            f.write(u'%s|\n' % m)
        else:
            print m
    f.close()
    print u'Go through %s and add any known renamed files after the pipe. ' \
          u'Note that the renamed value should not include prefix or extention ' \
          u'(i.e. be the same as in filenames file' % BROKEN_LINKS_FILE


def fixRenamedFiles(filename=BROKEN_LINKS_FILE, configPath=u'config.json'):
    '''
    Replaces any broken file links for files known to have been renamed
    '''
    f = codecs.open(filename, 'r', 'utf8')
    lines = f.read().split('\n')

    changed = []
    for l in lines:
        if len(l) == 0:
            continue
        oldName, newName = l.split('|')
        if len(newName.strip()) > 0:
            # if a rename was specified
            changed.append({'new': u'%s.%s' % (newName, oldName[-3:]),  # add file ending
                            'old': oldName[len('File:'):]})  # strip namespace

    comApi = helpers.openConnection(configPath)

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


def findAllMissing(infile=FILENAME_FILE, configPath=u'config.json'):
    '''
    Goes through the filenames file and checks each name for existence.
    Missing files are outputed to MISSING_FILES_FILE
    Existing files are outputed to LSH_EXPORT_FILE
    @toDo: Add mulid in LSH export format?
    '''
    # create targetdirectory if it doesn't exist
    if not os.path.isdir(POST_DIR):
        os.mkdir(POST_DIR)

    comApi = helpers.openConnection(configPath)

    f = codecs.open(infile, 'r', 'utf8')
    lines = f.read().split('\n')
    f.close()

    fMissing = codecs.open(MISSING_FILES_FILE, 'w', 'utf8')
    fMissing.write(u'%s\n' % lines.pop(0))

    fFound = codecs.open(LSH_EXPORT_FILE, 'w', 'utf8')
    fFound.write(u'PhoId|PhmInhalt01M / PhmInhalt01M\n')
    prefix = u'https://commons.wikimedia.org/wiki/'

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
            fMissing.write(u'%s\n' % files[name])
        else:
            phoId = files[name].split('|')[0]
            fFound.write(u'%s|%s%s\n' % (phoId, prefix, name.replace(' ', '_')))
    fMissing.close()
    fFound.close()


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


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_postUpload.py action\n' \
        u'\taction: purge - purges broken fileliks in LSH files and ' \
        u'produces a file with remaining broken file links\n' \
        u'\taction: rename - repairs broken file links for any files where ' \
        u'a new name was added to broken file links\n' \
        u'\taction: updateBroken - updates the brokenFileLinks file ' \
        u'(overwriting any added renamings)\n' \
        u'\taction: findMissing - checks all filenames for existance ' \
        u'and produces a link table for LSH import'
    argv = sys.argv[1:]
    if len(argv) == 1:
        if argv[0] == 'purge':
            purgeBrokenLinks()
            findMissingImages()
        elif argv[0] == 'rename':
            fixRenamedFiles()
        elif argv[0] == 'updateBroken':
            findMissingImages()
        elif argv[0] == 'findMissing':
            findAllMissing()
        else:
            print usage
    else:
        print usage
# EoF
