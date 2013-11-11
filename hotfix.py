#!/usr/bin/python
# -*- coding: utf-8  -*-
import WikiApi as wikiApi
import config as config
import codecs

def run(filename):
    f = codecs.open(filename,'r','utf8')
    lines = f.read().split('\n')
    
    changed = []
    for l in lines:
        if len(l)==0:continue
        oldName = u'%s.tif' %l[:-4]
        changed.append({'new':l,'old':oldName})
    
    comApi = wikiApi.WikiApi.setUpApi(user=config.username, password=config.password, site=config.site)
    
    while len(changed)>0:
        active = changed.pop()
        links = comApi.getImageUsage(u'File:%s' %active['old'], iunamespace=6) 
        if links:
            pages = comApi.getPage(links)
            for name, contents in pages.iteritems():
                contentsNew = contents.replace(active['old'],active['new'])
                #whilst we are here replace any others
                for c in changed:
                    contentsNew = contentsNew.replace(c['old'],c['new'])
                if contents == contentsNew:
                    print 'no change for %s' %name
                else:
                    comApi.editText(name, contentsNew, u'Fixing broken filelinks from [[Commons:Batch_uploading/LSH|batch upload]]', minor=True, bot=True, nocreate=True, userassert=None)
    

def findMissingImages():
    api = WikiApiHotfix.setUpApi(user=config.username, password=config.password, site=config.site)
    f = codecs.open(u'BrokenFileLinks.csv','w','utf8')
    
    pages = api.getCategoryMembers(categoryname=u'Category:Files with broken file links', cmnamespace=6)
    print u'Found %r pages' %len(pages)
    missing = []
    for page in pages:
        missing = missing + api.getMissingImages(page)
    missing=list(set(missing))
    print u'Found %r missing files' %len(missing)
    
    for m in missing:
        if (u'Livrustkammaren' in m) or (u'Skoklosters' in m) or (u'Hallwylska' in m):
            f.write(u'%s\n' %m)
        else:
            print m
    f.close()

def findAllMissing(infile=u'deriv-filenames.csv'):
    '''
    Goes through the filenames file and checks for existence for each file in it
    '''
    comApi = wikiApi.WikiApi.setUpApi(user=config.username, password=config.password, site=config.site)
    
    f = codecs.open(infile,'r','utf8')
    lines=f.read().split('\n')
    f.close()
    
    f = codecs.open(u'AllMissingFiles.csv','w','utf8')
    f.write(u'%s\n' %lines.pop(0))
    
    files = {}
    for l in lines:
        if len(l)==0:continue
        PhoId, MulId, MulPfadS, MulDateiS, filename = l.split('|')
        files[u'File:%s' %filename]=l
    
    print u'Found %r filenames' %len(files)
    
    fileInfos = comApi.getPageInfo(files.keys())
    for name, info in fileInfos.iteritems():
        if 'missing' in info.keys():
            f.write(u'%s\n' %files[name])
    f.close()
    

class WikiApiHotfix(wikiApi.WikiApi):
    '''Extends the WikiApi class with hotfix specific methods'''
    
    def getMissingImages(self, page, debug=False):
        '''
        Returns a list of all images linked to from a page where the given image does not exist
        :param page: The page to look at, incl. any namespace prefix
        :param iunamespace: namespace to limit the search to (0=main, 6=file)
        :return: list of pagenames
        '''
        #print "Fetching getMissingImages: " + page
        members = []
        #action=query&prop=images&format=json&imlimit=1&titles=File%3AFoo.jpg&generator=images&gimlimit=100
        jsonr = self.httpPOST("query", [('prop', 'images'),
                                        ('titles', page.encode('utf-8')),
                                        ('imlimit', '1'),
                                        ('generator', 'images'),
                                        ('gimlimit', '100')])
        
        if debug:
            print u'getMissingImages() page:%s \n' %page
            print jsonr
        
        #"query":{"pages":{"-1":{"ns":6,"title":"File:Axelgeh\u00e4ng - Livrustkammaren - 42925.tif","missing":""}
        for page in jsonr['query']['pages']:
            if int(page) <0:
                page = jsonr['query']['pages'][page]
                #if 'missing' in page.keys():
                members.append(page['title'])
        
        #print  "Fetching getMissingImages: " + page + "...complete"
        return members
