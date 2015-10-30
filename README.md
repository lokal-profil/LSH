LSH
===
Assorted scripts used for [LSH batch upload](http://commons.wikimedia.org/wiki/COM:LSH).
The work originally done on the redux branch (now merged) was a first attempt to cleanup the scripts and
include the original steps needed to convert the original csv files to those required for the input

Apart from the exeptions mentioned below this was produced by [Lokal_Profil](https://github.com/lokal-profil).
Note however that the majority of the codebase is old and the coding might make you want to cry
(I know that is how I feel when I see it).

The SQL scripts were created by [Fredrik Andersson](http://lsh.se/sv/fredrik-andersson) at LSH.

Included is PyCJWiki Version 1.31 (C) by [Smallman12q](https://en.wikipedia.org/wiki/User_talk:Smallman12q) GPL,
see http://www.gnu.org/licenses/.

## TODO
* Change over from PyCJWiki to WikiApi...
* Make older bits not suck...

Requires [WikiApi](https://github.com/lokal-profil/ODOK/blob/master/tools/WikiApi.py)

WikiApi is based on PyCJWiki Version 1.31 (C) by [Smallman12q](https://en.wikipedia.org/wiki/User_talk:Smallman12q) GPL,
see http://www.gnu.org/licenses/.

## Workflow

All of these should be run from the main code directory. Note that up to
step 10 all can be done without the actual image files.

0. Copy config.py.sample to config.py and fill in your username and password
0. Run `python py_listscraper.py old_connections data`, to make a copy of
   the latest Commons mappings
1. Unpack the new csv files to the `original_csv` directory
3. Update `csv_config.json` to the new file names
4. Run `python py_prepCSVData.py`, to populate a new `clean_csv` directory
5. Run `python py_analyseCSVData.py` and fix any errors, repeat until no
   actionable errors
  * creates `csv_analys.log`
6. Run `python py_crunchCSVData.py`, to populate a new `data` directory
  * Note that this takes some time and that there are three prompts at
    the start
  * individual log files are found in `data/logs`
7. Run `python py_filenames.py`, to generate the filenames
8. Run `python py_makeMappings.py`, to create mapping tables for Commons
9. Upload the mapping tables to the right place
10. Do the actual mappings...

11. Run `python py_listscraper.py`, to populate a new `connections` directory
    and update filenames
  * If filenames are updated then don't run again until Commons table has
    been updated.
12. Run `python py_prepUpload.py moveHits ../bilder` where *`../bilder`*
    is the relative path to the main image directory. Moves the relevant
    files to base directories and adds extension to `filenames.csv`
13. Run `python py_prepUpload.py makeAndRename ../bilder/m_a batchCat` etc.
    for each of the new image subdirectory. Where *`batchCat`*, if provided
    is a datestamp (e.g. `2015-11`) used for collecting the images in a
    category. Creates info files and renames files
  * Check `¤generator.log` for possible problems
14. Run `python py_prepUpload.py negatives ../bilder/m_a` etc. for each
    of the image subdirectory containing negatives. Creates a positive
    version and renames correctly
  * Series with negatives are A, B, D, E, G, O
  * Check `¤imageMagick-errors.log` for error reports
15. Run `python py_prepUpload.py negativeCleanup ../bilder/m_a` etc. for
    each of the image subdirectory where the previous step was run
  * Check `¤conversion-errors.log` for problematic conversions (fix manually)
16. Run `python py_Uploader.py ../bilder/m_a` etc. to upload the files
  * Successful uploads end up in the `Uploaded` subdirectory
  * Failed uploads in the `Uploaded_errors` subdirectory
  * Uploads with warnings in the `Uploaded_warnings` subdirectory
  * Details on problematic uploads can be found in `¤uploader.log`
    (fix manually, often by just trying again...)

## Post upload
1. Run `python py_postUpload.py purge` to purge LSH-files in [Category:Files with broken file links](https://commons.wikimedia.org/wiki/Category:Files_with_broken_file_links)
2. Look at `BrokenFileLinks.csv` to identify any remaining files with
   broken file links. Add any known renames after the pipe (excluding
   prefix and file extension)
3. Run `python py_postUpload.py rename` to repair file pages linking to
   renamed files
4. Run `python py_postUpload.py updateBroken` to find any remaining files
   with broken links
  * These indicate missing files, these can some times be uploaded manually
5. Run `python py_postUpload.py findMissing` to check filenames.csv for
   any files not present on Commons
  * This also generates an export file with photoid to url links for LSH
