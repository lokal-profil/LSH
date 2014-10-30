#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# PyCJWiki Version 1.31
# Requires python2.7, ujson, and PyCurl

#----------------------------------------------------------------------------------------
# Copyright (2013) Smallman12q (https://en.wikipedia.org/wiki/User_talk:Smallman12q)
#
# LICENSE:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pycurl, ujson, cStringIO
import time
import mmap
import traceback

class Wiki(object):


    class Delay:
        """
            Delay enum, the delays for requests etc.
            Delay implemented as sleep before given request...could be improved
        """
        ALLREQUESTS = 0
        UPLOAD = 0

    #useragenturl and contac in unicode
    #
    def __init__(self, apiurl, useragentidentify):
        """
        :param apiurl: The url of the api.php such as https://commons.wikimedia.org/w/api.php
            Pass as str
        :param useragentidentify: The identification to be sent in the header.
            Such as u'https://commons.wikimedia.org/wiki/User_talk:Smallman12q'
            Part of https://www.mediawiki.org/wiki/Api#Identifying_your_client
            Pass as u
        """

        #Wiki vars
        self._apiurl = apiurl
        self.userName = None
        self.tokens = []
        self.edittoken = None

        #Response buffer
        self.responsebuffer= cStringIO.StringIO()
        self.clearresponsebufferafterresponse = False #True will clear, and save memory, but less useful if error

        #Set up reusable curl connection
        self.sitecurl=pycurl.Curl()
        self.sitecurl.setopt(pycurl.WRITEFUNCTION, self.responsebuffer.write) #Writes to response buffer
        self.sitecurl.setopt(pycurl.COOKIEFILE, "") #Use in-memory cookie
        self.sitecurl.setopt(pycurl.USERAGENT, 'PyCJWiki/1.3 (' + useragentidentify.encode('utf-8') + ')')
        self.sitecurl.setopt(pycurl.POST, 1)
        self.sitecurl.setopt(pycurl.CONNECTTIMEOUT, 60)
        self.sitecurl.setopt(pycurl.TIMEOUT, 120)
        self.sitecurl.setopt(pycurl.ENCODING, 'gzip, deflate')
        self.sitecurl.setopt(pycurl.HTTPHEADER,["Expect:", "Connection: Keep-Alive", "Keep-Alive: 60"])
        #self.sitecurl.setopt(pycurl.PROXY, 'http://localhost:8888') #Proxy if needed


    def httpPOST(self, action, params, depth=0, timeoutretry=0):
        """

        :param action: The action, pass as str
        :param params: The params to be posted
        :param depth: A counter used for recursive failed stashes
        :param timeoutretry: A counter for timeoutretries
        :return:
        """
        #Clear response buffer
        self.responsebuffer.truncate(0)

        #Set curl http request
        self.sitecurl.setopt(pycurl.URL, self.apiaction(action))
        self.sitecurl.setopt(pycurl.HTTPPOST, params)

        #Try the curl http request
        try:
            time.sleep(self.Delay.ALLREQUESTS)
            self.sitecurl.perform()
        except pycurl.error, error:
            errno, errstr = error
            print( 'An error occurred: ' + str(errno) + ':', errstr)
            traceback.print_exc()

            #Response Timed Out, Retry up to 3 times
            if(errno == 28):
                if(timeoutretry < 3):
                    time.sleep(2)
                    self.httpPOST(action,params,depth,timeoutretry=(timeoutretry+1))

        #print self.responsebuffer.getvalue()
        json = ujson.loads(self.responsebuffer.getvalue())
        if "servedby" in json: #Some sort of error
            if "error" in json:
                if "code" in json["error"]:
                    #Bug 36587
                    if json["error"]["code"] == "internal_api_error_UploadChunkFileException":
                        if(depth < 3):
                            time.sleep(2)
                            self.httpPOST(action,params,(depth + 1))
            #maybe throw something?

        if self.clearresponsebufferafterresponse:
            self.responsebuffer.truncate(0)

        return json

    def printResponseBuffer(self):
        print self.responsebuffer.getvalue()

    #username,userpass unicode
    def login(self, userName, userPass):
        """
        :param userName: username as u
        :param userPass: userpassword as u. Not stored after login
        :return:
        :eturns type:
        """
        print "Logging into " + self._apiurl + " as " + userName
        print "Logging in...(1/2)"

        #Login
        jsonr = self.httpPOST("login", [('lgname', userName.encode('utf-8')),
                                        ('lgpassword', userPass.encode('utf-8'))])
        if 'NeedToken' in jsonr['login']['result']:
            print "Logging in...(1/2)...Success!"
        else:
            print "Logging in...(1/2)...Failed."
            self.printResponseBuffer()
            exit()

        #Login 2/2
        print "Logging in...(2/2)"
        jsonr = self.httpPOST("login", [('lgname', userName.encode('utf-8')),
                                        ('lgpassword', userPass.encode('utf-8')),
                                        ('lgtoken',str(jsonr['login']['token']))])
        if 'Success' in jsonr['login']['result']:
            print "Logging in...(2/2)...Success!"

        else :
            print "Logging in...(2/2)...Failed"
            self.printResponseBuffer()
            exit()

        self.userName = userName #Now logged in
        print "You are now logged in as " + self.userName

    def setToken(self, token):
        print "Retrieving token: " + token
        jsonr = self.httpPOST("tokens", [('type', str(token))])
        if(jsonr['tokens']['edittoken'] == "+\\"):
            print "Edit token not set."
            self.printResponseBuffer()
            exit()
        else:
            self.edittoken = str(jsonr['tokens']['edittoken'])
            print "Edit token retrieved: " + self.edittoken

    def setEditToken(self):
        self.setToken('edit')

    def clearEditToken(self):

        self.edittoken = None
        #TODO Clear in tokens dict when implemented

    def getcategorymembers(self, categoryname, cmnamespace):
        """

        """

        print "Fetching categorymembers: " + categoryname
        members = []
        #action=query&list=categorymembers&cmtitle=Category:Physics
        jsonr = self.httpPOST("query", [('list', 'categorymembers'),
                                        ('cmtitle', categoryname.encode('utf-8')),
                                        ('cmnamespace', str(cmnamespace)),
                                        ('cmlimit', '500')])

        #print self.responsebuffer.getvalue()

        #{"query":{"categorymembers":[{"pageid":22688097,"ns":0,"title":"Branches of physics"}]},"query-continue":{"categorymembers":{"cmcontinue":"page|200a474c4f5353415259204f4620434c4153534943414c2050485953494353|3445246"}}}
        for page in jsonr['query']['categorymembers']:
            members.append((page['title']))


            # print "print m"
        #for member in members:
        #    print member

        while 'query-continue' in jsonr:
            print  "Fetching categorymembers: " + categoryname + "...fetching more"
            #print jsonr['query-continue']['categorymembers']['cmcontinue']
            jsonr = self.httpPOST("query", [('list', 'categorymembers'),
                                            ('cmtitle', categoryname.encode('utf-8')),
                                            ('cmlimit', '500'),
                                            ('cmnamespace', str(cmnamespace)),
                                            ('cmcontinue', str(jsonr['query-continue']['categorymembers']['cmcontinue']))])
            for page in jsonr['query']['categorymembers']:
                members.append((page['title']))


        print  "Fetching categorymembers: " + categoryname + "...complete"
        return members
        #members.append()

    def movePage(self, fromTitle, toTitle, reason, noRedirect=False):
        #https://en.wikipedia.org/w/api.php?action=move&from=Main%20Pgae&to=Main%20Page&reason=Oops,%20misspelling&movetalk&noredirect&token=58b54e0bab4a1d3fd3f7653af38e75cb%2B\
        print "Moving page: " + fromTitle.encode('utf-8','ignore') + " -> " + toTitle.encode('utf-8','ignore')
        jsonr = self.httpPOST("move", [('from', fromTitle.encode('utf-8')),
                                       ('to', toTitle.encode('utf-8')),
                                       ('reason', reason.encode('utf-8')),
                                       ('token', str(self.edittoken)),
                                       ('movetalk',''),
                                       (('','noredirect')[noRedirect],'')])
        if "move" in jsonr.keys():
            print "Success"
            return None
        else:
            return jsonr

    def getText(self, title,resolveredirects=False):
        #title = self.su(title)
        #http://en.wikipedia.org/w/api.php?format=xml&action=query&titles=Albert%20Einstein&prop=revisions&rvprop=content&format=jsonfm
        #print(str(title))
        #none is missing or invalid title

        if(type(title) is list
           or type(title) is tuple):

            print "Getting titles: " + str(title)
            jsonr = self.httpPOST("query", [('titles', "|".join(title).encode('utf-8')),
                                            ('prop', 'revisions'),
                                            ('rvprop', 'content'),
                                            (('','redirects')[resolveredirects],'')])
            articlecontentdict={}
            for article in jsonr['query']['pages']:
                if(article == "-1"):
                    articlecontentdict[jsonr['query']['pages'][article]['title']]=""#None
                    #Either missing or invalid
                else:
                    articlecontentdict[jsonr['query']['pages'][article]['title']]=\
                    jsonr['query']['pages'][article]['revisions'][0]['*']
            return articlecontentdict

        else:
            print "Getting..." + title
            jsonr = self.httpPOST("query", [('titles', title.encode('utf-8')),
                                            ('prop', 'revisions'),
                                            ('rvprop', 'content'),
                                            (('','redirects')[resolveredirects],'')])

            if "-1" in jsonr['query']['pages']:
                print "missing"
                return None
            else:
                return jsonr['query']['pages'].values()[0]['revisions'][0]['*']

    def getCategoryMemberTexts(self,category,cmnamespace):
        #https://commons.wikimedia.org/w/api.php?action=query&generator=categorymembers&gcmtitle=Category:Physics&gcmlimit=500&prop=revisions&rvprop=content&format=jsonfm
        print ('Getting... ' +  category.encode('utf-8','ignore'))
        jsonr = self.httpPOST("query", [('generator', "categorymembers"),
                                        ("gcmtitle", category.encode('utf-8')),
                                        ("gcmnamespace",str(cmnamespace)),
                                        ("gcmlimit","500"),
                                        ('prop', 'revisions'),
                                        ('rvprop', 'content')])
        articlecontentdict={}

        if jsonr == []:#If empty
            return {}
        for article in jsonr['query']['pages']:
            if(article == "-1"):
                print "Empty page:" + jsonr['query']['pages'][article]['title']
                #articlecontentdict[jsonr['query']['pages'][article]['title']]=""#None
                #Either missing or invalid
                #Should not happen...empty pages can't be in category
            else:
                articlecontentdict[jsonr['query']['pages'][article]['title']]=\
                jsonr['query']['pages'][article]['revisions'][0]['*']

        while 'query-continue' in jsonr:
            print ('Getting more... {0}'.format(category))
            jsonr = self.httpPOST("query", [('generator', "categorymembers"),
                                            ("gcmtitle", category.encode('utf-8')),
                                            ("gcmnamespace",str(cmnamespace)),
                                            ("gcmlimit","500"),
                                            ("gcmcontinue",jsonr['query-continue']['categorymembers']['gcmcontinue'].encode('utf-8')),
                                            ('prop', 'revisions'),
                                            ('rvprop', 'content')])

            for article in jsonr['query']['pages']:
                if(article == "-1"):
                    print "Empty page:" + jsonr['query']['pages'][article]['title']
                    #articlecontentdict[jsonr['query']['pages'][article]['title']]=""#None
                    #Either missing or invalid
                    #Should not happen...empty pages can't be in category
                else:
                    articlecontentdict[jsonr['query']['pages'][article]['title']]=\
                    jsonr['query']['pages'][article]['revisions'][0]['*']
        return articlecontentdict

    def createPage(self, title, text, comment):
        print("Creating " + title.encode('utf-8','ignore'))
        jsonr = self.httpPOST("edit", [('title',  title.encode('utf-8')),
                                       ('text', text.encode('utf-8')),
                                       ('summary', comment.encode('utf-8')),
                                       ('token', str(self.edittoken)),
                                       ('minor', 'true'),
                                       ('create','true'),
                                       ('bot', 'true'),
                                       ('assert', 'bot')])


        if 'edit' in jsonr:
            if(jsonr['edit']['result'] == "Success"):
                print "Creating " + title.encode('utf-8','ignore') + "...Success"
        else:
            print "Creating " + title + "...Failure"
            print self.responsebuffer.getvalue()
            #exit()
            #time.sleep(.2)


    def editText(self, title, newtext, comment, minor=False,bot=True,userassert='bot', nocreate=False):
        txt = ''
        print("Editing " + title.encode('utf-8','ignore'))
        requestparams = [('title',  title.encode('utf-8')),
                         ('text', newtext.encode('utf-8')),
                         ('summary', comment.encode('utf-8')),
                         ('token', str(self.edittoken))]
        if minor:
            requestparams.append(('minor', 'true'))
        if bot:
            requestparams.append(('bot', 'true'))
        if userassert is not None:
            requestparams.append(('assert', userassert))
        if nocreate:
            requestparams.append(('nocreate','true'))

        jsonr = self.httpPOST("edit", requestparams)

        if 'edit' in jsonr:
            if(jsonr['edit']['result'] == "Success"):
                txt = txt +  "Editing " + title.encode('utf-8','ignore') + "...Success"
            return txt
        else:
            txt = txt +  "Editing " + title.encode('utf-8','ignore') + "...Failure"
            txt = txt +  self.responsebuffer.getvalue()
            return txt
            exit()
            #time.sleep(.2)

    def appendtext(self,title,newtext,comment):
        print("Editing " + title)
        jsonr = self.httpPOST("edit", [('title',  title.encode('utf-8')),
                                       ('appendtext', newtext.encode('utf-8')),
                                       ('summary', comment.encode('utf-8')),
                                       ('token', str(self.edittoken)),
                                       ('minor', 'true'),
                                       ('nocreate','true'),
                                       ('bot', 'true'),
                                       ('assert', 'bot')])

        if 'edit' in jsonr:
            if(jsonr['edit']['result'] == "Success"):
                print "Editing " + title.encode('utf-8','ignore') + "...Success"
        else:
            print "Editing " + title + "...Failure"
            print self.responsebuffer.getvalue()
            exit()

    def uploadignorewarnings(self,title,filekey,text,comment):
        jsonr = self.httpPOST("upload", [('filename',  title.encode('utf-8')),
                                         ('filekey',filekey.encode('utf-8')),
                                         ('comment', comment.encode('utf-8')),
                                         ('text',text.encode('utf-8')),
                                         ('token', str(self.edittoken)),
                                         ('ignorewarnings','1')])

    def upload(self,title,file,text,comment,overwritepageexists = False, uploadifduplicate = False):
        """
        For uploading files
        :param title: File title to upload to without the "File:" in u
        :param file: The name of the file on the harddrive in str, may include relative/full path
        :param text: Text of article in u
        :param comment: The comment in u
        :param overwritepageexists: Set to True to overwrite existing pages
        :param uploadifduplicate: Set to True to upload even if duplicate
        :return:
        """
        print "Uploading to " + title.encode('utf-8','ignore')
        time.sleep(self.Delay.UPLOAD)
        jsonr = self.httpPOST("upload", [('filename',  title.encode('utf-8')),
                                         ('file', (pycurl.FORM_FILE, str(file), pycurl.FORM_CONTENTTYPE, "application/octet-stream")),
                                         ('comment', comment.encode('utf-8')),
                                         ('text',text.encode('utf-8')),
                                         ('token', str(self.edittoken))])
        #('nassert','exists'), #only new

        if 'upload' in jsonr:
            if(jsonr['upload']['result'] == "Success"):
                print "Upload success"
            elif(jsonr['upload']['result'] == "Warning"):
                if 'duplicate' in jsonr['upload']['warnings']:
                    if not uploadifduplicate:
                        pass
                elif 'exists' in jsonr['upload']['warnings']:
                    if overwritepageexists:
                        self.uploadignorewarnings(title,jsonr['upload']['filekey'],text,comment)
        print self.responsebuffer.getvalue()

    #http://www.mediawiki.org/wiki/API:Upload
    def chunkupload(self,title,file,text,comment,
                    chunksize=5,chunkinmem=True, overwritepageexists = False,
                    uploadifduplicate = False):
        """
        
        :param title:  File title to upload to without the "File:" in u
        :param file: The name of the file on the harddrive in str, may include relative/full path
        :param text: Text of article in u
        :param comment: The comment in u
        :param chunksize: The chunk size to upload in MB
        :param chunkinmem: Whether to read full file to memory first, or read pieces off disc. True for full in mem
        :param overwritepageexists: Set to True to overwrite existing pages
        :param uploadifduplicate: Set to True to upload even if duplicate
        :return:
        """
        txt = ''
        txt = txt+ "Chunk uploading to " + title.encode('utf-8','ignore')
        filekey = self.stash(title,file,chunksize,chunkinmem)
        
        jsonr = self.httpPOST("upload", [('filename',  title.encode('utf-8')),
                                         ('filekey', str(filekey)),
                                         ('comment', comment.encode('utf-8')),
                                         ('text',text.encode('utf-8')),
                                         ('token', self.edittoken)])
        
        if 'upload' in jsonr:
            if(jsonr['upload']['result'] == "Success"):
                txt = txt+" "+ "Upload success"
            elif(jsonr['upload']['result'] == "Warning"):
                if 'duplicate' in jsonr['upload']['warnings']:
                    if not uploadifduplicate:
                        pass
                elif 'page-exists' in jsonr['upload']['warnings']:
                    if overwritepageexists:
                        self.uploadignorewarnings(title,jsonr['upload']['filekey'],text,comment)
        
        txt = txt+" "+ self.responsebuffer.getvalue()
        return txt

    def stash(self,title, filename,
              chunksize=5,chunkinmem=True):
        """

        :param title: The filename to stash it under in u
        :param filename:
        :param chunksize: The chunksize in MB
        :param chunkinmem: Whether to read all into mem at once, or off disk. True for all into mem
        :return:
        """
        print "Stashing to " + title.encode('utf-8','ignore')

        b=open(filename,'r+b')
        if chunkinmem:
            #Load whole file into memory
            map=mmap.mmap(fileno = b.fileno(), length=0, access=mmap.ACCESS_COPY)
            b.close()

        else:
            map=mmap.mmap(fileno = b.fileno(), length=0, access=mmap.ACCESS_READ)
            #Close later

        jsonr = self.httpPOST("upload", [('stash','1'),
                                         ('token', str(self.edittoken)),
                                         ('filename', title.encode('utf-8')),
                                         ('offset', str(map.tell())),
                                         ('filesize', str(map.size())),
                                         ('chunk"; filename="something', (pycurl.FORM_CONTENTTYPE, "application/octet-stream",
                                                                          pycurl.FORM_CONTENTS, map.read(chunksize * 1048576)))])
        if 'upload' in jsonr:
            uploadcounter=1
            try:
                while(jsonr['upload']['result'] == "Continue"):
                    jsonr = self.httpPOST("upload", [('stash','1'),
                                                     ('token', str(self.edittoken)),
                                                     ('filename', title.encode('utf-8')),
                                                     ('offset', str(map.tell())),
                                                     ('filesize', str(map.size())),
                                                     ('filekey', str(jsonr['upload']['filekey'])),
                                                     ('chunk"; filename="something', (pycurl.FORM_CONTENTTYPE, "application/octet-stream",
                                                                                      pycurl.FORM_CONTENTS, map.read(chunksize * 1048576)))])
                    #Bug 44923
                    if((uploadcounter == 1) and (map.tell() == map.size())):
                        if(jsonr['upload']['result'] == "Continue"):
                            jsonr['upload']['result'] = "Success"
                            break
                if(jsonr['upload']['result'] == "Success"):
                    print 'Successfully stashed at: ' + jsonr['upload']['filekey']
                    return jsonr['upload']['filekey']
                else:
                    print "Error"
            except KeyError:
                print jsonr
            print self.responsebuffer.getvalue()

        if not chunkinmem:
            b.close()

        print self.responsebuffer.getvalue()

    def apiaction(self, action):
        return self._apiurl + "?action=" + action + "&format=json"

    def logout(self):
        jsonr = self.httpPOST('logout',[('','')])

    @property
    def apiurl(self):
        return self._apiurl
