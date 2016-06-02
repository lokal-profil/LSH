# -*- coding: utf-8  -*-
#
# Methods comonly shared by the analysis files
#
# TODO: Reuse the common common.py and split off anything LSH specific
#
import codecs
import helpers
import operator  # needed by sortedDict


class Common:
    @staticmethod
    def openFileAsDictList(filename, delimiter='|', codec='utf-8',
                           headerCheck=None):
        '''
        opens a given pipe-separated csv file (utf-8)
        and returns a list of dicts, using header row for keys)
        '''
        header, lines = helpers.open_csv_file(
            filename, delimiter=delimiter, codec=codec)

        # verify header works
        if headerCheck is not None and headerCheck != header:
            print 'Header not same as comparison string!'
            exit()

        entryList = []
        for l in lines:
            if not l:  # empty line
                continue
            entry = {}
            parts = l.split(delimiter)
            for i, e in enumerate(header):
                entry[e] = parts[i]
            entryList.append(entry)
        return entryList

    @staticmethod
    def sortedDict(ddict):
        '''turns a dict into a sorted list'''
        sorted_ddict = sorted(ddict.iteritems(), key=operator.itemgetter(1),
                              reverse=True)
        return sorted_ddict

    @staticmethod
    def getPhoList(filename=u'multimedia_1.2.csv'):
        '''
        returns a list of the unique MulPhoId's in multimedia.csv
        '''
        fin = codecs.open(filename, 'r', 'utf-8')
        txt = fin.read()
        fin.close()
        lines = txt.split('\n')
        ids = []
        lines.pop()
        for l in lines:
            cols = l.split('|')
            if not cols[1] in ids:
                ids.append(cols[1])
        return ids

    @staticmethod
    def addUniqes(dDict, key, value, dcounter):
        '''
        for a given dictinary add key, value and return new value of
        duplicate counter
        '''
        if key in dDict.keys():
            if value in dDict[key]:
                dcounter += 1
            else:
                dDict[key].append(value)
        else:
            dDict[key] = [value, ]
        return dcounter

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def file_to_dict(filename, idcol=0, verbose=False, careful=False):
        '''
        reads in a file and passes it to a dict where each row is in
        turn a dict
        '''
        listcols = isinstance(idcol, list)
        header, lines = helpers.open_csv_file(filename)
        dDict = {}
        unique = True
        for l in lines:
            if not l:  # empty line
                continue
            col = l.split('|')
            # id can either be one column or a combination of several
            if listcols:
                idno = u''
                for ic in idcol:
                    idno = u'%s:%s' % (idno, col[ic])
                idno = idno[1:]  # trim leading :
            else:
                idno = col[idcol]
            wDict = {}
            for i in range(0, len(col)):
                wDict[header[i]] = col[i]
            # test for uniqueness
            if careful:
                if idno in dDict.keys():
                    unique = False
            dDict[idno] = wDict
        if verbose:
            if careful:
                print 'read %s: %r items of length %r. Uniqueness is %s' % \
                    (filename, len(dDict), len(dDict.itervalues().next()),
                     unique)
            else:
                print 'read %s: %r items of length %r.' % \
                    (filename, len(dDict), len(dDict.itervalues().next()))
        return dDict

    @staticmethod
    def makeConnections(filename, useCol=False, start=None, end=None, addpipe=False, verbose=False, multi=False, keepskip=False):
        '''
        Requires file to have the format "*keyword|...|commonsconnection" where - means ignore
           usecol: column containing the relevant value. Default = last one. If a list then values are :-separated
           start/end: Trims away this part of each string. Default = None
           addpipe: If string ends with "]]" and contains a ":" then a "|" is added just before the "]]". Default = False
           verbose: outputs read lines and found connections. Default = False
           multi: If string contains ";" then a list of values is returned. Default = False
           keepskip: Also returns "-" instead of skipping these. Default = False
        '''
        dDict = {}
        lines = codecs.open(filename, 'r', 'utf-8').read().split('\n')
        c = 0
        for l in lines:
            if l.startswith(u'===') or len(l) == 0:
                continue  # allow lists to be split by subheadings, ignore empty lines
            c += 1
            col = l[1:].split('|')  # remove leading *
            if useCol:
                connection = col[useCol]
            else:
                connection = col[-1]
            if keepskip and connection == u'-':
                dDict[col[0].strip()] = connection
            elif not len(connection) == 0 and not connection == u'-':
                connection = connection.replace(u'{{!}}', u'|')
                if multi:
                    cList = []
                    for cSub in connection.split(';'):
                        cList.append(Common.makeConnectionsSub(cSub.strip(), addpipe, start, end))
                    dDict[col[0].strip()] = cList
                else:
                    dDict[col[0].strip()] = Common.makeConnectionsSub(connection, addpipe, start, end)
            elif not connection:
                dDict[col[0].strip()] = None
        if verbose:
            print u'read in %s which had %r lines. Found %r connections' % \
                (filename, c, len(dDict))
        return dDict

    @staticmethod
    def makeConnectionsSub(connection, addpipe, start, end):
        '''broken out part of makeConnections'''
        if addpipe and connection.endswith(u']]') and u':' in connection and u'|' not in connection:
            connection = u'%s|]]' % connection[:-2]
        if start:
            if connection.startswith(start):
                connection = connection.strip()[len(start):]
                if end:
                    connection = connection.strip()[:-len(end)]
            else:
                print 'the following row has wrong formatting: %s\n' % connection
                return None  # poor man's error handling
        return connection.strip()

    @staticmethod
    def stdDate(date, risky=False):
        print 'You have called the deprecated stdDate(), please update'
        return Common.std_date(date, risky=risky)

    @staticmethod
    def std_date(date, risky=False):
        """
        Attempt to convert a string to a Commons date.

        Commons date is either isoform or using {{other_date}}.

        :param date: string to analyse
        :param risky: activate additional logic. Note that risky has not yet
                      been tested in full production and is never suitable as
                      a first run
        """
        # interpret semicolon as multiple dates
        if ';' in date:
            combined = []
            for p in date.split(';'):
                combined.append(Common.std_date(p))
                if combined[-1] is None:  # if any fails then fail all
                    return None
            return u'; '.join(combined)

        # A single date, or range
        date = date.strip(u'.  ')
        if len(date) == 0 or date == u'n.d':
            return u''  # this is equivalent to u'{{other date|unknown}}'
        date = date.replace(u' - ', u'-')

        # Atempt risky tactic
        # Note that this should only be run on values which have failed a first run
        # Note also that it calls the std_date function WITHOUT the risky option
        if risky and (len(date.split(u'-')) == 2):
            combined = []
            for p in date.split(u'-'):
                combined.append(Common.std_date(p))
                if combined[-1] is None:  # if any fails then fail all
                    return None
            return Common.other_date_range(combined[0], combined[1])

        # Non-risky continues
        endings = {
            u'?': u'?',
            u'(?)': u'?',
            u'c': u'ca',
            u'ca': u'ca',
            u'cirka': u'ca',
            u'andra hälft': u'2half',
            u'första hälft': u'1half',
            u'början': u'early',
            u'slut': u'end',
            u'slutet': u'end',
            u'mitt': u'mid',
            u'första fjärdedel': u'1quarter',
            u'andra fjärdedel': u'2quarter',
            u'tredje fjärdedel': u'3quarter',
            u'fjärde fjärdedel': u'4quarter',
            u'sista fjärdedel': u'4quarter',
            u'före': u'<',
            u'efter': u'>',
            u'-': u'>'}
        starts = {
            u'tidigt': u'early',
            u'br av': u'early',
            u'tid ': u'early',
            u'sent': u'late',
            u'sl av': u'late',
            u'ca': u'ca',
            u'våren': u'spring',
            u'sommaren': u'summer',
            u'hösten': u'fall',
            u'vintern': u'winter',
            u'sekelskiftet': u'turn of the century',
            u'före': u'<',
            u'efter': u'>',
            u'-': u'<'}
        tal_endings = [u'-talets', u'-tal', u'-talet', u' talets']
        modality_endings = [u'troligen', u'sannolikt']
        for k, v in starts.iteritems():
            if date.lower().startswith(k):
                return Common.other_date_if_more(v, date[len(k):])
        for k, v in endings.iteritems():
            if date.lower().endswith(k):
                return Common.other_date_if_more(v, date[:-len(k)])
        for k in modality_endings:
            if date.lower().endswith(k):
                date = date[:-len(k)].strip(u'.,  ')
                again = Common.std_date(date)
                if again:
                    return u'%s {{Probably}}' % again
                else:
                    return None
        for k in tal_endings:
            if date.lower().endswith(k):
                date = date[:-len(k)].strip(u'.  ')
                # attempt century matchings
                try:
                    return Common.other_date_century(date)
                except helpers.MyError:
                    if len(date.split('-')) == 2:
                        try:
                            part = date.split('-')
                            return Common.other_date_range(
                                Common.other_date_century(part[0]),
                                Common.other_date_century(part[1]))
                        except helpers.MyError:
                            pass

                # assume decade
                return Common.other_date_if_more(u'decade', date)

        # reach this point if all else fails
        return Common.std_numeric_date(date)

    @staticmethod
    def other_date_if_more(typ, remainder):
        """
        Return {{other_date|typ}} if remainder can be interpreted by std_date.
        """
        again = Common.std_date(remainder)
        if again:
            return u'{{other date|%s|%s}}' % (typ, again)
        else:
            return None

    @staticmethod
    def other_date_century(year):
        """Return {{other_date|century}} for a given year."""
        # TODO add year[-2:] == u'00' and helpers.is_int(year) testing
        if not helpers.is_int(year) or int(year[-2:]) != 0:
            raise helpers.MyError(
                u'other_date_century() expects year in the format YY00 or Y00')
        return '{{other date|century|%d}}' % (int(year[:-2]) + 1)

    @staticmethod
    def other_date_range(date_from, date_to):
        """
        Return a {{other_date}} for a given range.

        Gives:
        * {{other_date|-}} if both to and from
        * {{other_date|>}} if just from
        * {{other_date|<}} if just to
        raises an error if both are empty
        """
        if date_from and date_to:
            return u'{{other date|-|%s|%s}}' % (date_from, date_to)
        elif date_from:
            return u'{{other date|>|%s}}' % date_from
        elif date_from:
            return u'{{other date|<|%s}}' % date_to
        else:
            raise helpers.MyError(
                u'other_date_range() must get at least one non-empty value')

    @staticmethod
    def std_numeric_date(date):
        """
        Attempt to convert a numeric (+ dash) string as a Commons date.

        Note that standard string_to_ISO dunctions don't work, mainly since
        ####-## is YYYY-YY not the standard YYYY-MM.
        :param date: string to analyse
        :return: string
        """
        if date.strip('1234567890-'):
            # if string contains anything other than numbers and dash
            return

        parts = date.split('-')
        if len(parts) == 3 and len(parts[0]) == 4 and \
                len(parts[1]) == 2 and len(parts[2]) == 2:
            # YYYY-MM-DD
            return date
        elif len(parts) == 2:
            if (len(parts[0]) == 4 and len(parts[1]) in (0, 4)) or \
                    (len(parts[0]) == 0 and len(parts[1]) == 4):
                # YYYY-YYYY or YYYY- or -YYYY
                return Common.other_date_range(parts[0], parts[1])
            elif len(parts[0]) == 4 and len(parts[1]) == 2:
                # YYYY-YY
                parts[1] = u'%s%s' % (parts[0][:2], parts[1])
                return Common.other_date_range(parts[0], parts[1])
        elif len(parts) == 1 and len(parts[0]) == 4:
            # YYYY
            return date
        else:
            return None

    @staticmethod
    def findUnit(contents, start, end, brackets=None):
        u'''
        Method for isolating an object in a string. Will not work with either
        start or end using the ¤ symbol
        @input:
            * content: the string to look at
            * start: the substring indicating the start of the object
            * end: the substring indicating the end of the object
            * brackets: a dict of brackets used which must match
                        within the object
        @output:
            the-object, lead-in-to-object, the-remainder-of-the-string
            OR None, None, None if an error
            OR '', '', '' if no object is found
        '''
        if start in contents:
            uStart = contents.find(start) + len(start)
            uEnd = contents.find(end, uStart)
            if brackets:
                for bStart, bEnd in brackets.iteritems():
                    dummy = u'¤' * len(bEnd)
                    diff = contents[uStart:uEnd].count(bStart) - contents[uStart:uEnd].count(bEnd)
                    if diff < 0:
                        print 'Negative bracket missmatch for: %s <--> %s' % (bStart, bEnd)
                        return None, None, None
                    i = 0
                    while(diff > 0):
                        i += 1
                        uEnd = contents.replace(bEnd, dummy, i).find(end, uStart)
                        if uEnd < 0:
                            print 'Positive (final) bracket missmatch for: %s <--> %s' % (bStart, bEnd)
                            return None, None, None
                        diff = contents[uStart:uEnd].count(bStart) - contents[uStart:uEnd].count(bEnd)
            unit = contents[uStart:uEnd]
            lead_in = contents[:uStart - len(start)]
            remainder = contents[uEnd + len(end):]
            return (unit, remainder, lead_in)
        else:
            return '', '', ''
# done
