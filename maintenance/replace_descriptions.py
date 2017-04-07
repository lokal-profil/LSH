#!/usr/bin/python
# -*- coding: UTF-8  -*-
"""
Attempt replacing file descriptions pages while preserving user changes.

Notes:
* For non-LSH use you have to ensure that the outputted filenames corresponds
  to the actual filenames used on Commons. Else you need to replace the
  filename field in the make_info json by the actual Commons filenames.
* "only categories" means only categories have changed since the first
  upload, not that only categories will be changed.

Temporary visitor in LSH repo before mostly being moved to BatchUploads.
To make this work in LSH:
* Generate clean csv with the target files in photo.csv and multimedia.csv
* Run analysis, crunch and filenames
* run maintanance/replace_descriptions
"""
from __future__ import unicode_literals
from builtins import dict, object, open
import pywikibot
from pywikibot import textlib

from batchupload.make_info import make_info_page
from py_MakeInfo import MakeInfo

DATA_DIR = 'data'
CONNECTIONS_DIR = 'connections'


class UpdatedPage(object):
    """Object holding page to be updated and its replacement."""

    def __init__(self, page, new_text, dry_run=True, summary=None,
                 minor=True):
        """
        Initialise object.

        :param page: pywikibot.Page to modify
        :param new_text: replacement wikitext file description page
        :param dry_run: if we are just simulating an update
        :param summary: edit summary to use if an edit is made
        :param minor: if the edit should be considered minor
        """
        self.site = page.site
        self.page = page
        self.new_text = new_text
        self.dry = dry_run
        self.summary = summary
        self.minor = minor

        self.text = None
        self.first_text = page.getOldVersion(page.oldest_revision.revid)
        self.last_text = page.get()

    def remove_cats_and_comments(self, text):
        """Remove categories, comments and trailing spaces from wikitext."""
        text = textlib.removeCategoryLinks(text, site=self.site)
        text = textlib.removeDisabledParts(text, tags=['comments'])
        return text.strip()

    def has_only_one_revision(self):
        """Check if there is only one revision of the page."""
        rev_count = len(self.page.getVersionHistory())
        return (rev_count == 1)

    def content_not_changed(self):
        """Check if generated content is identical."""
        return (self.first_text == self.new_text)

    def only_cats_differ(self):
        """Check if only difference is in categories."""
        first_text = self.remove_cats_and_comments(self.first_text)
        last_text = self.remove_cats_and_comments(self.last_text)
        return (first_text == last_text)

    def get_final_categories(self):
        """
        Return final categories to keep.

        We keep any categories added after the first revision
        plus any categories in the new text which were not also
        present in the first revision and later removed.
        :return: list of pywikibot.Category
        """
        first_cats = set(textlib.getCategoryLinks(self.first_text, self.site))
        # can't use page.categories() since some cats are embedded by templates
        last_cats = set(textlib.getCategoryLinks(self.last_text, self.site))
        new_cats = set(textlib.getCategoryLinks(self.new_text, self.site))

        cats = ((new_cats - (first_cats - last_cats)) |
                (last_cats - first_cats))
        return list(cats)

    def handle_single_page(self):
        """
        Determine action to perform on page.

        Effectively this is done by setting self.text if an update is
        needed/possible.
        @todo: handle Unresolved better

        :return: String describing action
        """
        log_entry = None
        # determine action
        if self.content_not_changed():
            return "No change from original"  # no need to do an update
        elif self.has_only_one_revision():
            self.text = self.new_text  # just replace contents
            return "One revision"
        elif self.only_cats_differ():
            log_entry = "Only categories"
            final_cats = self.get_final_categories()
            # replace cats in new_text with final cats
            self.text = "{text}\n\n{catgories}".format(
                text=self.remove_cats_and_comments(self.new_text),
                catgories=textlib.categoryFormat(final_cats))
        else:
            # This will also catch any already updated pages
            log_entry = "Unresolved"
            pass  # don't know what to do

        if self.text and self.text == self.page.text or \
                self.new_text == self.page.text:
            # Either by coincidence or due to a previous run
            self.text = None
            return "No change from final version"
        else:
            return log_entry

    def update_page(self):
        """
        Upload final description to file page.

        :return: bool indicating success
        """
        if not self.text:
            pywikibot.output('No update needed for {:s}'
                             .format(self.page.title()))
            return False

        if self.dry:
            pywikibot.output(
                "Would have updated {title:s} with:\n{text}".format(
                    title=self.page.title(),
                    text=self.text))
            return True
        else:
            try:
                self.page.text = self.text
                self.page.save(summary=self.summary, minor=self.minor)
                pywikibot.output('Updated {:s}'.format(self.page.title()))
                return True
            except pywikibot.PageSaveRelatedError as e:
                pywikibot.output(
                    'Failed to updated {titel:s} due to {error:s}'.format(
                        title=self.page.title(),
                        error=e))
                return False


def process_info_blob(info, site, log, summary, dry, cutoff=None):
    """
    Process each image in an info blob.

    :param info: output of make_info
    :param site: the pywikibot.Site corresponding to the image repository
    :param log: the log function to use
    :param summary: the edit summary to use
    :param dry: if this is a dry run
    :param cutoff: Number of images to process before terminating. If None,
        assume all.
    """
    # @TODO: Check that File: is not already included in filename
    pywikibot.output('Processing {} images.'.format(len(info)))
    counter = 0
    for orig_name, image_data in info.items():
        if cutoff and cutoff <= counter:
            pywikibot.output('Reached cutoff.')
            return
        title = "File:{:s}".format(image_data['filename'])
        page = pywikibot.Page(site, title)
        new_text = make_info_page(image_data)
        updated_page = UpdatedPage(page, new_text, dry_run=dry,
                                   summary=summary)
        log_entry = updated_page.handle_single_page()
        if updated_page.update_page():
            log_entry = "Updated | {}".format(log_entry)
        else:
            log_entry = "Skipped | {}".format(log_entry)
        log("{title:s} | {log:s}\n".format(
            title=page.title(),
            log=log_entry))
        counter += 1


def load_and_dump_LSH_info(batch, data_dir=None, connections_dir=None):
    """
    Construct and return an info_blob for LSH data.

    :param batch: The category added to all files of the format
        "Category:Media contributed by LSH: <batch>".
    :param data_dir: override the default directory for data files
    :param connections_dir: override the default directory for connection
        files
    """
    data_dir = data_dir or DATA_DIR
    connections_dir = connections_dir or CONNECTIONS_DIR
    base_meta_cat = 'Media contributed by LSH'

    maker = MakeInfo()
    maker.readInLibraries(folder=data_dir)
    maker.readConnections(folder=connections_dir)
    batch_cat = '{:s}: {:s}'.format(base_meta_cat, batch)
    data = maker.dump_info(base_meta_cat, use_commons_name=True)

    # Add batch category which was added at upload
    for orig_names, image in data.items():
        image['meta_cats'].append(batch_cat)
    return data


def run(batch, log_file, summary, dry=True, cutoff=None):
    """
    Process every image in the LSH filenames file.

    :param batch: The category added to all files of the format
        "Category:Media contributed by LSH: <batch>".
    :param log_file: Path to log file
    :param summary: the edit summary to use
    :param dry: A simulated run
    :param cutoff: Number of images to process before terminating. If None,
        assume all.
    """
    data = load_and_dump_LSH_info(batch)
    with open(log_file, 'a', encoding='utf-8') as f:
        commons = pywikibot.Site('commons', 'commons')
        process_info_blob(data, commons, f.write, summary, dry, cutoff)

    pywikibot.output('Result available in: {:s}'.format(log_file))


def tmp_test():
    """Temporary testing function."""
    commons = pywikibot.Site('commons', 'commons')
    info = 'BLA'
    filename = 'Japansk tekopp från 1700-talet - Skoklosters slott - 93278.tif'  # noqa E501
    cats = ['hej']
    data = {'info': info, 'filename': filename, 'cats': cats, 'meta_cats': []}
    process_info_blob({'one': data}, commons, pywikibot.output, None, True)


def skipped_info(batch, skipped, view="last-new"):
    """
    Provide information/diffs for a list of skipped files.

    :param batch: The category added to all files of the format
        "Category:Media contributed by LSH: <batch>".
    :param skipped: list of skipped Commons filenames (incl. namespace).
    :param view: the diff view which you want. Allows last-new,
        first-last, first-new with last-new as default.
    """
    allowed_views = ('last-new', 'first-last', 'first-new')
    if view not in allowed_views:
        pywikibot.output("view must be one of the allowed_views: {}".format(
                         ', '.join(allowed_views)))
    data = load_and_dump_LSH_info(batch)
    site = pywikibot.Site('commons', 'commons')
    for orig_name, image_data in data.items():
        title = "File:{:s}".format(image_data['filename'])
        if title not in skipped:
            continue
        page = pywikibot.Page(site, title)
        last_text = page.get()
        new_text = make_info_page(image_data)
        first_text = page.getOldVersion(page.oldest_revision.revid)
        if view == 'last-new':
            print_diff(last_text, new_text)
        elif view == 'first-last':
            print_diff(first_text, last_text)
        elif view == 'first-new':
            print_diff(first_text, new_text)
        raw_input(u"Press enter for next.")


def print_diff(text_1, text_2):
    """Visualize the diff between two wikitexts."""
    patch = pywikibot.diff.PatchManager(text_1, text_2)
    patch.print_hunks()


def handle_args(*args):
    """
    Parse and load all of the basic arguments.

    Also passes any needed arguments on to pywikibot and sets any defaults.

    :param args: arguments to be handled
    :return: list of options
    """
    usage = ('Usage:\tpython maintanance/replace_description.py '
             '-batch:STRING -summary:STRING -log_file:<PATH> -live '
             '-cutoff:NUM\n'
             '\tbatch: the batch to simulate e.g. "2014-11"\n'
             '\tsummary: [optional] edit summary to use'
             '\tlog_file: [optional] path to the log_file to use, defaults to '
             '¤replace_description.log.\n'
             '\tlive: [optional] to do actual edits on Commons, defaults to'
             ' False.\n'
             '\tcutoff: [optional] Number of files to process before '
             'terminating, defaults to all.')
    options = {
        'batch': None,
        'summary': 'updating based on new data from #LSH',
        'log_file': '¤replace_description.log',
        'dry': True,
        'cutoff': None}

    for arg in pywikibot.handle_args(args):
        option, sep, value = arg.partition(':')
        if option == '-batch':
            options['batch'] = value
        elif option == '-summary':
            options['summary'] = value
        elif option == '-log_file':
            options['log_file'] = value
        elif option == '-live':
            options['dry'] = False
        elif option == '-cutoff':
            options['cutoff'] = int(value)

    if not options.get('batch'):
        pywikibot.error(usage)
        exit()

    return options


if __name__ == '__main__':
    options = handle_args()
    run(**options)
