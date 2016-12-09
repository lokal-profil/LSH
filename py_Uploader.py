#!/usr/bin/python
# -*- coding: UTF-8  -*-
#
# Legacy file. Now serving only as a wrapper for batchupload.uploader
#
import pywikibot
import batchupload.common as common
import batchupload.uploader as uploader


def main(*args):
    """Command line entry-point."""
    usage = u'Usage:\n' \
            u'\tpython py_Uploader.py -path:<1> -cutoff:<2> -chunked:<3> -verbose:<4>\n' \
            u'\tpath: the relative path to the directory containing ' \
            u'images and descriptions.\n' \
            u'\tcutoff is optional and allows the upload to stop after ' \
            u'the specified number of files.\n' \
            u'\tchunked is optional and allows the upload to be run without ' \
            u'chunked uploading if given "False" or "F".\n' \
            u'\tverbose is optional and allows the upload to be more chatty ' \
            u'if given "True" or "T".'
    path = None
    cutoff = None
    chunked = True
    verbose = False

    # Load pywikibot args and handle local args
    for arg in pywikibot.handle_args(args):
        option, sep, value = arg.partition(':')
        if option == '-path':
            path = common.convert_from_commandline(value)
        elif option == '-cutoff':
            cutoff = int(value)
        elif option == '-chunked':
            if value.lower() in ('false', 'f'):
                chunked = False
        elif option == '-verbose':
            if value.lower() in ('true', 't'):
                verbose = True
        elif option == '-usage':
            pywikibot.output(usage)
            return

    if path:
        uploader.up_all(path, cutoff=cutoff, chunked=chunked, verbose=verbose)
    else:
        pywikibot.output(usage)

if __name__ == '__main__':
    main()
