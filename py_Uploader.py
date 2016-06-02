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


def upFiles(in_path, cutoff=None, target=u'Uploaded',
            config_path=u'config.json', file_exts=None, test=False):
    """
    Upload all matched files in the supplied directory to Commons and
    moves any processed files to the target folder.
    :param in_path: path to directory with files to upload
    :param cutoff: number of files to upload (defaults to all)
    :param target: sub-directory for uploaded files (defaults to Uploaded)
    :param config_path: path to JSON config file (defaults to config.json)
    :param file_exts: tuple of allowed file extensions (defaults to FILEEXTS)
    :param test: set to True to test but not upload
    :return: None
    """
    # set defaults unless overridden
    file_exts = file_exts or FILEEXTS

    com_api = helpers.openConnection(config_path, apiClass=wikiApi.CommonsApi,
                                     verbose=True)

    # Verify inPath
    if not os.path.isdir(in_path):
        print u'The provided in_path was not a valid directory: %s' % in_path
        exit(1)

    # create target directories if they don't exist
    done_dir = os.path.join(in_path, target)
    error_dir = u'%s_errors' % done_dir
    warnings_dir = u'%s_warnings' % done_dir
    if not os.path.isdir(done_dir):
        os.mkdir(done_dir)
    if not os.path.isdir(error_dir):
        os.mkdir(error_dir)
    if not os.path.isdir(warnings_dir):
        os.mkdir(warnings_dir)

    # logfile
    logfile = os.path.join(in_path, u'¤uploader.log')
    flog = codecs.open(logfile, 'a', 'utf-8')

    # find all content files
    files = helpers.findFiles(path=in_path, fileExts=file_exts, subdir=False)

    counter = 1
    for f in files:
        if cutoff and counter > cutoff:
            break
        # verify that there is a matching info file
        info_file = u'%s.txt' % os.path.splitext(f)[0]
        base_name = os.path.basename(f)
        if not os.path.exists(info_file):
            flog.write(u'%s: Found tif/jpg without info' % base_name)
            continue

        # prepare upload
        fin = codecs.open(info_file, 'r', 'utf-8')
        txt = fin.read()
        fin.close()

        if test:
            print base_name
            print txt
            continue

        # stop here if testing
        result = com_api.chunkupload(base_name, f, txt, txt,
                                     uploadifbadprefix=True)

        # parse results and move files
        base_info_name = os.path.basename(info_file)
        details = ''
        jresult = json.loads(result[result.find('{'):])
        target_dir = None
        if 'error' in jresult.keys():
            details = json.dumps(jresult['error'], ensure_ascii=False)
            target_dir = error_dir
        elif 'upload' in jresult.keys() and \
                'warnings' in jresult['upload'].keys():
            details = json.dumps(jresult['upload'], ensure_ascii=False)
            target_dir = warnings_dir
        else:
            details = json.dumps(jresult['upload']['filename'],
                                 ensure_ascii=False)
            target_dir = done_dir
        os.rename(f, os.path.join(target_dir, base_name))
        os.rename(info_file, os.path.join(target_dir, base_info_name))

        # logging
        counter += 1
        result_text = result[:result.find('{')].strip().decode('utf8')
        flog.write(u'%s %s\n' % (result_text, details))
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
