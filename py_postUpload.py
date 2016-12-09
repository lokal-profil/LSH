#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Post upload library
# TODO: Batch purges
#
import helpers
import codecs
import os
import time
import pywikibot
from pywikibot import config as pwb_config

# strings indicating a file belongs to the upload
IDENTIFIERS = (u'Livrustkammaren', u'Skoklosters', u'Hallwylska', u'LSH')
POST_DIR = u'postAnalysis'
BROKEN_LINKS_FILE = os.path.join(POST_DIR, u'BrokenFileLinks.csv')
MISSING_FILES_FILE = os.path.join(POST_DIR, u'AllMissingFiles.csv')
DATA_DIR = u'data'
FILENAME_FILE = os.path.join(DATA_DIR, u'filenames.csv')
LSH_EXPORT_FILE = os.path.join(POST_DIR, u'FileLinkExport.csv')


def purge_broken_links():
    """
    Purge images which contain links to (potentially) missing files.

    This is needed for any image which embeds (through <gallery>) an image
    which was uploaded afterwards.
    """
    site = pywikibot.Site('commons', 'commons')
    hotfix = WikiApiHotfix(site)

    category_title = u'Category:Files with broken file links'
    category = pywikibot.Page(site, category_title)
    pages = site.categorymembers(category, namespaces=6)

    # purge any where the filename contains one of our identifiers
    to_purge = filter(lambda page: any(i in page.title() for i in IDENTIFIERS),
                      pages)

    hotfix.purge_links(pages=to_purge, forcelinkupdate=True, verbose=True)


def find_missing_images():
    """Identify missing images from any LSH images with broken file links."""
    # create target directory if it doesn't exist
    if not os.path.isdir(POST_DIR):
        os.mkdir(POST_DIR)

    site = pywikibot.Site('commons', 'commons')
    hotfix = WikiApiHotfix(site)
    f = codecs.open(BROKEN_LINKS_FILE, 'w', 'utf8')

    # find which images point to (potentially) missing files
    category_title = u'Category:Files with broken file links'
    category = pywikibot.Page(site, category_title)
    pages = site.categorymembers(category, namespaces=6)

    to_check = filter(lambda page: any(i in page.title() for i in IDENTIFIERS),
                      pages)

    # find which images are refered to
    missing = []
    count = 0
    for page in to_check:
        count += 1
        missing += hotfix.get_missing_images(page=page)
    missing = list(set(missing))
    print u'Found %d missing files in %d broken pages' % (len(missing), count)

    for m in missing:
        if any(i in m for i in IDENTIFIERS):
            f.write(u'%s|\n' % m)
        else:
            print m
    f.close()
    print u'Go through %s and add any known renamed files after the pipe. ' \
          u'Note that the renamed value should not include "File:"-prefix ' \
          u'(i.e. be the same as in filenames file' % BROKEN_LINKS_FILE


def fixRenamedFiles(filename=BROKEN_LINKS_FILE, configPath=u'config.json'):
    '''
    Replaces any broken file links for files known to have been renamed
    :param filename: path to output file
    :param configPath: path to config.json file
    :return: None
    '''
    f = codecs.open(filename, 'r', 'utf8')
    lines = f.read().split('\n')

    changed = []
    for l in lines:
        if not l:
            continue
        oldName, newName = l.split('|')
        if newName.strip():
            # if a rename was specified
            changed.append({'new': u'%s' % newName,
                            'old': oldName[len('File:'):]})  # strip prefix

    comApi = helpers.openConnection(configPath)
    comment = u'Fixing broken filelinks from ' \
              u'[[Commons:Batch_uploading/LSH|batch upload]]'
    while changed:
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
                    comApi.editText(name, contentsNew, comment, minor=True,
                                    bot=True, nocreate=True, userassert=None)
    print 'Check that any replacements worked since double replacements on the same ' \
          'page is known to cause errors.'


def findAllMissing(filenamesFile=FILENAME_FILE, configPath=u'config.json'):
    """
    Goes through the filenames file and checks each name for existence.
    Missing files are outputted to MISSING_FILES_FILE
    Existing files are outputted to LSH_EXPORT_FILE
    :param filenamesFile: path to filenames data file
    :param configPath: path to config.json file
    :return: None
    """
    # create targetdirectory if it doesn't exist
    if not os.path.isdir(POST_DIR):
        os.mkdir(POST_DIR)

    # load filenames file
    filenamesHeader = 'PhoId|MulId|MulPfadS|MulDateiS|filename|ext'
    filenames = helpers.csvFileToDict(filenamesFile, 'PhoId', filenamesHeader)

    # identify all Commons filenames
    files = {}
    for k, v in filenames.iteritems():
        commonsFile = u'File:%s.%s' % (v['filename'], v['ext'])
        files[commonsFile] = v
    print u'Found %d filenames' % len(files)

    # get extra info from Commons
    comApi = helpers.openConnection(configPath)
    fileInfos = comApi.getPageInfo(files.keys())

    # determine which are present and which are missing
    missing = {}
    found = {}
    prefix = u'https://commons.wikimedia.org/wiki/'
    for name, info in fileInfos.iteritems():
        if name not in files.keys():
            print name
            continue
        if 'missing' in info.keys():
            missing[name] = files[name]
        else:
            found[name] = {
                'PhoId': files[name]['PhoId'],
                'MulId': files[name]['MulId'],
                'CommonsFile': '%s%s' % (prefix, name.replace(' ', '_'))
            }

    # output files
    foundHeader = u'PhoId|MulId|CommonsFile'
    helpers.dictToCsvFile(LSH_EXPORT_FILE, found, foundHeader)
    helpers.dictToCsvFile(MISSING_FILES_FILE, missing, filenamesHeader)
    print u'Created %s and %s' % (LSH_EXPORT_FILE, MISSING_FILES_FILE)


class WikiApiHotfix(object):
    """Extends the WikiApi class with post_upload specific methods"""

    def __init__(self, site=None):
        """

        """
        self.site = site or pywikibot.Site('commons', 'commons')
        self.site.login()

    def get_missing_images(self, page=None, page_title=None):
        """
        All images linked to from a page where the given image does not exist.

        :param page: The Page to look at, as a pywikibot.Page object
        :param page_title: The page to look at, incl. any namespace prefix.
            Used only if page is not provided.
        :return: list of page titles
        """
        if not page:
            if not page_title:
                raise pywikibot.Error(
                    'get_missing_images() requires either a page title or a '
                    'pywikibot.Page object.')
            page = pywikibot.Page(self.site, page_title)
        image_links = page.imagelinks()
        members = filter(lambda image: image.pageid == 0, image_links)

        return [member.title() for member in members]

    def purge_links(self, pages=None, page_titles=None, forcelinkupdate=True,
                    verbose=False):
        """
        Trigger a purge (and link update) for the given pages.

        These are done in batches to reduce number of api calls.
        Timeout settings are temporarily changed to deal with the unusually
        long response time for a purge request and the method implements its
        own throttling to ensure it respects rate limits.

        :param pages: A list of pywkibot.Page to look at
        :param page_titles: A list of pages to look at, incl. namespace prefix.
            Used only if pages is not provided.
        :param forcelinkupdate: if links table should be updated
        :param verbose: output to log after every purge
        :return: bool (if errors were encountered)
        """
        if not pages:
            if not page_titles:
                raise pywikibot.Error(
                    'purge_links() requires a list of either pages titles or '
                    'pywikibot.Page objects.')
            pages = [pywikibot.Page(self.site, title) for title in page_titles]

        batch_size = 30
        rate_limit = 65  # default limit is 30 edits per 60 seconds
        max_timeout = 300
        original_size = len(pages)

        # bump timeout
        old_timeout = pwb_config.socket_timeout
        pwb_config.socket_timeout = max_timeout

        requestparams = {}
        if forcelinkupdate:
            requestparams['forcelinkupdate'] = True
        count = 0
        while True:
            batch = pages[:batch_size]
            pages = pages[batch_size:]
            pre_timepoint = time.time()
            result = self.site.purgepages(batch, **requestparams)
            count += len(batch)

            if verbose:
                pywikibot.output(u'Purging: %d/%d' % (count, original_size))
            if not result:
                pywikibot.output(u'Some trouble occurred while purging')

            if pages:
                # ensure the rate limit is respected
                duration = time.time() - pre_timepoint
                time.sleep(max(0, (rate_limit - duration)))
            else:
                break

        # reset timeout
        pwb_config.socket_timeout = old_timeout


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_postUpload.py action\n' \
            u'\taction: purge - purges broken fileliks in LSH files and ' \
            u'produces a file with remaining broken file links\n' \
            u'\taction: rename - repairs broken file links for any files ' \
            u'where a new name was added to broken file links then ' \
            u'updates the brokenFileLinks file ' \
            u'(overwriting any added renamings)\n' \
            u'\taction: findMissing - checks all filenames for existance ' \
            u'and produces a link table for LSH import'
    argv = sys.argv[1:]
    if len(argv) == 1:
        if argv[0] == 'purge':
            purge_broken_links()
            find_missing_images()
        elif argv[0] == 'rename':
            fixRenamedFiles()
            find_missing_images()
        elif argv[0] == 'findMissing':
            findAllMissing()
        else:
            print usage
    else:
        print usage
# EoF
