#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Legacy file. Now serving only as a wrapper for batchupload.uploader
#
import helpers
import batchupload.uploader as uploader


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
            uploader.up_all(path, cutoff=cutoff)
        else:
            uploader.up_all(path)
    else:
        print usage
