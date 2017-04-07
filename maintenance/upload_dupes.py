#!/usr/bin/python
# -*- coding: UTF-8  -*-
"""Script to upload replacement versions of existing files."""
import batchupload.csv_methods as csv
import batchupload.common as common
import batchupload.prepUpload as prep
import batchupload.uploader as uploader
import os
import pywikibot
import codecs


def rename(base_dir, sub_cat, in_filename, log_file='move.log'):
    """
    Identify any files to replace and rename them to their commons names.

    :param base_dir: Path to directory in which replacement image files are
        found.
    :param sub_cat: The name of the subdirectory into which processed files
        should be moved.
    :param in_filename: The photoAll.csv file filtered to only contain the
        files to replace.
    :param log_file: The name of the log file to be created (in base_dir).
    """
    # Load indata
    in_filename = common.modify_path(base_dir, in_filename)
    header_check = u'PhoId|PhoObjId|PhoBeschreibungM|PhoAufnahmeortS|' \
                   u'PhoSwdS|MulId|filnamn|AdrVorNameS|AdrNameS|PhoSystematikS'
    data = csv.csv_file_to_dict(in_filename, "filnamn", header_check,
                                keep=('PhoSystematikS', 'filnamn'),
                                delimiter='|', codec='utf-16')

    # reformat the commons filenames
    url_prefix = u'https://commons.wikimedia.org/wiki/File:'
    for k, v in data.iteritems():
        if v['PhoSystematikS'].startswith(url_prefix):
            data[k] = v['PhoSystematikS'][len(url_prefix):]
        else:
            pywikibot.output("error in indatafile: %s, %s" % (k, v))

    # find candidate files
    candidates = prep.find_files(base_dir, ('.tif', ), subdir=False)

    # rename the files
    sub_cat = common.modify_path(base_dir, sub_cat)
    log_file = common.modify_path(base_dir, log_file)
    common.create_dir(sub_cat)
    log = []

    for candidate in candidates:
        base_name = os.path.basename(candidate)
        if base_name not in data.keys():
            log.append('%s not found in csv file' % base_name)
            continue

        commons_name = data.pop(base_name)
        commons_name = common.modify_path(sub_cat, commons_name)
        os.rename(candidate, commons_name)

    for k in data.keys():
        log.append('%s not found on disk' % k)

    common.open_and_write_file(log_file, '\n'.join(log), codec='utf-8')
    pywikibot.output(u'Created %s' % log_file)


def upload_all(base_dir, sub_dir=u'Uploaded', log_file='upload.log',
               verbose=True):
    """
    Upload the renamed files.

    We cannot just use uploader.up_all since  there are no corresponding .info
    files.
    """
    commons = pywikibot.Site('commons', 'commons')
    commons.login()

    upload_comment = u'Source image improved by the institution #LSH'

    # create target directories if they don't exist
    done_dir = common.modify_path(base_dir, sub_dir)
    error_dir = u'%s_errors' % done_dir
    warnings_dir = u'%s_warnings' % done_dir
    common.create_dir(done_dir)
    common.create_dir(error_dir)
    common.create_dir(warnings_dir)

    # logfile
    logfile = common.modify_path(base_dir, log_file)
    flog = codecs.open(logfile, 'a', 'utf-8')

    # find candidate files
    media_files = prep.find_files(base_dir, ('.tif', ), subdir=False)
    for media_file in media_files:
        file_name = os.path.basename(media_file)
        target_dir = None
        result = uploader.upload_single_file(
            file_name, media_file, upload_comment, commons,
            overwrite_page_exists=True)

        if result.get('error'):
            target_dir = error_dir
        elif result.get('warning'):
            target_dir = warnings_dir
        else:
            target_dir = done_dir
        if verbose:
            pywikibot.output(result.get('log'))

        flog.write(u'%s\n' % result.get('log'))
        os.rename(media_file, common.modify_path(target_dir, file_name))
        flog.flush()

    flog.close()
    pywikibot.output(u'Created %s' % logfile)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython upload_dupes.py -path:<path> -infile:<path>\n' \
            u'\tpath: the relative path to the directory containing ' \
            u'images and descriptions (optional).\n' \
            u'\tinfile: the relative path to the filtered photoAll csv file ' \
            u'containing metadata for the replacement images.'
    argv = sys.argv[1:]
    if len(argv) >= 1 and argv[0] in ('rename', 'upload'):
        # hard coded paths
        base_dir = '/media/andre/Leverans_wiki_4/2016_02/Replace_images/'
        rename_sub_dir = 'renamed'
        override_path = None
        infile = None

        # let pywikibot intercept any other args
        for arg in pywikibot.handle_args(argv[1:]):
            option, sep, value = arg.partition(':')
            if option == '-path':
                override_path = value
            if option == '-infile':
                infile = value

        if not infile:
            print usage
        elif argv[0] == 'rename':
            path = override_path or base_dir
            rename(path, rename_sub_dir, infile)
        elif argv[0] == 'upload':
            path = override_path or \
                common.modify_path(base_dir, rename_sub_dir)
            upload_all(path)
    else:
        print usage
