#!/usr/bin/python
# -*- coding: UTF-8
#
# Preparing original csv files
#
# KNOWN LIMITATIONS:
# * The first cell must NEVER be linebroken (since one cannot detect the
#   difference between a linbroken last cell and a linebroken first cell)
# * Original csv must be UTF encoded with "|" as cell separator and no
#   field separator
#
# TODO:
#   Set up CSV_FILES so that version no/data can more easily be updated/read
#
# Includes the following old files:
# * FixFile.py
# * FixFile-fullObjDaten.py (partially)
#
'''
what to run:
fixFiles() - converts orignal csv to cleaned up csv, run from main folder
'''
import codecs
import os
import re  # only needed for hackfix

CSV_DIR_ORIG = u'original_csv'
CSV_DIR_CLEAN = u'clean_csv'

CSV_FILES = {  # all of these must be present
    'ausstellung': u'Ausstellung 2.0.csv',
    'kuenstler': u'kuenstler 2.0.csv',
    'objDaten': u'ObjDaten 2.0 - alla objId 2014-10-23.csv',
    'objMass': u'ObjMass 2.0.csv',
    'photo': u'photo 2.0.csv',
    'stichwort': u'Photo_stichwort 2.0.csv',
    'ereignis': u'Ereignis 2.0.csv',
    'multimedia': u'multimedia 2.0.csv',
    'objDatenSam': u'ObjDaten - samhФrande nr 2.0.csv',
    'objMultiple': u'ObjMultiple 2.0.csv',
    'photoObjDaten': u'Photo - ObjDaten 2.0.csv'
}


def fixFiles(in_path=CSV_DIR_ORIG, out_path=CSV_DIR_CLEAN, encoding='utf-16'):
    '''
    Checks that the required files are present, converts them from utf-16,
    replaces \r\n linbreaks, replaces in-cell linebreaks with <!>,
    removes BOM and outputs as UTF-8 encoded with \n linebreaks and
    |-cell separation
    param: (optional) in_path - the folder containing the original csv files
    param: (optional) out_path - the folder to which cleand csv are written
    param: (optional) encoding - encoding of the original files
    '''
    # convert to unicode if not the case
    if type(in_path) == str:
        in_path = unicode(in_path)
    if type(out_path) == str:
        out_path = unicode(out_path)
    # check that path is a directory and all files are present
    if not os.path.isdir(in_path):
        print u"Given path \"%s\" is not a directory" % in_path
    for k, v in CSV_FILES.iteritems():
        if v not in os.listdir(in_path):
            print u"Required file \"%s\" is not present in " \
                  u"\"%s\"" % (v, in_path)
    # create target if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    # convert the files and output a clean copy
    for k, v in CSV_FILES.iteritems():
        file_out = u'%s/%s.csv' % (out_path, k)
        file_in = u'%s/%s' % (in_path, v)
        fixLinebreak(file_in, file_out, encoding)
    print u"Done!"


# ideally this is removable by correcting the source
def hackfix(txt, file_out):
    '''
    runs a few hackish fixes to correct problems discovered
    in the original csv files
    ObjMultiple:
    1) Remove any S:\[...].jpg
    '''
    txt_orig = txt
    if file_out.endswith(u'objMultiple.csv'):
        txt = re.sub(r'S:\\[^.]*.(jpg|JPG)', u'', txt)
        if txt_orig == txt:
            print "hackfix not needed for objMultiple"
    return txt


def fixLinebreak(file_in, file_out, encoding):
    '''
    Given a filename this loads the required file and:
    replaces \r\n linbreaks with \n;
    replaces in-cell linebreaks with <!>
    param: file_in - filename to load (including path)
    param: file_out - filename to write to (including path)
    param: encoding - encoding to load the file with
    returns: the loaded treated text
    '''
    # load, convert and parse file
    fin = codecs.open(file_in, 'r', encoding)
    txt = fin.read()
    fin.close()
    txt = txt.replace(u'\r\n', u'\n')  # if windows encoded
    txt = txt.replace(u'\r', u'<!>')   # remaining are in-cell linebreaks

    # hack in the corrections found before
    txt = hackfix(txt, file_out)

    # split into lines and separate header
    lines = txt.split('\n')
    header = lines.pop(0).split('|')   # first line is the header

    # output cleaned file and deal with potential bad linebreaks
    fout = codecs.open(file_out, 'w', 'utf-8')
    # output header
    fout.write(u'|'.join(header))

    # To deal with additional linebreaks record the previous printed line
    # and count until the right number of cells are reached
    prevline = u''
    for line in lines:
        if len(line.strip()) == 0:
            # skip empties
            continue
        if (prevline == u'') and (len(line.split('|')) == 1):
            # if the last cell is line broken then this must be detected
            # and the output added to the previous line
            fout.write(u'<!>%s' % line)
            continue

        comb = u'%s<!>%s' % (prevline, line)
        if len(comb.split('|')) == len(header):
            fout.write(u'\n%s' % comb[3:])  # remove leading <!>
            prevline = u''         # reset prevline
        elif len(comb.split('|')) > len(header):
            print u'Found to many pipes in a line of %s please ' \
                  u'correct manually:\n%s' % (file_out, comb[3:])
            break
        else:
            prevline = comb      # set prevline

    # verify that no data has remained unprinted
    if prevline not in (u'', u'<!>'):
        print u"The following was not printed to " \
              u"<%s>: <%s>" % (file_out, prevline)
    fout.close()


if __name__ == '__main__':
    import sys
    usage = u'Usage:\tpython py_prepCSVData.py in_path out_path\n' \
        u'\tin_path (optional): the relative pathname to the csv directory.\n' \
        u'out_path (optional):the relative pathname to the target directory.\n' \
        u'\tEither provide both or leave them out ' \
        u'(thus defaulting to "%s", "%s")' % (CSV_DIR_ORIG, CSV_DIR_CLEAN)
    argv = sys.argv[1:]
    if len(argv) == 0:
        fixFiles()
    elif len(argv) == 2:
        fixFiles(in_path=argv[0], out_path=argv[1])
    else:
        print usage
# EoF
