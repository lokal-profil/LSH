#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# Cleanup library (moved out of upload)
# Also contains a functions for updating info pages
# TODO: make more like py_Uploader
#
import os
import helpers
import codecs


def updateInfoLocal(path, target=u'Updated', configPath=u'config.json',
                    comment=u'Updating information page due to improved '
                            u'algorithm for batch upload. See '
                            u'[[Commons:Batch_uploading/LSH]] for more info'):
    '''
    @todo: Make this and updateInfoOnline share writing parts (and use WikiApi)
           And consider shifting to postUpload/Cleanup
    Overwrites the information on the given filepages.
    Essentially upFiles without the filetransfer
    '''
    cwd = os.getcwd()
    os.chdir(path)
    comApi = helpers.openConnection(configPath)
    # redirect print to logfile for the sake of PyCJWiki
    flog = codecs.open(u'¤updater.log', 'a', 'utf-8')
    # sys.stdout = open(os.path.join(os.getcwd(),u'¤uploader.log'), 'w')

    # create targetdirectory if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)

    files = os.listdir(u'.')
    for f in files:
        if f.endswith((u'.tif', u'.jpg')):
            infoFile = u'%s.txt' % f[:-4]
            if not os.path.exists(infoFile):
                flog.write(u'%s: Found tif/jpg without info' % f)
                continue
            infoIn = codecs.open(infoFile, 'r', 'utf-8')
            info = infoIn.read()
            infoIn.close()
            result = comApi.editText(u'File:%s' % f,
                                     info,
                                     comment,
                                     minor=False,
                                     bot=True,
                                     userassert='bot',
                                     nocreate=True)
            flog.write(u'%s\n' % result.decode('utf8'))
            flog.flush()
            # Move files
            os.rename(f, os.path.join(target, f))
            os.rename(infoFile, os.path.join(target, infoFile))
    comApi.logout()
    os.chdir(cwd)  # so that same path structure can be used for next call
    flog.close()


def updateInfoOnline(path, target=u'Updated', configPath=u'config.json',
                     live=False,
                     comment=u'Updating information page due to improved '
                             u'algorithm for batch upload. See '
                             u'[[Commons:Batch_uploading/LSH]] for more info'):
    '''
    Rewrites the currently uploaded information, sends it to a modifier
    and uploads the new result
    '''
    cwd = os.getcwd()
    os.chdir(path)
    comApi = helpers.openConnection(configPath)
    # redirect print to logfile for the sake of PyCJWiki
    flog = codecs.open(u'¤updater.log', 'a', 'utf-8')

    # create targetdirectory if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)

    files = os.listdir(u'.')
    for f in files:
        if f.endswith((u'.tif', u'.jpg')):
            print u'Working on: %s...' % f
            infoFile = u'%s.txt' % f[:-4]
            # get current version
            pagename = u'File:%s' % f
            oldInfo = comApi.getPage(pagename)
            if pagename not in oldInfo.keys():
                pagename = pagename.replace('_', ' ')
                if pagename not in oldInfo.keys():
                    flog.write(u'%s: Did not find file on Commons\n' % f)
                    continue
            oldInfo = oldInfo[pagename]
            # create new info
            newInfo = changeInfo(f, oldInfo)
            if not newInfo:
                flog.write(u'%s: Could not change info\n' % f)
                continue
            elif newInfo.strip() == oldInfo.strip():
                flog.write(u'%s: No change needed\n' % f)
                continue
            # upload new info
            if live:
                result = comApi.editText(u'File:%s' % f,
                                         newInfo,
                                         comment,
                                         minor=False,
                                         bot=True,
                                         userassert='bot',
                                         nocreate=True)
                flog.write(u'%s\n' % result.decode('utf8'))
                flog.flush()
                # Move files
                os.rename(f, os.path.join(target, f))
                os.rename(infoFile, os.path.join(target, infoFile))
            else:
                flog.write(u'Update!: %s\n' % f)
    comApi.logout()
    os.chdir(cwd)  # so that same path structure can be used for next call
    flog.close()


def changeInfo(fileName, oldInfo):
    '''
    Takes filename and oldInfo and changes into the new info.
    This method is expected to change each time
    '''
    # return txt.strip()
    return False
