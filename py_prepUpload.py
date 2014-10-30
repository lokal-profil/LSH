# -*- coding: UTF-8  -*-
#
# Preparing files for upload and adding file extentions to filenames
#
# TODO: Make imagemagic handle ")"-characters
#
import os
import codecs
from py_MakeInfo import MakeInfo

# filename file
FILENAMES = u'data/filenames.csv'


def findFiles(path=u'.', filetypes=[u'.tif', u'.jpg']):
    '''
    first call should be without the path parameter
    if not run from the starting directory then first use
    os.chdir(path)
    '''
    files = []
    subdirs = []
    for filename in os.listdir(path):
        try:
            if any(filename.endswith(x) for x in filetypes):
                files.append(os.path.join(path, filename))
        except UnicodeDecodeError:
            print 'UnicodeDecodeError: %s' % os.path.join(path, filename)
            exit
        if os.path.isdir(os.path.join(path, filename)):
            subdirs.append(os.path.join(path, filename))
    for subdir in subdirs:
        files += findFiles(path=subdir)
    return files


def moveFiles(target, tree, nameToPho, path=u'.', filetypes=[u'.tif', u'.jpg']):
    '''
    move all files in the given dir and subdirs of the specified
    filetypes to the target dir
    '''
    # create target if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)
    files = findFiles(path, filetypes)
    counter = 0
    for filename in files:
        plain_name = filename.split('/')[-1]
        filepath = filename[:-len(plain_name)].strip(u'./')
        if filepath in tree.keys() and plain_name[:-4] in tree[filepath]:
            os.rename(filename, os.path.join(target, plain_name))
            counter += 1
            # record the actual file extention
            nameToPho[plain_name[:-4]]['ext'] = plain_name[-3:]
    return (counter, len(files))


def makeHitlist(filename_file=FILENAMES):
    '''
    Goes through the allowed filenames and builds up a treestructure
    as well as a look-up dictionary for filenames to phoId (and new filenames).
    '''
    f = codecs.open(filename_file, 'r', 'utf8')
    lines = f.read().split('\n')
    tree = {}
    nameToPho = {}
    first = True
    for l in lines:
        if first or len(l) == 0:
            first = False
            continue
        phoId, mullId, path, name, new_name, ext = l.split('|')
        path = path.replace('\\', '/')  # linux<->windows
        if path in tree.keys():
            tree[path].append(name)
        else:
            tree[path] = [name, ]
        nameToPho[name] = {'phoMull': u'%s:%s' % (phoId, mullId),
                           'filename': new_name,
                           'ext': ext}
    return (tree, nameToPho)


def moveHits(path):
    '''
    run from main dir
    path: path from running directory to directory with image file structure
    '''
    tree, nameToPho = makeHitlist()
    cwd = os.getcwd()
    os.chdir(path)
    subdirs = []
    for filename in os.listdir('.'):
        if os.path.isdir(os.path.join('.', filename)) and filename.isupper():
            subdirs.append(filename)
    for subdir in subdirs:
        counter, fileNum = moveFiles(subdir.lower(), tree, nameToPho, path=subdir, filetypes=[u'.tif', u'.jpg'])
        print u'%s: %r out of %r were hits' % (subdir, counter, fileNum)
    os.chdir(cwd)

    # Now add found extentions to filenames file
    f = codecs.open(FILENAMES, 'r', 'utf8')
    lines = f.read().split('\n')
    f.close()
    f = codecs.open(FILENAMES, 'w', 'utf8')
    header = lines.pop(0)
    f.write(u'%s\n' % header)
    for l in lines:
        if len(l) == 0:
            continue
        col = l.split('|')
        name = col[3]
        if name in nameToPho.keys():
            col[5] = nameToPho[name]['ext']  # overwrite extention
        f.write(u'%s\n' % '|'.join(col))
    f.close()


def makeAndRename(path):
    '''
    Create infofile and rename image file
    path is the realtive path to the folder in which to process the files
    '''
    tree, nameToPho = makeHitlist()
    catTest(path)
    flog = codecs.open(os.path.join(path, u'¤generator.log'), 'w', 'utf-8')  # logfile
    maker = MakeInfo()
    maker.readInLibraries()
    maker.readConnections()
    for filename_in in os.listdir(path):
        if filename_in.startswith(u'¤'):  # log files
            continue
        elif not filename_in[:-4] in nameToPho.keys():
            flog.write(u'%s did not have a photoId\n' % filename_in)
            continue
        phoMull = nameToPho[filename_in[:-4]]['phoMull']
        filename_out = nameToPho[filename_in[:-4]]['filename'].replace(u' ', u'_')
        wName, out = maker.infoFromPhoto(phoMull, preview=False, testing=False)
        if out:
            # Make info file
            infoFile = u'%s.txt' % filename_out[:-4]
            f = codecs.open(os.path.join(path, infoFile), 'w', 'utf-8')
            f.write(out)
            f.close()
            # Move image file
            os.rename(os.path.join(path, filename_in), os.path.join(path, u'%s%s' % (filename_out[:-4], filename_in[-4:])))
            flog.write(u'%s outputed to %s\n' % (filename_in, filename_out))
        else:
            flog.write(u'%s failed to make infopage. See log\n' % filename_in)


def negatives(path):
    '''
    moves file to filename-negative.tif
    creates an inverted file at filename.tif
    creates a info file for negative and modifes info file for positive
    path is the realtive path to the folder in which to process the files
    '''
    count = 0
    skipcount = 0
    for filename in os.listdir(path):
        if filename.endswith(u'.tif') and not filename.endswith(u'-negative.tif'):
            negative = u'%s-negative.tif' % filename[:-4]
            if os.path.isfile(os.path.join(path, negative)):
                print u'%s was already inverted, skipping...' % filename
                skipcount += 1
                continue
            os.rename(os.path.join(path, filename), os.path.join(path, negative))
            imageMagick = u'convert %s -negate -auto-gamma -level 10%%,90%%,1,0 %s' % (os.path.join(path, negative), os.path.join(path, filename))
            imageMagick = u'%s 2>>%s' % (imageMagick, os.path.join(path, u'¤imageMagick-errors.log'))  # pipe errors to file
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
                print u'%r files inverted (%r)' % (count, count+skipcount)


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


def catTest(path, nameToPho=None):
    '''
    check the category statistics for the files in a given folder
    '''
    if not nameToPho:
        (tree, nameToPho) = makeHitlist()
    flog = codecs.open(os.path.join(path, u'¤catStats.log'), 'w', 'utf-8')  # logfile
    maker = MakeInfo()
    phoMull_list = []
    for filename_in in os.listdir(path):
        if not filename_in[:-4] in nameToPho.keys():
            continue
        phoMull_list.append(nameToPho[filename_in[:-4]]['phoMull'])
    maker.catTestBatch(phoMull_list, flog)
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
    f.write(u'Total: %r, problems %r\n' % (len(os.listdir(path)), len(no_invert)+len(no_original)))
    f.write(u'\n== no_invert: %r ==\n' % len(no_invert))
    for i in no_invert:
        f.write(u'%s\n' % i)
    f.write(u'\n== no_original: %r ==\n' % len(no_original))
    for i in no_original:
        f.write(u'%s\n' % i)
    f.write(u'\n== no_invert_info: %r ==\n' % len(no_invert_info))
    for i in no_invert_info:
        f.write(u'%s\n' % i)
    f.write(u'\n== no_original_info: %r ==\n' % len(no_original_info))
    for i in no_original_info:
        f.write(u'%s\n' % i)
    f.write(u'\n== just_info: %r ==\n' % len(just_info))
    for i in just_info:
        f.write(u'%s\n' % i)
    f.close()


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_prepUpload.py action path\n' \
        u'\taction: moveHits - moves the relevant files to base folders ' \
        u'and adds extention to filenames\n' \
        u'\t\tpath: relative pathname to main directory for images\n' \
        u'\taction: makeAndRename - make info files and rename\n' \
        u'\t\tpath: relative pathname to a directory containing images\n' \
        u'\taction: negatives - create positives for the relevant folders\n' \
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
        argv[1] = unicode(argv[1])  # risky but unsure how else t
        if argv[0] == 'moveHits':
            moveHits(path=argv[1])
        elif argv[0] == 'makeAndRename':
            makeAndRename(path=argv[1])
        elif argv[0] == 'negatives':
            negatives(path=argv[1])
        elif argv[0] == 'negativeCleanup':
            negativeCleanup(path=argv[1])
        else:
            print usage
    else:
        print usage
# EoF
