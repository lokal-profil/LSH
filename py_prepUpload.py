#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Preparing files for upload and adding file extentions to filenames
# @toDo: Import improvements from batchUploadTools
#        Cleanup untouched functions (negatives() onwards)
#
import os
import codecs
import pipes
import helpers
from helpers import output
from py_MakeInfo import MakeInfo

# filename file
DATA_DIR = u'data'
CONNECTIONS_DIR = u'connections'
FILENAMES = os.path.join(DATA_DIR, u'filenames.csv')
FILEEXTS = (u'.tif', u'.jpg', u'.tiff', u'.jpeg')
NEGATIVE_PATTERN = u'-negative%s'


def moveFiles(target, tree, nameToPho, path=u'.', fileExts=None):
    """
    Move all files in the given dir and subdirs of the specified
    filetypes to the target dir.
    :param target: target directory to move files to
    :param tree: treestructure of expected filenames
    :param nameToPho: look-up dictionary for filenames to phoId
    :param path: path to directory in which to look for files and
                 subdirectories (defaults to ".")
    :param filetypes: tuple of allowed file extensions (defaults to FILEEXTS)
    :return: int, int (moved files, total files)
    """
    # set defaults unless overridden
    fileExts = fileExts or FILEEXTS

    baseDir, subdir = os.path.split(path)
    # create target if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)

    files = helpers.findFiles(path, fileExts)
    counter = 0
    for filename in files:
        filepath, plain_name = os.path.split(filename)
        fileKey, ext = os.path.splitext(plain_name)  # filename, .ext
        filepath = filepath.replace(baseDir, '').lstrip(u'./')
        if filepath in tree.keys() and fileKey in tree[filepath]:
            os.rename(filename, os.path.join(target, plain_name))
            counter += 1
            # record the actual file extention
            nameToPho[fileKey]['ext'] = ext[1:]
    return (counter, len(files))


def makeHitlist(filenamesFile=None):
    """
    Goes through the allowed filenames and builds up a treestructure
    {directory: [filenames]} as well as a look-up dictionary for filenames
    to phoId {MulDateiS: {phoMull, filename, ext}}
    :param filenamesFile: filenames data file
    :return: dict, dict
    """
    # set defaults unless overridden
    filenamesFile = filenamesFile or FILENAMES

    # load filenames file
    filenamesHeader = 'PhoId|MulId|MulPfadS|MulDateiS|filename|ext'
    filenames = helpers.csvFileToDict(filenamesFile, 'PhoId', filenamesHeader)

    tree = {}
    nameToPho = {}
    for phoId, v in filenames.iteritems():
        oldName = v['MulDateiS']
        path = v['MulPfadS'].replace('\\', os.sep)  # windows -> current os
        if path not in tree.keys():
            tree[path] = []
        tree[path].append(oldName)
        nameToPho[oldName] = {'phoMull': u'%s:%s' % (phoId, v['MulId']),
                              'filename': v['filename'],
                              'ext': v['ext']}
    return (tree, nameToPho)


def moveHits(path, filenamesFile=None):
    """
    Goes through the root export directory to find any matching file and
    moves these to a lower case version of the directory. This flattens
    out the directory structure whilst making it easy to identify any
    non-matched files.
    :param path: path to directory with image file structures
    :param filenamesFile: filenames data file
    :return: None
    """
    # set defaults unless overridden
    filenamesFile = filenamesFile or FILENAMES

    # Find and move all relevant files
    tree, name_to_pho = makeHitlist(filenamesFile)
    subdirs = []
    for filename in os.listdir(path):
        # for LSH all files are in upper case directories
        filename_path = os.path.join(path, filename)
        if os.path.isdir(filename_path) and filename.isupper():
            subdirs.append(filename_path)
    for subdir in subdirs:
        # make a subdir path where (only the) last directory is lower case
        tmp_path, tmp_dir = os.path.split(subdir)
        lower_subdir = os.path.join(tmp_path, tmp_dir.lower())

        counter, file_num = moveFiles(lower_subdir, tree, name_to_pho,
                                      path=subdir)
        output(u'%s: %d out of %d were hits' % (subdir, counter, file_num))

    # load filenames file
    filenames_header = 'PhoId|MulId|MulPfadS|MulDateiS|filename|ext'
    old_filenames = helpers.csvFileToDict(filenamesFile, 'PhoId',
                                          filenames_header)

    # Add found extentions to filenames file
    for phoId, v in old_filenames.iteritems():
        old_filename = v['MulDateiS']
        if old_filename in name_to_pho.keys():
            v['ext'] = name_to_pho[old_filename]['ext']  # overwrite extention

    # output updated file
    helpers.dictToCsvFile(filenamesFile, old_filenames, filenames_header)

    # delete all emptied directories
    for subdir in subdirs:
        removeEmptyDirectories(subdir, top=False)


def makeAndRename(path, dataDir=None, connectionsDir=None,
                  filenameFile=None, batchCat=None):
    """
    Create info file and rename image file
    :param path: relative path to the directory in which to process files
    :param batchCat: If given a category of the format
                     Category:Media contributed by LSH: batchCat will be added
                     to all files.
    :return: None
    """
    # set defaults unless overridden
    dataDir = dataDir or DATA_DIR
    connectionsDir = connectionsDir or CONNECTIONS_DIR
    filenameFile = filenameFile or FILENAMES

    # logfile
    logfile = os.path.join(path, u'¤generator.log')
    flog = codecs.open(logfile, 'a', 'utf-8')

    # require batchCat to be of some length
    if batchCat is not None:
        batchCat = batchCat.strip()
        if not batchCat:
            batchCat = None
        else:
            batchCat = u'[[Category:Media contributed by LSH: %s]]' % batchCat

    tree, nameToPho = makeHitlist(filenameFile)

    # get category statistics
    catTest(path, dataDir, connectionsDir, filenameFile)

    # initialise maker
    maker = MakeInfo()
    maker.readInLibraries(folder=dataDir)
    maker.readConnections(folder=connectionsDir)

    for filenameIn in os.listdir(path):
        baseName = os.path.splitext(filenameIn)[0]

        if filenameIn.startswith(u'¤'):  # log files
            continue
        elif baseName not in nameToPho.keys():
            flog.write(u'%s did not have a photoId\n' % filenameIn)
            continue
        phoMull = nameToPho[baseName]['phoMull']
        filenameOut = u'%s.%s' % (
            nameToPho[baseName]['filename'].replace(u' ', u'_'),
            nameToPho[baseName]['ext'])
        wName, out = maker.infoFromPhoto(phoMull, preview=False, testing=False)

        # output
        if out:
            if batchCat:
                out += batchCat

            # Make info file
            info_file = u'%s.txt' % os.path.splitext(filenameOut)[0]
            helpers.open_and_write_file(os.path.join(path, info_file), out)

            # Move image file
            os.rename(os.path.join(path, filenameIn),
                      os.path.join(path, filenameOut))
            flog.write(u'%s outputed to %s\n' % (filenameIn, filenameOut))
        else:
            flog.write(u'%s failed to make infopage. See log\n' % filenameIn)


def negatives(path, ext=u'.tif'):
    """
    Identify and invert all files at the given location.

    * moves file to filename-NEGATIVE_PATTERN.ext
    * creates an inverted file at filename.ext
    * creates a info file for negative and modifes info file for positive
    :param path: realtive path to the directory in which to process the files
    :param ext: image file extension (only .tif are ever negatives?)
    """
    negative_appendix = NEGATIVE_PATTERN % ext
    count = 0
    skipcount = 0
    for filename in os.listdir(path):
        if filename.endswith(ext) and \
                not filename.endswith(negative_appendix):
            negative = u'%s%s' % (filename[:-len(ext)], negative_appendix)
            if os.path.isfile(os.path.join(path, negative)):
                output(u'%s was already inverted, skipping...' % filename)
                skipcount += 1
                continue
            invert_file_and_info(path, filename, negative, ext)
            count += 1
            if count % 10 == 0:
                output(u'%d files inverted (%d)' % (count, count + skipcount))


def invert_file_and_info(path, filename, negative, ext):
    """
    Given a negative file and an output filename, invert files and update info.

    * Moves the original file to the negative filename
    * Inverts the (new) negative file and stores as original filename
    * Updates the original file description and creates one for the negative.
    :param path: realtive path to the directory in which to process the files
    :param filename: the original (negative) file
    :param negative: the target name for the negative
    :param ext: the file extension
    """
    # move original
    os.rename(os.path.join(path, filename),
              os.path.join(path, negative))

    # invert using imageMagick with errors piped to file
    image_magick = u'convert %s -negate -auto-gamma -level 10%%,90%%,1,0 %s 2>>%s' % (
        pipes.quote(os.path.join(path, negative)),
        pipes.quote(os.path.join(path, filename)),
        pipes.quote(os.path.join(path, u'¤imageMagick-errors.log')))
    os.system(image_magick.encode(encoding='UTF-8'))

    # make new info files
    info_filename_pos = os.path.join(path, u'%s.txt' % filename[:-len(ext)])
    info_filename_neg = os.path.join(path, u'%s.txt' % negative[:-len(ext)])
    info_file = helpers.open_and_read_file(info_filename_pos)
    neg_info, pos_info = make_neg_and_pos_info(
        info_file, filename.replace(u'_', u' '), ext)
    helpers.open_and_write_file(info_filename_neg, neg_info)
    helpers.open_and_write_file(info_filename_pos, pos_info)


def make_neg_and_pos_info(info_file, filename, ext):
    """
    Generate a negative and positive version of the given info file.

    The two refer to each other using the negative/positive parameters. The
    negative file gets categories removed.
    :param info_file: the contents of the info file
    :param filename: the (positive) image filename
    :param ext: the file extension
    """
    negative_appendix = NEGATIVE_PATTERN % ext
    ov_position = info_file.find(u'|other_versions=')

    # for negative we need to identify end position of the template
    end_position = -1
    end_patterns = [u'</gallery>\n}}', u'|other_versions= \n}}']
    for end_pattern in end_patterns:
        end_position = info_file.find(end_pattern)
        if end_position > 0:
            end_position += len(end_pattern)
            break
    if not end_position > 0:
        # if all else fails just keep it all
        output('%s: could not find end of template' % filename)
        end_position = len(info_file)

    # make new infos
    pos_info = u'%s|negative= %s\n%s' % (
        info_file[:ov_position],
        u'%s%s' % (filename[:-len(ext)], negative_appendix),
        info_file[ov_position:])
    neg_info = u'%s|positive= %s\n%s' % (
        info_file[:ov_position],
        filename,
        info_file[ov_position:end_position])
    return (neg_info, pos_info)


def catTest(path, data_dir, connections_dir, filename_file, nameToPho=None):
    '''
    check the category statistics for the files in a given directory
    '''
    if not nameToPho:
        tree, nameToPho = makeHitlist(filename_file)
    # logfile
    flog = codecs.open(os.path.join(path, u'¤catStats.log'), 'w', 'utf-8')
    maker = MakeInfo()
    phoMull_list = []
    for filename_in in os.listdir(path):
        if not filename_in[:-4] in nameToPho.keys():
            continue
        phoMull_list.append(nameToPho[filename_in[:-4]]['phoMull'])
    maker.catTestBatch(phoMull_list, data_dir, connections_dir,
                       outputPath=path, log=flog)
    flog.close()


def negative_cleanup(path, ext=u'.tif'):
    '''
    Run after negatives to identify any failed conversions.
    '''
    negative_appendix = NEGATIVE_PATTERN % ext
    info = {
        'no_invert': [],
        'no_invert_info': [],
        'no_original': [],
        'no_original_info': [],
        'just_info': []
    }
    for filename in os.listdir(path):
        if filename.endswith(negative_appendix):
            positive = filename[:-len(negative_appendix)]
            negative = filename[:-len(ext)]
            check_related_file_existence(path, positive, negative, ext, info)
        elif filename.endswith(ext):
            positive = filename[:-len(ext)]
            negative = u'%s%s' % (filename[:-len(ext)],
                                  negative_appendix[:-len(ext)])
            check_related_file_existence(path, positive, negative, ext, info)
        elif filename.endswith(u'.txt'):
            # check that either -negative.tif or .tif exists
            # (if so then dealt with by above)
            negative_info_appendix = NEGATIVE_PATTERN % '.txt'
            if filename.endswith(negative_info_appendix):
                positive = u'%s%s' % (filename[:-len(negative_info_appendix)],
                                      ext)
                negative = u'%s%s' % (filename[:-len(u'.txt')], ext)
            else:
                positive = u'%s%s' % (filename[:-len(u'.txt')], ext)
                negative = u'%s%s' % (filename[:-len(u'.txt')],
                                      negative_appendix)
            if not os.path.isfile(os.path.join(path, negative)) and \
                    not os.path.isfile(os.path.join(path, positive)):
                info['just_info'].append(filename)

    # sort and remove any dupes
    for k, v in info.iteritems():
        info[k] = sorted(set(v))

    # output to log
    log_filename = u'¤conversion-errors.log'
    txt = u'Total: %d, problems %d\n' % (
        len(os.listdir(path)),
        len(info['no_invert']) + len(info['no_original']))
    for k, v in info.iteritems():
        txt += u'\n== %s: %d ==\n' % (k, len(v))
        txt += u'%s\n' % '\n'.join(v)
    helpers.open_and_write_file(os.path.join(path, log_filename), txt)


def check_related_file_existence(path, positive, negative, ext, info):
    """
    Given a pattern for positive and negative check that related files exist.

    :param path: realtive path to the directory in which to process the files
    :param positive: full path to positive, without file extension
    :param negative: full path to negative, without file extension
    :param ext: image file extension
    :param info: dict to hold found statistics
    """
    if not os.path.isfile(os.path.join(path, u'%s%s' % (positive, ext))):
        # check if .ext exists
        info['no_original'].append(u'%s%s' % (positive, ext))
    if not os.path.isfile(os.path.join(path, u'%s%s' % (negative, ext))):
        # check if -NEGATIVE_PATTERN.ext exists
        info['no_invert'].append(u'%s%s' % (negative, ext))
    if not os.path.isfile(os.path.join(path, u'%s.txt' % positive)):
        # check if .txt exists
        info['no_original_info'](u'%s.txt' % positive)
    if not os.path.isfile(os.path.join(path, u'%s.txt' % negative)):
        # check if NEGATIVE_PATTERN.txt exists
        info['no_invert_info'].append(u'%s.txt' % negative)


def removeEmptyDirectories(path, top=True):
    """
    Remove any empty directories and subdirectories
    :param path: path to direcotry to start deleting from
    :param top: set to True to not delete the current directory
    :return: None
    """
    if not os.path.isdir(path):
        return

    # remove empty sub-directory
    files = os.listdir(path)
    for f in files:
        fullpath = os.path.join(path, f)
        if os.path.isdir(fullpath):
            removeEmptyDirectories(fullpath, top=False)

    # re-read and delete directory if empty,
    files = os.listdir(path)
    if not top:
        if not files:
            os.rmdir(path)
        else:
            output('Not removing non-empty directory: %s' % path)


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_prepUpload.py action path\n' \
            u'\taction: moveHits - moves the relevant files to base ' \
            u'directories and adds extention to filenames\n' \
            u'\t\tpath: relative pathname to main directory for images\n' \
            u'\taction: makeAndRename - make info files and rename\n' \
            u'\t\tpath: relative pathname to a directory containing images\n' \
            u'\taction: negatives - create positives for the relevant directories\n' \
            u'\t\tpath: relative pathname to a directory containing images\n' \
            u'\taction: negativeCleanup - spot any conversion problems from negatives\n' \
            u'\t\tpath: relative pathname to a directory containing images\n' \
            u'\tExamples:\n' \
            u'\tmoveHits ../diskkopia\n' \
            u'\tmakeAndRename ../diskkopia/m_dig\n' \
            u'\tnegatives ../diskkopia/m_b\n' \
            u'\tnegativeCleanup ../diskkopia/m_b'
    argv = sys.argv[1:]
    if len(argv) == 2:
        path = helpers.convertFromCommandline(argv[1])
        if not os.path.isdir(path):
            print u'The provided path was not a valid directory: %s' % path
            exit(1)
        if argv[0] == 'moveHits':
            moveHits(path=path)
        elif argv[0] == 'makeAndRename':
            makeAndRename(path=path)
        elif argv[0] == 'negatives':
            negatives(path=path)
        elif argv[0] == 'negativeCleanup':
            negative_cleanup(path=path)
        else:
            print usage
    elif len(argv) == 3:
        path = helpers.convertFromCommandline(argv[1])
        batchCat = helpers.convertFromCommandline(argv[2])
        if argv[0] == 'makeAndRename':
            makeAndRename(path=path, batchCat=batchCat)
        else:
            print usage
    else:
        print usage
# EoF
