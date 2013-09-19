# -*- coding: UTF-8  -*-
#
# Uploading files
#
'''Specifications:
    
'''
import codecs, os, sys
from PyCJWiki import Wiki
import config as config

def setUp(password, user):
    #Provide url and identify (either talk-page url or email)
    commons = Wiki("http://commons.wikimedia.org/w/api.php","http://commons.wikimedia.org/wiki/User_talk:%s" %user)
    
    #Login
    commons.login(user,password)
    #Get an edittoken
    commons.setEditToken()
    return commons
    
def upFiles(path, password=config.password, user=config.username, target=u'Uploaded'):
    '''
    Uploads files to Commons. Moves any processed files to the target folder
    '''
    cwd = os.getcwd()
    os.chdir(path)
    commons = setUp(password, user)
    flog = codecs.open(u'¤uploader.log','a', 'utf-8') #redirect print to logfile for the sake of PyCJWiki
    #sys.stdout = open(os.path.join(os.getcwd(),u'¤uploader.log'), 'w') #redirect print to logfile for the sake of PyCJWiki
    
    #create targetdirectory if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)
    
    count =0
    files = os.listdir(u'.')
    for f in files:
        if f.endswith(u'.tif') or f.endswith(u'.jpg'):
            infoFile = u'%s.txt' %f[:-4]
            if not os.path.exists(infoFile):
                flog.write(u'%s: Found tif without info' %f)
                continue
            infoIn = codecs.open(infoFile, 'r', 'utf-8')
            info = infoIn.read()
            infoIn.close()
            result = commons.chunkupload(f,f,info,u'Batch upload for [[COM:LSH]]. Working on folder: %s. See [[Commons:Batch_uploading/LSH]] for more info' %path.split(u'/')[-1].upper())
            flog.write(u'%s\n' %result.decode('utf8'))
            flog.flush()
            #Move files
            os.rename(f, os.path.join(target,f))
            os.rename(infoFile, os.path.join(target,infoFile))
    commons.logout()
    os.chdir(cwd) #so that same path structure can be used for next call
    flog.close()

def updateInfo(path, password=config.password, user=config.username, target=u'Updated'):
    '''
    Rewrites the information on the given filepages. Essentially upFiles without the filetransfer
    '''
    cwd = os.getcwd()
    os.chdir(path)
    commons = setUp(password, user)
    flog = codecs.open(u'¤updater.log','a', 'utf-8') #redirect print to logfile for the sake of PyCJWiki
    comment = u'Updating information page due to improved algorithm for batch upload. See [[Commons:Batch_uploading/LSH]] for more info'
    #sys.stdout = open(os.path.join(os.getcwd(),u'¤uploader.log'), 'w') #redirect print to logfile for the sake of PyCJWiki
    
    #create targetdirectory if it doesn't exist
    if not os.path.isdir(target):
        os.mkdir(target)
    
    count =0
    files = os.listdir(u'.')
    for f in files:
        if f.endswith(u'.tif'):
            infoFile = u'%s.txt' %f[:-4]
            if not os.path.exists(infoFile):
                flog.write(u'%s: Found tif without info' %f)
                continue
            infoIn = codecs.open(infoFile, 'r', 'utf-8')
            info = infoIn.read()
            infoIn.close()
            result = commons.editText(u'File:%s' %f, info, comment, minor=False, bot=True, userassert='exists', nocreate=True)
            flog.write(u'%s\n' %result.decode('utf8'))
            flog.flush()
            #Move files
            os.rename(f, os.path.join(target,f))
            os.rename(infoFile, os.path.join(target,infoFile))
    commons.logout()
    os.chdir(cwd) #so that same path structure can be used for next call
    flog.close()
    
