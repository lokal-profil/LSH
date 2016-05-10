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


def moveFiles(target, tree, nameToPho, path=u'.', fileExts=FILEEXTS):
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


def makeHitlist(filenamesFile=FILENAMES):
    """
    Goes through the allowed filenames and builds up a treestructure
    {directory: [filenames]} as well as a look-up dictionary for filenames
    to phoId {MulDateiS: {phoMull, filename, ext}}
    :param filenamesFile: filenames data file
    :return: dict, dict
    """
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


def moveHits(path, filenamesFile=FILENAMES):
    """
    Goes through the root export directory to find any matching file and
    moves these to a lower case version of the directory. This flattens
    out the directory structure whilst making it easy to identify any
    non-matched files.
    :param path: path to directory with image file structures
    :param filenamesFile: filenames data file
    :return: None
    """
    # Find and move all relevant files
    tree, nameToPho = makeHitlist(filenamesFile)
    subdirs = []
    for filename in os.listdir(path):
        # for LSH all files are in upper case directories
        filenamePath = os.path.join(path, filename)
        if os.path.isdir(filenamePath) and filename.isupper():
            subdirs.append(filenamePath)
    for subdir in subdirs:
        counter, fileNum = moveFiles(subdir.lower(), tree, nameToPho,
                                     path=subdir)
        output(u'%s: %d out of %d were hits' % (subdir, counter, fileNum))

    # load filenames file
    filenamesHeader = 'PhoId|MulId|MulPfadS|MulDateiS|filename|ext'
    oldFilenames = helpers.csvFileToDict(filenamesFile, 'PhoId',
                                         filenamesHeader)

    # Add found extentions to filenames file
    for phoId, v in oldFilenames.iteritems():
        oldFilename = v['MulDateiS']
        if oldFilename in nameToPho.keys():
            v['ext'] = nameToPho[oldFilename]['ext']  # overwrite extention

    # output updated file
    helpers.dictToCsvFile(filenamesFile, oldFilenames, filenamesHeader)

    # delete all emptied directories
    for subdir in subdirs:
        removeEmptyDirectories(subdir, top=False)


def makeAndRename(path, dataDir=DATA_DIR, connectionsDir=CONNECTIONS_DIR,
                  filenameFile=FILENAMES, batchCat=None):
    """
    Create info file and rename image file
    :param path: relative path to the directory in which to process files
    :param batchCat: If given a category of the format
                     Category:Media contributed by LSH: batchCat will be added
                     to all files.
    :return: None
    """
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
        filenameOut = u'%s.%s' % (nameToPho[baseName]['filename'].replace(u' ', u'_'),
                                  nameToPho[baseName]['ext'])
        wName, out = maker.infoFromPhoto(phoMull, preview=False, testing=False)
        if out:
            # Make info file
            infoFile = u'%s.txt' % os.path.splitext(filenameOut)[0]
            f = codecs.open(os.path.join(path, infoFile), 'w', 'utf-8')
            if batchCat:
                out += batchCat
            f.write(out)
            f.close()
            # Move image file
            os.rename(os.path.join(path, filenameIn),
                      os.path.join(path, filenameOut))
            flog.write(u'%s outputed to %s\n' % (filenameIn, filenameOut))
        else:
            flog.write(u'%s failed to make infopage. See log\n' % filenameIn)


def negatives(path):
    '''
    moves file to filename-negative.tif
    creates an inverted file at filename.tif
    creates a info file for negative and modifes info file for positive
    path is the realtive path to the directory in which to process the files
    only .tif are ever negatives
    '''
    count = 0
    skipcount = 0
    for filename in os.listdir(path):
        if filename.endswith(u'.tif') and not filename.endswith(u'-negative.tif'):
            negative = u'%s-negative.tif' % filename[:-4]
            if os.path.isfile(os.path.join(path, negative)):
                output(u'%s was already inverted, skipping...' % filename)
                skipcount += 1
                continue
            os.rename(os.path.join(path, filename), os.path.join(path, negative))
            imageMagick = u'convert %s -negate -auto-gamma -level 10%%,90%%,1,0 %s' % (pipes.quote(os.path.join(path, negative)), pipes.quote(os.path.join(path, filename)))
            imageMagick = u'%s 2>>%s' % (imageMagick, pipes.quote(os.path.join(path, u'¤imageMagick-errors.log')))  # pipe errors to file
            os.system(imageMagick.encode(encoding='UTF-8'))
            # new info files
            infoFilename = u'%s.txt' % filename[:-4]
            f = codecs.open(os.path.join(path, infoFilename), 'r', 'utf-8')
            infoFile = f.read()
            f.close()
            negInfo, posInfo = negPosInfo(infoFile, filename.replace(u'_', u' '))
            f = codecs.open(os.path.join(path, u'%s-negative.txt' % infoFilename[:-4]), 'w', 'utf-8')
            f.write(negInfo)
            f.close()
            f = codecs.open(os.path.join(path, infoFilename), 'w', 'utf-8')
            f.write(posInfo)
            f.close()
            count += 1
            if count % 10 == 0:
                output(u'%d files inverted (%d)' % (count, count + skipcount))


def negPosInfo(infoFile, filename):
    '''
    generate a negative and positive version of the given info file
    '''
    ovPos = infoFile.find(u'|other_versions=')
    # for negative we want to remove cats (i.e. anything after </gallery>\n}} )
    # so need to identify end position
    end = infoFile.find(u'</gallery>\n}}')
    if end > 0:
        end += len(u'</gallery>\n}}')
    else:
        end = infoFile.find(u'|other_versions= \n}}')
        if end > 0:
            end += len(u'|other_versions= \n}}')
        else:
            print '%s: could not find end of template' % filename
            end = ''
    pos = u'%s|negative= %s\n%s' % (infoFile[:ovPos],
                                    u'%s-negative.%s' % (filename[:-4], filename[-3:]),
                                    infoFile[ovPos:])
    neg = u'%s|positive= %s\n%s' % (infoFile[:ovPos],
                                    filename,
                                    infoFile[ovPos:end])
    return (neg, pos)


def catTest(path, data_dir, connections_dir, filename_file, nameToPho=None):
    '''
    check the category statistics for the files in a given directory
    '''
    if not nameToPho:
        tree, nameToPho = makeHitlist(filename_file)
    flog = codecs.open(os.path.join(path, u'¤catStats.log'), 'w', 'utf-8')  # logfile
    maker = MakeInfo()
    phoMull_list = []
    for filename_in in os.listdir(path):
        if not filename_in[:-4] in nameToPho.keys():
            continue
        phoMull_list.append(nameToPho[filename_in[:-4]]['phoMull'])
    maker.catTestBatch(phoMull_list, data_dir, connections_dir,
                       outputPath=path, log=flog)
    flog.close()


def negativeCleanup(path):
    '''
    Run after negatives to identify any failed conversions.
    '''
    no_invert = []
    no_invert_info = []
    no_original = []
    no_original_info = []
    just_info = []
    for filename in os.listdir(path):
        if filename.endswith(u'-negative.tif'):
            positive = filename[:-len(u'-negative.tif')]
            negative = filename[:-len('.tif')]
            if not os.path.isfile(os.path.join(path, u'%s.tif' % positive)):  # check if .tif exists
                no_original.append(u'%s.tif' % positive)
            if not os.path.isfile(os.path.join(path, u'%s.txt' % positive)):  # check if .txt exists
                no_original_info(u'%s.txt' % positive)
            if not os.path.isfile(os.path.join(path, u'%s.tif' % negative)):  # check if -negative.txt exists
                no_invert_info.append(u'%s.txt' % negative)
        elif filename.endswith(u'.tif'):
            positive = filename[:-len(u'.tif')]
            negative = u'%s-negative' % filename[:-len('.tif')]
            if not os.path.isfile(os.path.join(path, u'%s.tif' % negative)):  # check if -negative.tif exists
                no_invert.append(u'%s.tif' % negative)
            if not os.path.isfile(os.path.join(path, u'%s.txt' % positive)):  # check if .txt exists
                no_original_info(u'%s.txt' % positive)
            if not os.path.isfile(os.path.join(path, u'%s.tif' % negative)):  # check if -negative.txt exists
                no_invert_info.append(u'%s.txt' % negative)
        elif filename.endswith(u'.txt'):
            # check that either -negative.tif or .tif exists
            # (if so then dealt with by above)
            if filename.endswith(u'-negative.txt'):
                positive = filename[:-len(u'-negative.txt')]
                negative = filename[:-len(u'.txt')]
            else:
                positive = filename[:-len(u'.txt')]
                negative = u'%s-negative' % filename[:-len(u'.txt')]
            if not os.path.isfile(os.path.join(path, u'%s.tif' % negative)) and not os.path.isfile(os.path.join(path, u'%s.tif' % positive)):
                just_info.append(filename)
    # sort and remove any dupes
    no_invert = sorted(set(no_invert))
    no_invert_info = sorted(set(no_invert_info))
    no_original = sorted(set(no_original))
    no_original_info = sorted(set(no_original_info))
    just_info = sorted(set(just_info))
    # output to log
    logFilename = u'¤conversion-errors.log'
    f = codecs.open(os.path.join(path, logFilename), 'w', 'utf-8')
    f.write(u'Total: %d, problems %d\n' % (len(os.listdir(path)),
                                           len(no_invert) + len(no_original)))
    f.write(u'\n== no_invert: %d ==\n' % len(no_invert))
    for i in no_invert:
        f.write(u'%s\n' % i)
    f.write(u'\n== no_original: %d ==\n' % len(no_original))
    for i in no_original:
        f.write(u'%s\n' % i)
    f.write(u'\n== no_invert_info: %d ==\n' % len(no_invert_info))
    for i in no_invert_info:
        f.write(u'%s\n' % i)
    f.write(u'\n== no_original_info: %d ==\n' % len(no_original_info))
    for i in no_original_info:
        f.write(u'%s\n' % i)
    f.write(u'\n== just_info: %d ==\n' % len(just_info))
    for i in just_info:
        f.write(u'%s\n' % i)
    f.close()


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
            negativeCleanup(path=path)
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
