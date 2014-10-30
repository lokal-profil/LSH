LSH
===
The redux branch is an attempt to cleanup the scripts and include the original steps needed to convert the original csv files to those required for the input

Assorted scripts used for LSH batch upload (http://commons.wikimedia.org/wiki/COM:LSH)


Requires [WikiApi](https://github.com/lokal-profil/ODOK/blob/master/tools/WikiApi.py)

WikiApi is based on PyCJWiki Version 1.31 (C) by [Smallman12q](https://en.wikipedia.org/wiki/User_talk:Smallman12q) GPL, see http://www.gnu.org/licenses/.

## Workflow
All of these should be run from the main code folder.
0. Run `python py_listscraper.py old_connections`  # To make a copy of the latest Commons mappings
1. Unpack the new csv files to the "original_csv" folder
3. Update CSV_FILES in "py_prepCSVData.py" to the new file names
4. Run `python py_prepCSVData.py`  # to populate a new "clean_csv" folder
5. Run `python py_analyseCSVData.py` and fix any errors, repeat until no actionable errors  # creates analysis-logg
6. Run `python py_crunchCSVData.py`  # to populate a new "data" folder
  * Note that this takes some time and that there are two prompts at the start
7. Run `python py_filenames.py`  # to generate the filenames
8. Run `python py_makeMappings.py`  # to create mappingtables for Commons
9. Upload the mapping tables to the right place
10. Do the actual mappings...

11. Run `python py_listscraper.py`  # to populate a new "connections" folder
  * Check differences in filenames manually...
12. Run `python py_prepUpload.py moveHits ../bilder` where ../bilder is the relative path to the main image folder  # moves the relevant files to base folders and adds extention to filenames
13. Run `python py_prepUpload.py makeAndRename ../bilder/m_a` etc. for each of the new image sub.folders  # creates info files and renames files
  * Check `¤generator.log` for possible problems
14. Run `python py_prepUpload.py negatives ../bilder/m_a` etc. for each of the image sub.folders containing negatives  # creates a positive version and renames correctly
  * Check `¤imageMagick-errors.log` for errorreports
15. Run `python py_prepUpload.py negativeCleanup ../bilder/m_a` etc. for each of the image sub.folders where 14. was run
  * Check `¤conversion-errors.log` for problematic conversions (fix manually)

16. Run `python py_Uploader.py ../bilder/m_a` etc. to upload the files
