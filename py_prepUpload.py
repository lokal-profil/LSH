# -*- coding: UTF-8  -*-
#
# Preparing files for upload
#
'''Specifications:
    moveHits(path=u'../diskkopia') to move all relevant files to the base folders
    makeAndRename(path=u'../diskkopia/m_dig') etc. to make info files and rename
    negatives(path=u'../diskkopia/m_b') etc. for the folders starting A, B, E, O
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
    #create target if it doesn't exist
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
    f=codecs.open(u'deriv-filenames.csv','r','utf8')
    lines=f.read().split('\n')
    tree = {}
    nameToPho = {}
    first=True
    for l in lines:
        if first or len(l)==0:
            first = False
            continue
        (phoId,mullId,path,name,new_name) = l.split('|')
        path = path.replace('\\','/') #linux<->windows
        if path in tree.keys():
            tree[path].append(name)
        else:
            tree[path] = [name,]
        nameToPho[name] = {'phoMull':u'%s:%s' % (phoId,mullId),'filename':new_name}
    return (tree, nameToPho)

def moveHits(path):
    '''
    run from main dir
    path=path from running directory to direcotry with image file structure
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
    flog = codecs.open(os.path.join(path,u'¤generator.log'), 'w', 'utf-8') #logfile
    maker = MakeInfo()
    maker.readInLibraries()
    maker.readConnections()
    for filename_in in os.listdir(path):
        if not filename_in[:-4] in nameToPho.keys():
            flog.write(u'%s did not have a photoId\n' %filename_in)
            continue
        phoMull = nameToPho[filename_in[:-4]]['phoMull']
        filename_out = nameToPho[filename_in[:-4]]['filename'].replace(u' ',u'_')
        wName, out = maker.infoFromPhoto(phoMull, preview=False, testing=False)
        if out:
            #Make info file
            infoFile = u'%s.txt' %filename_out[:-4]
            f = codecs.open(os.path.join(path,infoFile), 'w', 'utf-8')
            f.write(out)
            f.close()
            #Move image file
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
    for filename in os.listdir(path):
        if filename.endswith(u'.tif'):
            negative = u'%s-negative.tif' % filename[:-4]
            os.rename(os.path.join(path,filename), os.path.join(path,negative))
            imageMagick = u'convert %s -negate -auto-gamma -level 10%%,90%%,1,0 %s' %(os.path.join(path,negative), os.path.join(path,filename))
            imageMagick = u'%s 2>>%s' %(imageMagick, os.path.join(path,u'¤imageMagick-errors.log')) #pipe errors to file
            os.system(imageMagick.encode(encoding='UTF-8')) 
            #new info files
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
                print u'%r files inverted' %count

def negPosInfo(infoFile, filename):
    '''
    generate a negative and positive version of the given info file
    '''
    #for negative we want to remove cats (i.e. anything after </gallery>\n}} )
    #instead go through info and identify |source= LRK + end position
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
    source=u''
    lines=infoFile.split('\n')
    for l in lines:
        if l.startswith(u'|source='):
            source = l.split(u'=')[-1].strip()
            break
    pos = u'%s\n{{LSH positive|%s}}\n%s' %(infoFile[:end], u'%s-negative.%s' %(filename[:-4],filename[-3:]), infoFile[end:])
    neg = u'{{LSH negative|%s|%s}}\n%s' %(filename, source, infoFile[:end])
    return (neg, pos)

def catTest(path, nameToPho=None):
    '''
    check the category statistics for the files in a given folder
    '''
    if not nameToPho:
        (tree, nameToPho) = makeHitlist()
    flog = codecs.open(os.path.join(path,u'¤catStats.log'), 'w', 'utf-8') #logfile
    maker = MakeInfo()
    phoMull_list=[]
    for filename_in in os.listdir(path):
        if not filename_in[:-4] in nameToPho.keys():
            continue
        phoMull_list.append(nameToPho[filename_in[:-4]]['phoMull'])
    maker.catTestBatch(phoMull_list, flog)
    flog.close()
