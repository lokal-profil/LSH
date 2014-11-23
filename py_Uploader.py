#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Uploading files
#
'''
Uploader for all files in a folder files where discription pages have
already ben created and files renamed to target filename on commons.

Also contains a functions for updating info pages

TODO: Change over from PyCJWiki to WikiApi
'''
import codecs
import os
import json
from PyCJWiki import Wiki
import config as config


def setUp(password, user):
    # Provide url and identify (either talk-page url or email)
    commons = Wiki("https://commons.wikimedia.org/w/api.php",
                   "https://commons.wikimedia.org/wiki/User_talk:%s" % user)

    # Login
    commons.login(user, password)
    # Get an edittoken
    commons.setEditToken()
    return commons


def upFiles(path, password=config.password, user=config.username,
            target=u'Uploaded'):
    '''
    Uploads files to Commons. Moves any processed files to the target folder
    '''
    cwd = os.getcwd()
    os.chdir(path)
    commons = setUp(password, user)
    # redirect print to logfile for the sake of PyCJWiki
    flog = codecs.open(u'¤uploader.log', 'a', 'utf-8')
    # sys.stdout = open(os.path.join(os.getcwd(),u'¤uploader.log'), 'w')

    # create target directories if they don't exist
    if not os.path.isdir(target):
        os.mkdir(target)
    if not os.path.isdir(u'%s_errors' % target):
        os.mkdir(u'%s_errors' % target)
    if not os.path.isdir(u'%s_warnings' % target):
        os.mkdir(u'%s_warnings' % target)
    
    files = os.listdir(u'.')
    for f in files:
        if f.endswith(u'.tif') or f.endswith(u'.jpg'):
            infoFile = u'%s.txt' % f[:-4]
            if not os.path.exists(infoFile):
                flog.write(u'%s: Found tif/jpg without info' % f)
                continue
            infoIn = codecs.open(infoFile, 'r', 'utf-8')
            info = infoIn.read()
            infoIn.close()
            result = commons.chunkupload(f, f, info, info)
            flog.write(u'%s\n' % result.decode('utf8'))
            flog.flush()
            # parse results and move files
            jresult = json.loads(result[result.find('{'):])
            if 'error' in jresult.keys():
                os.rename(f, os.path.join(u'%s_errors' % target, f))
                os.rename(infoFile, os.path.join(u'%s_errors' % target, infoFile))
            elif 'upload' in jresult.keys() and 'Warning' in jresult['upload'].keys():
                os.rename(f, os.path.join(u'%s_warnings' % target, f))
                os.rename(infoFile, os.path.join(u'%s_warnings' % target, infoFile))
            else:
                os.rename(f, os.path.join(target, f))
                os.rename(infoFile, os.path.join(target, infoFile))
    commons.logout()
    os.chdir(cwd)  # so that same path structure can be used for next call
    flog.close()


def updateInfoLocal(path, password=config.password, user=config.username,
                    target=u'Updated',
                    comment=u'Updating information page due to improved '
                        u'algorithm for batch upload. See '
                        u'[[Commons:Batch_uploading/LSH]] for more info'):
    '''
    Overwrites the information on the given filepages.
    Essentially upFiles without the filetransfer
    '''
    cwd = os.getcwd()
    os.chdir(path)
    commons = setUp(password, user)
    # redirect print to logfile for the sake of PyCJWiki
    flog = codecs.open(u'¤updater.log', 'a', 'utf-8')
    # sys.stdout = open(os.path.join(os.getcwd(),u'¤uploader.log'), 'w')

    # create targetdirectory if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)

    files = os.listdir(u'.')
    for f in files:
        if f.endswith(u'.tif'):
            infoFile = u'%s.txt' % f[:-4]
            if not os.path.exists(infoFile):
                flog.write(u'%s: Found tif without info' % f)
                continue
            infoIn = codecs.open(infoFile, 'r', 'utf-8')
            info = infoIn.read()
            infoIn.close()
            result = commons.editText(u'File:%s' % f,
                                      info,
                                      comment,
                                      minor=False,
                                      bot=True,
                                      userassert='exists',
                                      nocreate=True)
            flog.write(u'%s\n' % result.decode('utf8'))
            flog.flush()
            # Move files
            os.rename(f, os.path.join(target, f))
            os.rename(infoFile, os.path.join(target, infoFile))
    commons.logout()
    os.chdir(cwd)  # so that same path structure can be used for next call
    flog.close()


def updateInfoOnline(path, password=config.password, user=config.username,
                     target=u'Updated', live=False,
                     comment=u'Updating information page due to improved '
                        u'algorithm for batch upload. See '
                        u'[[Commons:Batch_uploading/LSH]] for more info'):
    '''
    Rewrites the currently uploaded information, sends it to a modifier
    and uploads the new result
    '''
    cwd = os.getcwd()
    os.chdir(path)
    commons = setUp(password, user)
    # redirect print to logfile for the sake of PyCJWiki
    flog = codecs.open(u'¤updater.log', 'a', 'utf-8')

    # create targetdirectory if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)

    files = os.listdir(u'.')
    for f in files:
        if f.endswith(u'.tif'):
            print u'Working on: %s...' % f
            infoFile = u'%s.txt' % f[:-4]
            # get current version
            oldInfo = commons.getText(u'File:%s' % f)
            if not oldInfo:
                flog.write(u'%s: Did not find file on Commons\n' % f)
                continue
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
                result = commons.editText(u'File:%s' % f,
                                          newInfo,
                                          comment,
                                          minor=False,
                                          bot=True,
                                          userassert='exists',
                                          nocreate=True)
                flog.write(u'%s\n' % result.decode('utf8'))
                flog.flush()
                # Move files
                os.rename(f, os.path.join(target, f))
                os.rename(infoFile, os.path.join(target, infoFile))
            else:
                flog.write(u'Update!: %s\n' % f)
    commons.logout()
    os.chdir(cwd)  # so that same path structure can be used for next call
    flog.close()


def changeInfo(fileName, oldInfo):
    '''
    Takes filename and oldInfo and changes into the new info.
    This method is expected to change each time
    '''
    # return txt.strip()
    return False


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_Uploader.py path\n' \
        u'\tpath: the relative pathname to the directory containing ' \
        u'images and descriptions.\n'
    argv = sys.argv[1:]
    if len(argv) == 1:
        path = argv[0].decode(sys.getfilesystemencoding())  # str to unicode
        if not os.path.isdir(path):
            print u'The provided path was not a valid directory: %s' % path
            exit()
        upFiles(path)
    else:
        print usage
# EoF
