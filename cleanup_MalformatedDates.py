#
# Cleanup
# Corrects misstake with empty date being tagged as malformated
# Corrects new logic for multiple dates
#
# Also useful for new runs with risky=True
# 
#!/usr/bin/python
# -*- coding: utf-8  -*-
import WikiApi as wikiApi
import config as config
from common import Common
from time import sleep

def run(test=True, risky=False):
    api = wikiApi.WikiApi.setUpApi(user=config.username, password=config.password, site=config.site)
    editcomment = u'Fixing malformated date and removing maintanance cat, empty date is not malformated'
    
    pages = api.getCategoryMembers(categoryname=u'Category:Media contributed by LSH: malformated year', cmnamespace=6)
    print u'Found %r pages in cat' %len(pages)
    
    #retrieve content for all of these
    content = api.getPage(pages)
    
    #check which should be fixed
    fixCat = {}
    p = u'|date= '
    for k, v in content.iteritems():
        if p +u'\n|' in v: #i.e. empty
            fixCat[k] = v.replace(u'\n[[Category:Media contributed by LSH: malformated year]]','')
        elif p in v:
            date = v[v.find(p)+len(p):v.find(u'\n|',v.find(p))]
            stdDate = Common.stdDate(date, risky=risky)
            if stdDate is not None:
                if '{{' in date:
                    print 'seems to be a lagg in the categorymembers. Skipping "%s"' %k
                    continue
                if test: print date, u'-->', stdDate
                fixCat[k] = v.replace(u'\n[[Category:Media contributed by LSH: malformated year]]','').replace(p+date,p+stdDate)
    
    print u'Found %r pages in need of update' %len(fixCat.keys())
    if test: exit(1)
    #upload updates
    for k, v in fixCat.iteritems():
        api.editText(k, v, editcomment, minor=True, bot=True, userassert=None, nocreate=True, debug=False, append=False)
        sleep(0.05) #play nice
