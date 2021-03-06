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
import json
import helpers
import re  # only needed for hackfix

CSV_DIR_ORIG = u'original_csv'
CSV_DIR_CLEAN = u'clean_csv'
CSV_CONFIG = u'csv_config.json'


def fixFiles(in_path=None, out_path=None, encoding='utf-16'):
    """
    Checks that the required files are present, converts them from utf-16,
    replaces \r\n linbreaks, replaces in-cell linebreaks with <!>,
    removes BOM and outputs as UTF-8 encoded with \n linebreaks and
    |-cell separation
    :param in_path: the folder containing the original csv files (optional)
    :param out_path: the folder to which cleand csv are written (optional)
    :param encoding: encoding of the original files (optional)
    :return: None
    """
    # set defaults unless overridden
    in_path = in_path or CSV_DIR_ORIG
    out_path = out_path or CSV_DIR_CLEAN

    # convert to unicode if not the case
    if type(in_path) == str:
        in_path = unicode(in_path)
    if type(out_path) == str:
        out_path = unicode(out_path)

    # check that path is a directory and all files are present
    if not os.path.isdir(in_path):
        raise Exception(u"The provided path \"%s\" is not a directory"
                        % in_path)

    # read csv files from config
    f = codecs.open(CSV_CONFIG, 'r', 'utf-8')
    csvFiles = json.load(f)
    f.close()

    for k, v in csvFiles.iteritems():
        if v not in os.listdir(in_path):
            raise Exception(u"Required file \"%s\" is not present in "
                            u"\"%s\"" % (v, in_path))
    # create target if it doesn't exist
    if not os.path.isdir(out_path):
        os.mkdir(out_path)

    # convert the files and output a clean copy
    for k, v in csvFiles.iteritems():
        file_out = os.path.join(out_path, u'%s.csv' % k)
        file_in = os.path.join(in_path, v)
        fixLinebreak(file_in, file_out, encoding)
    print u"Done!"


# ideally this is removable by correcting the source
def hackfix(txt, file_out):
    """
    runs a few hackish fixes to correct problems discovered
    in the original csv files
    ObjMultiple:
    1) Remove any S:\[...].jpg
    :param txt: text to process
    :param file_out: (output) name of file being processed
    :return: str
    """
    txt_orig = txt
    if file_out.endswith(u'objMultiple.csv'):
        txt = re.sub(r'S:\\[^.]*.(jpg|JPG)', u'', txt)
        if txt_orig == txt:
            print "hackfix not needed for objMultiple"
    return txt


def fixLinebreak(file_in, file_out, encoding):
    """
    Given a filename this loads the required file and:
    replaces \r\n linbreaks with \n;
    replaces in-cell linebreaks with <!>
    :param file_in: filename to load (including path)
    :param file_out: filename to write to (including path)
    :param encoding: encoding to load the file with
    :return: str - the loaded treated text
    """
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
        if not line.strip():
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
                  u'correct manually and rerun:\n%s' % (file_in, comb[3:])
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
    if not argv:
        fixFiles()
    elif len(argv) == 2:
        in_path = helpers.convertFromCommandline(argv[0])
        out_path = helpers.convertFromCommandline(argv[1])
        fixFiles(in_path=in_path, out_path=out_path)
    else:
        print usage
# EoF
