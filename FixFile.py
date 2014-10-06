# -*- coding: UTF-8  -*-
#
# this replaces linebreaks within cells of a csv file by <!>
# requires UTF encoding \n linebreaks and | cell separation
# the first cell must NEVER be linebroken (since one cannot detect the difference between a linbroken last cell and a linebroken first cell)
#
import re
import codecs
import os
import operator


def fixFile(filename=None, encoding='utf-8'):  # use utf-16 for original files
    if filename:
        fixLinebreak(filename, encoding)
    else:
        dirList = os.listdir(u'%s' % os.getcwd())
        for fname in dirList:
            if fname.endswith(u'.csv'):
                fixLinebreak(fname, encoding)


def fixLinebreak(filename, encoding):
    fin = codecs.open(filename, 'r', encoding)
    txt = fin.read()
    fin.close()
    txt = txt.replace(u'\r\n', u'\n')  # if windows encoded
    txt = txt.replace(u'\r', u'<!>')   # if any remaining
    lines = txt.split('\n')
    header = lines[0].split('|')
    #
    if lines[len(lines)-1] == u'':     # remove last blank line which is added by read()
        lines.pop()
    #
    fileOut = u'mod-%s' % filename
    # fileOut = u'%s-mod.csv' % filename[:-4]
    f = codecs.open(fileOut, 'w', 'utf-8')
    first = True
    prevline = u''
    for line in lines:
        if (prevline == u'') and (len(line.split('|')) == 1):    # if the last cell is line broken then this is the only way of detecting it
            f.write(u'<!>%s' % line)
            continue
        comb = u'%s<!>%s' % (prevline, line)
        if not first:
            if len(comb.split('|')) == len(header):
                f.write(u'\n%s' % comb[3:])  # remove leading <!>
                prevline = u''         # reset prevline
            else:
                prevline = comb      # set prevline
        else:
            f.write(line)
            first = False
    if not (prevline == u'' or prevline == u'<!>'):    # verifies that no data has remained unprinted
        print 'The following line was not printed to <%s>: <%s>' % (filename, prevline)
    f.close()
#
