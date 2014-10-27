# -*- coding: UTF-8  -*-
#
# Preparing files for upload
#
'''Specifications:
    moveHits(path=u'../diskkopia') to move all relevant files to the base folders
    makeAndRename(path=u'../diskkopia/m_dig') etc. to make info files and rename
    negatives(path=u'../diskkopia/m_b') etc. for the folders starting A, B, E, O
    negativeCleanup(path=u'../diskkopia/m_b') etc. to spot any conversion problems
'''
import os
import codecs
from py_MakeInfo import MakeInfo

def findFiles(path = u'.', filetypes=[u'.tif',u'.jpg']):
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
                files.append(os.path.join(path,filename))
        except UnicodeDecodeError:
            print 'UnicodeDecodeError: %s' %os.path.join(path,filename)
            exit
        if os.path.isdir(os.path.join(path,filename)):
            subdirs.append(os.path.join(path,filename))
    for subdir in subdirs:
        files = files + findFiles(path=subdir)
    return files

def moveFiles(target, tree, path = u'.', filetypes=[u'.tif',u'.jpg']):
    '''move all files in the given dir and subdirs of the specified filetypes
    to the target dir'''
    # create target if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)
    files = findFiles(path, filetypes)
    counter = 0
    for filename in files:
        plain_name = filename.split('/')[-1]
        filepath = filename[:-len(plain_name)].strip(u'./')
        if filepath in tree.keys() and plain_name[:-4] in tree[filepath]:
            os.rename(filename, os.path.join(target,plain_name))
            counter = counter+1
    return (counter,len(files))

def makeHitlist():
    '''
    Goes through the allowed filenames and builds up a treestructure as well as a
    look-up dictionary for filenames to phoId (and new filenames).
    '''
    f=codecs.open(u'data/deriv-filenames.csv','r','utf8')
    lines=f.read().split('\n')
    tree = {}
    nameToPho = {}
    first=True
    for l in lines:
        if first or len(l)==0:
            first = False
            continue
        (phoId,mullId,path,name,new_name) = l.split('|')
        path = path.replace('\\','/')  # linux<->windows
        if path in tree.keys():
            tree[path].append(name)
        else:
            tree[path] = [name,]
        nameToPho[name] = {'phoMull':u'%s:%s' % (phoId,mullId),'filename':new_name}
    return (tree, nameToPho)

def moveHits(path):
    '''
    run from main dir
    path=path from running directory to directory with image file structure
    '''
    (tree, nameToPho) = makeHitlist()
    cwd = os.getcwd()
    os.chdir(path)
    subdirs = []
    for filename in os.listdir('.'):
        if os.path.isdir(os.path.join('.',filename)) and filename.isupper():
            subdirs.append(filename)
    for subdir in subdirs:
        (counter, fileNum) = moveFiles(subdir.lower(), tree, path = subdir, filetypes=[u'.tif',u'.jpg'])
        print u'%s: %r out of %r were hits' %(subdir,counter, fileNum)
    os.chdir(cwd)

def makeAndRename(path):
    '''
    Create infofile and rename image file
    path is the realtive path to the folder in which to process the files
    '''
    (tree, nameToPho) = makeHitlist()
    catTest(path)
    flog = codecs.open(os.path.join(path,u'¤generator.log'), 'w', 'utf-8')  # logfile
    maker = MakeInfo()
    maker.readInLibraries()
    maker.readConnections()
    for filename_in in os.listdir(path):
        if filename_in.startswith(u'¤'):  # log files
            continue
        elif not filename_in[:-4] in nameToPho.keys():
            flog.write(u'%s did not have a photoId\n' %filename_in)
            continue
        phoMull = nameToPho[filename_in[:-4]]['phoMull']
        filename_out = nameToPho[filename_in[:-4]]['filename'].replace(u' ',u'_')
        wName, out = maker.infoFromPhoto(phoMull, preview=False, testing=False)
        if out:
            # Make info file
            infoFile = u'%s.txt' %filename_out[:-4]
            f = codecs.open(os.path.join(path,infoFile), 'w', 'utf-8')
            f.write(out)
            f.close()
            # Move image file
            os.rename(os.path.join(path,filename_in), os.path.join(path,u'%s%s' %(filename_out[:-4],filename_in[-4:])))
            flog.write(u'%s outputed to %s\n' %(filename_in, filename_out))
        else:
            flog.write(u'%s failed to make infopage. See log\n' %filename_in)
        
def negatives(path):
    '''
    moves file to filename-negative.tif
    creates an inverted file at filename.tif
    creates a info file for negative and modifes info file for positive
    path is the realtive path to the folder in which to process the files
    '''
    count = 0
    skipcount=0
    for filename in os.listdir(path):
        if filename.endswith(u'.tif') and not filename.endswith(u'-negative.tif'):
            negative = u'%s-negative.tif' % filename[:-4]
            if os.path.isfile(os.path.join(path,negative)):
                print u'%s was already inverted, skipping...' % filename
                skipcount = skipcount +1
                continue
            os.rename(os.path.join(path,filename), os.path.join(path,negative))
            imageMagick = u'convert %s -negate -auto-gamma -level 10%%,90%%,1,0 %s' %(os.path.join(path,negative), os.path.join(path,filename))
            imageMagick = u'%s 2>>%s' %(imageMagick, os.path.join(path,u'¤imageMagick-errors.log'))  # pipe errors to file
            os.system(imageMagick.encode(encoding='UTF-8')) 
            # new info files
            infoFilename = u'%s.txt' %filename[:-4]
            f = codecs.open(os.path.join(path,infoFilename), 'r', 'utf-8')
            infoFile = f.read()
            f.close()
            (negInfo, posInfo) = negPosInfo(infoFile, filename.replace(u'_',u' '))
            f = codecs.open(os.path.join(path,u'%s-negative.txt' %infoFilename[:-4]), 'w', 'utf-8')
            f.write(negInfo)
            f.close()
            f = codecs.open(os.path.join(path,infoFilename), 'w', 'utf-8')
            f.write(posInfo)
            f.close()
            count=count+1
            if count%10 == 0:
                print u'%r files inverted (%r)' %(count, count+skipcount)

def negPosInfo(infoFile, filename):
    '''
    generate a negative and positive version of the given info file
    '''
    ovPos = infoFile.find(u'|other_versions=')
    # for negative we want to remove cats (i.e. anything after </gallery>\n}} )
    # so need to identify end position
    end = infoFile.find(u'</gallery>\n}}')
    if end>0:
        end=end+len(u'</gallery>\n}}')
    else:
        end = infoFile.find(u'|other_versions= \n}}')
        if end>0:
            end=end+len(u'|other_versions= \n}}')
        else:
            print '%s: could not find end of template' %filename
            end = ''
    pos = u'%s|negative= %s\n%s' %(infoFile[:ovPos], u'%s-negative.%s' %(filename[:-4],filename[-3:]), infoFile[ovPos:])
    neg = u'%s|positive= %s\n%s' %(infoFile[:ovPos], filename, infoFile[ovPos:end])
    return (neg, pos)

def catTest(path, nameToPho=None):
    '''
    check the category statistics for the files in a given folder
    '''
    if not nameToPho:
        (tree, nameToPho) = makeHitlist()
    flog = codecs.open(os.path.join(path,u'¤catStats.log'), 'w', 'utf-8')  # logfile
    maker = MakeInfo()
    phoMull_list=[]
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
    count = 0
    no_invert = []
    no_invert_info = []
    no_original = []
    no_original_info = []
    just_info = []
    for filename in os.listdir(path):
        if filename.endswith(u'-negative.tif'):
            positive = filename[:-len(u'-negative.tif')]
            negative = filename[:-len('.tif')]
            if not os.path.isfile(os.path.join(path, u'%s.tif' %positive)): no_original.append(u'%s.tif' %positive)     # check if .tif exists
            if not os.path.isfile(os.path.join(path, u'%s.txt' %positive)): no_original_info(u'%s.txt' %positive)       # check if .txt exists
            if not os.path.isfile(os.path.join(path, u'%s.tif' %negative)): no_invert_info.append(u'%s.txt' %negative)  # check if -negative.txt exists
        elif filename.endswith(u'.tif'):
            positive = filename[:-len(u'.tif')]
            negative = u'%s-negative' %filename[:-len('.tif')]
            if not os.path.isfile(os.path.join(path, u'%s.tif' %negative)): no_invert.append(u'%s.tif' %negative)       # check if -negative.tif exists
            if not os.path.isfile(os.path.join(path, u'%s.txt' %positive)): no_original_info(u'%s.txt' %positive)       # check if .txt exists
            if not os.path.isfile(os.path.join(path, u'%s.tif' %negative)): no_invert_info.append(u'%s.txt' %negative)  # check if -negative.txt exists
        elif filename.endswith(u'.txt'):
            # check that either -negative.tif or .tif exists (if so then dealt with by above)
            if filename.endswith(u'-negative.txt'):
                positive = filename[:-len(u'-negative.txt')]
                negative = filename[:-len(u'.txt')]
            else:
                positive = filename[:-len(u'.txt')]
                negative = u'%s-negative' % filename[:-len(u'.txt')]
            if not os.path.isfile(os.path.join(path, u'%s.tif' %negative)) and not os.path.isfile(os.path.join(path, u'%s.tif' %positive)):
                just_info.append(filename)
    # sort and remove any dupes
    no_invert = sorted(set(no_invert))
    no_invert_info = sorted(set(no_invert_info))
    no_original = sorted(set(no_original))
    no_original_info = sorted(set(no_original_info))
    just_info = sorted(set(just_info))
    # output to log
    logFilename = u'¤conversion-errors.log'
    f = codecs.open(os.path.join(path,logFilename), 'w', 'utf-8')
    f.write(u'Total: %r, problems %r\n' %(len(os.listdir(path)),len(no_invert)+len(no_original)))
    f.write(u'\n== no_invert: %r ==\n' %len(no_invert))
    for i in no_invert:
        f.write(u'%s\n' %i)
    f.write(u'\n== no_original: %r ==\n' %len(no_original))
    for i in no_original:
        f.write(u'%s\n' %i)
    f.write(u'\n== no_invert_info: %r ==\n' %len(no_invert_info))
    for i in no_invert_info:
        f.write(u'%s\n' %i)
    f.write(u'\n== no_original_info: %r ==\n' %len(no_original_info))
    for i in no_original_info:
        f.write(u'%s\n' %i)
    f.write(u'\n== just_info: %r ==\n' %len(just_info))
    for i in just_info:
        f.write(u'%s\n' %i)
    f.close()
