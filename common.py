# -*- coding: UTF-8  -*-
#
# Methods comonly shared by the analysis files
#
import codecs
import os
import operator

class Common:
    @staticmethod
    def openFile(filename):
        '''opens a given file (utf-8) and returns the header row plus following lines)'''
        fin = codecs.open(filename, 'r', 'utf-8')
        txt = fin.read()
        fin.close()
        lines = txt.split('\n')
        header = lines[0].split('|')
        lines.pop()
        return header, lines
    @staticmethod
    def sortedDict(ddict):
        '''turns a dict into a sorted list'''
        sorted_ddict = sorted(ddict.iteritems(), key=operator.itemgetter(1), reverse=True)
        return sorted_ddict
    @staticmethod
    def getPhoList(filename=u'multimedia_1.2.csv'):
        '''returns a list of the unique MulPhoId's in multimedia.csv'''
        fin = codecs.open(filename, 'r', 'utf-8')
        txt = fin.read()
        fin.close()
        lines = txt.split('\n')
        ids=[]
        lines.pop()
        for l in lines:
            cols = l.split('|')
            if not cols[1] in ids:
                ids.append(cols[1])
        return ids
    @staticmethod
    def addUniqes(dDict, key, value, dcounter):
        '''for a given dictinary add key, value and return new value of duplicate counter'''
        if key in dDict.keys():
            if value in dDict[key]:
                dcounter = dcounter+1
            else:
                dDict[key].append(value)
        else:
            dDict[key] = [value,]
        return dcounter
    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    @staticmethod
    def file_to_dict(filename, idcol=0, verbose=False, careful=False):
        '''reads in a file and passes it to a dict where each row is in turn a dict'''
        listcols = isinstance(idcol,list)
        header, lines = Common.openFile(filename)
        dDict = {}
        unique=True
        first = True
        for l in lines:
            if first:
                first=False
                continue
            col = l.split('|')
            #id can either be one column or a combination of several
            if listcols:
                idno=u''
                for ic in idcol:
                    idno=u'%s:%s' % (idno,col[ic])
                idno = idno[1:] #trim leading :
            else:
                idno = col[idcol]
            wDict = {}
            for i in range(0,len(col)):
                wDict[header[i]] = col[i]
            #test for uniqueness
            if careful:
                if idno in dDict.keys():
                    unique=False
            dDict[idno] = wDict
        if verbose:
            if careful:
                print 'read %s: %r items of length %r. Uniqueness is %s' % (filename, len(dDict), len(dDict.itervalues().next()),unique)
            else:
                print 'read %s: %r items of length %r.' % (filename, len(dDict), len(dDict.itervalues().next()))
        return dDict
    @staticmethod
    def makeConnections(filename, useCol=False, start=None, end=None, addpipe=False, verbose=False, multi=False):
        '''Requires file to have the format "*keyword|...|commonsconnection" where - means ignore
           usecol: column containing the relevant value. Default = last one. If a list then values are :-separated
           start/end: Trims away this part of each string. Default = None
           addpipe: If string ends with "]]" and contains a ":" then a "|" is added just before the "]]". Default = False
           verbose: outputs read lines and found connections. Default = False
           multi: If string contains ";" then a list of values is returned. Default = False
        '''
        dDict = {}
        header, lines = Common.openFile(filename)
        intro = True
        c=0
        for l in lines:
            if intro:
                if l.startswith(u'==='): intro=False
                continue
            if l.startswith(u'===') or len(l)==0: continue #allow lists to be split by subheadings, ignore empty lines
            c=c+1
            col = l[1:].split('|')  #remove leading *
            if useCol:
                connection = col[useCol]
            else:
                connection = col[len(col)-1]
            if not len(connection) == 0 and not connection==u'-':
                connection = connection.replace(u'{{!}}',u'|')
                if multi:
                    cList = []
                    for cSub in connection.split(';'):
                        cList.append(Common.makeConnectionsSub(cSub.strip(), addpipe, start, end))
                    dDict[col[0].strip()] = cList
                else:
                    dDict[col[0].strip()] = Common.makeConnectionsSub(connection, addpipe, start, end)
            elif len(connection) == 0:
                dDict[col[0].strip()] = None
        if verbose:
            print u'read in %s which had %r lines. Found %r connections' %(filename,c,len(dDict))
        return dDict
    @staticmethod
    def makeConnectionsSub(connection, addpipe, start, end):
        '''broken out part of makeConnections'''
        if addpipe and connection.endswith(u']]') and u':' in connection:
            connection= u'%s|]]' % connection[:-2]
        if start:
            if connection.startswith(start):
                connection = connection.strip()[len(start):]
                if end:
                    connection = connection.strip()[:-len(end)]
            else:
                print 'the following row has wrong formatting: %s\n' %connection
                return None #por man's error handling
        return connection.strip()
    @staticmethod
    def stdDate(date):
        '''returns a standardised date in isoform or for other date template'''
        #interpret semicolon as multiple dates
        if ';' in date:
            combined = []
            for p in date.split(';'):
                combined.append(Common.stdDate(p))
                if combined[-1] is None: #if any fails then fail all
                    return None
            return u'; '.join(combined)
        
        #A single date, or range
        date=date.strip(u'.  ')
        if len(date) == 0:
            return u'' #this is equivalent to u'{{other date|unknown}}'
        date=date.replace(u' - ', u'-')
        endings = {u'?':u'?',
                u'(?)':u'?', 
                u'c':u'ca', 
                u'ca':u'ca', 
                u'cirka':u'ca',                 
                u'Cirka':u'ca',
                u'andra hälft':u'2half', 
                u'första hälft':u'1half', 
                u'början':u'early',
                u'slut':u'end',
                u'mitt':u'mid',
                u'första fjärdedel':u'1quarter',
                u'andra fjärdedel':u'2quarter',
                u'tredje fjärdedel':u'3quarter',
                u'fjärde fjärdedel':u'4quarter',
                u'Före':u'<',
                u'Efter':u'>',
                u'före':u'<',
                u'efter':u'>'}
        talEndings = [u'-talets', u'-tal', u'-talet', u' talets']
        modalityEndings = [u'troligen',u'sannolikt']
        for k,v in endings.iteritems():
            if date.endswith(k):
                again = Common.stdDate(date[:-len(k)])
                if again: return u'{{other date|%s|%s}}' % (v, again)
                else: return None
        for k in modalityEndings:
            if date.endswith(k):
                date = date[:-len(k)].strip(u'.,  ')
                again = Common.stdDate(date)
                if again: return u'%s {{Probably}}' % again
                else: return None
        for k in talEndings:
            if date.endswith(k):
                date = date[:-len(k)].strip(u'.  ')
                if date[-2:] == u'00':
                    v = u'century'
                    if len(date) == 4:
                        return u'{{other date|%s|%r}}' %(v,int(date[:2])+1)
                    elif len(date) == 9:
                        return u'{{other date|-|{{other date|%s|%s}}|{{other date|%s|%s}}}}' %(v,int(date[:2])+1,v,int(date[5:7])+1)
                    else:
                        return None
                else:
                    v = u'decade'
                again = Common.stdDate(date)
                if again: return u'{{other date|%s|%s}}' % (v, again)
                else: return None
        ldate = len(date)
        if ldate == 10: #YYYY-MM-DD
            if Common.is_number(date[:4]) and Common.is_number(date[5:7]) and Common.is_number(date[-2:]):
                return u'%s-%s-%s' %(date[:4], date[5:7], date[-2:])
        elif ldate == 9: #YYYY-YYYY
            if Common.is_number(date[:4]) and Common.is_number(date[-4:]):
                return u'{{other date|%s|%s|%s}}' %(u'-',date[:4], date[-4:])
        elif ldate == 7: #YYYY-YY
            if Common.is_number(date[:4]) and Common.is_number(date[-2:]):
                return u'{{other date|%s|%s|%s%s}}' %(u'-',date[:4], date[:2], date[-2:])
        elif ldate == 5: #YYYY-
            if date[:1] == '-' and Common.is_number(date[1:]):
                return u'{{other date|%s|%s}}' %(u'<',date[1:])
            elif date[4:5] == '-' and Common.is_number(date[:4]):
                return u'{{other date|%s|%s}}' %(u'>',date[:4])
        elif ldate == 4: #YYYY
            if Common.is_number(date):
                return date
        else:
            return None
    @staticmethod
    def findUnit(contents, start, end, brackets=None):
        '''
        Method for isolating an object in a string. Will not work with either start or end using the ¤ symbol
        @input: 
            * content: the string to look at
            * start: the substring indicateing the start of the object
            * end: the substring indicating the end of the object
            * brackets: a dict of brackets used which must match within the object
        @output:
            the-object, lead-in-to-object, the-remainder-of-the-string
            OR None,None if an error
            OR '','' if no object is found
        '''
        if start in contents:
            uStart = contents.find(start) + len(start)
            uEnd = contents.find(end,uStart)
            if brackets:
                for bStart,bEnd in brackets.iteritems():
                    dummy=u'¤'*len(bEnd)
                    diff = contents[uStart:uEnd].count(bStart) - contents[uStart:uEnd].count(bEnd)
                    if diff<0:
                        print 'Negative bracket missmatch for: %s <--> %s' %(bStart,bEnd)
                        return None, None, None
                    i=0
                    while(diff >0):
                        i=i+1
                        uEnd = contents.replace(bEnd,dummy,i).find(end,uStart)
                        if uEnd < 0:
                            print 'Positive (final) bracket missmatch for: %s <--> %s' %(bStart,bEnd)
                            return None, None, None
                        diff = contents[uStart:uEnd].count(bStart) - contents[uStart:uEnd].count(bEnd)
            unit = contents[uStart:uEnd]
            lead_in = contents[:uStart-len(start)]
            remainder = contents[uEnd+len(end):]
            return (unit, remainder, lead_in)
        else:
            return '','',''
#done
