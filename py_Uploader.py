#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Uploader for all files in a folder files where description pages have
# already been created and files renamed to target filename on Commons.
#
import codecs
import os
import json
import WikiApi as wikiApi
import helpers
from helpers import output
FILEEXTS = (u'.tif', u'.jpg', u'.tiff', u'.jpeg')


def upFiles(inPath, cutoff=None, target=u'Uploaded', configPath=u'config.json',
            fileExts=None, test=False):
    """
    Upload all matched files in the supplied directory to Commons and
    moves any processed files to the target folder.
    :param inPath: path to directory with files to upload
    :param cutoff: number of files to upload (defaults to all)
    :param target: sub-directory for uploaded files (defaults to Uploaded)
    :param configPath: path to JSON config file (defaults to config.json)
    :param fileExts: tuple of allowed file extensions (defaults to FILEEXTS)
    :param test: set to True to test but not upload
    :return: None
    """
    # set defaults unless overridden
    fileExts = fileExts or FILEEXTS

    comApi = helpers.openConnection(configPath, apiClass=wikiApi.CommonsApi,
                                    verbose=True)

    # Verify inPath
    if not os.path.isdir(inPath):
        print u'The provided inPath was not a valid directory: %s' % inPath
        exit(1)

    # create target directories if they don't exist
    doneDir = os.path.join(inPath, target)
    errorDir = u'%s_errors' % doneDir
    warningsDir = u'%s_warnings' % doneDir
    if not os.path.isdir(doneDir):
        os.mkdir(doneDir)
    if not os.path.isdir(errorDir):
        os.mkdir(errorDir)
    if not os.path.isdir(warningsDir):
        os.mkdir(warningsDir)

    # logfile
    logfile = os.path.join(inPath, u'¤uploader.log')
    flog = codecs.open(logfile, 'a', 'utf-8')

    # find all content files
    files = helpers.findFiles(path=inPath, fileExts=fileExts, subdir=False)

    counter = 1
    for f in files:
        if cutoff and counter > cutoff:
            break
        # verify that there is a matching info file
        infoFile = u'%s.txt' % os.path.splitext(f)[0]
        baseName = os.path.basename(f)
        if not os.path.exists(infoFile):
            flog.write(u'%s: Found tif/jpg without info' % baseName)
            continue

        # prepare upload
        fin = codecs.open(infoFile, 'r', 'utf-8')
        txt = fin.read()
        fin.close()

        if test:
            print baseName
            print txt
            continue

        # stop here if testing
        result = comApi.chunkupload(baseName, f, txt, txt,
                                    uploadifbadprefix=True)

        # parse results and move files
        baseInfoName = os.path.basename(infoFile)
        details = ''
        jresult = json.loads(result[result.find('{'):])
        targetDir = None
        if 'error' in jresult.keys():
            details = json.dumps(jresult['error'], ensure_ascii=False)
            targetDir = errorDir
        elif 'upload' in jresult.keys() and \
                'warnings' in jresult['upload'].keys():
            details = json.dumps(jresult['upload'], ensure_ascii=False)
            targetDir = warningsDir
        else:
            details = json.dumps(jresult['upload']['filename'],
                                 ensure_ascii=False)
            targetDir = doneDir
        os.rename(f, os.path.join(targetDir, baseName))
        os.rename(infoFile, os.path.join(targetDir, baseInfoName))

        # logging
        counter += 1
        resultText = result[:result.find('{')].strip().decode('utf8')
        flog.write(u'%s %s\n' % (resultText, details))
        flog.flush()

    flog.close()
    output(u'Created %s' % logfile)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_Uploader.py path cutoff\n' \
            u'\tpath: the relative path to the directory containing ' \
            u'images and descriptions.\n' \
            u'\tcutoff is optional and allows the upload to stop after ' \
            u'the specified number of files'
    argv = sys.argv[1:]
    if len(argv) in (1, 2):
        path = helpers.convertFromCommandline(argv[0])
        if len(argv) == 2:
            cutoff = int(argv[1])
            upFiles(path, cutoff=cutoff)
        else:
            upFiles(path)
    else:
        print usage
# EoF
