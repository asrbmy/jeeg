# Reference: Files, folders, backups and the clipboard

Finding, organising, renaming and cleaning files; folders; backups; the clipboard; snippets; data files.

69 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [files](#files), [folders](#folders), [backup](#backup), [clipboard](#clipboard), [snippets](#snippets), [data](#data), [security](#security)

## files

### backup folder

**Usage:** `backup folder <folder>`  
**What it does:** Zip a folder into ~/Backups with a timestamp (backup folder documents)  
**Also found by:** `backup`, `back up`, `backup files`, `save copy`, `make backup`, `archive folder`  
**Script:** `scripts/backup_folder.py`

### bulk rename

**Usage:** `bulk rename <folder> replace <old> with <new>`  
**What it does:** Rename many files at once, with a preview first (bulk rename downloads replace img with photo)  
**Also found by:** `batch rename`, `rename files`, `rename all files`, `mass rename`, `rename many files`, `add prefix`, `add suffix`, `number files`  
**Your words:** passed through untouched  
**Script:** `scripts/bulk_rename.py`

### clean temp files

**Usage:** `clean temp files [preview]`  
**What it does:** Delete temporary files older than 24 hours (clean temp files preview shows what would go)  
**Behaviour:** asks before running.  
**Also found by:** `clean`, `cleanup`, `temp`, `temporary`, `junk`, `temp files`, `free space`, `clear cache`, `delete temp`, `clean up pc`  
**Script:** `scripts/clean_temp_files.py`

### compare files

**Usage:** `compare files <a> <b>`  
**What it does:** Compare two files: same or different, and what changed (compare files a.txt b.txt)  
**Also found by:** `diff files`, `file difference`, `are these files the same`, `compare two files`, `what changed between files`, `same file`  
**Your words:** passed through untouched  
**Script:** `scripts/compare_files.py`

### compare folders

**Usage:** `compare folders <a> <b>`  
**What it does:** Compare two folders: what is only in one, and what differs (compare folders a b)  
**Also found by:** `diff folders`, `folder difference`, `compare directories`, `are folders the same`, `sync check`, `folder compare`, `what is different between folders`  
**Your words:** passed through untouched  
**Script:** `scripts/compare_folders.py`

### contact sheet

**Usage:** `contact sheet <folder>`  
**What it does:** Make one picture with small thumbnails of every photo in a folder (contact sheet <folder>). Needs Pillow.  
**Also found by:** `photo grid`, `thumbnail sheet`, `photo overview`, `picture overview`, `thumbnails of folder`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/contact_sheet.py`

### convert encoding

**Usage:** `convert encoding <file>`  
**What it does:** Fix garbled text by saving a file as UTF-8 (convert encoding old.txt)  
**Also found by:** `fix encoding`, `utf-8 convert`, `garbled text`, `weird characters`, `text encoding`, `change encoding`, `save as utf8`, `fix strange characters`  
**Your words:** passed through untouched  
**Script:** `scripts/convert_encoding.py`

### copy file

**Usage:** `copy file <file> to <folder>`  
**What it does:** Copy a file or folder (copy file report.pdf to desktop)  
**Also found by:** `copy folder`, `duplicate file`, `copy to`, `copy document`, `make a copy of`, `clone file`  
**Your words:** passed through untouched  
**Script:** `scripts/copy_file.py`

### copy path

**Usage:** `copy path of <file>`  
**What it does:** Copy a file or folder's full path to the clipboard (copy path of report.pdf)  
**Also found by:** `copy file path`, `full path`, `path of file`, `copy folder path`, `get path`, `copy location`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/copy_path.py`

### create folder

**Usage:** `create folder <name>`  
**What it does:** Create a new folder on your Desktop (create folder projects)  
**Also found by:** `new folder`, `make folder`, `make directory`, `mkdir`, `new directory`, `add folder`  
**Script:** `scripts/create_folder.py`

### csv chart

**Usage:** `chart csv <file.csv>`  
**What it does:** Make a bar chart (HTML page) from a CSV: first text column vs first number column (chart csv sales.csv).  
**Also found by:** `chart csv`, `graph csv`, `plot csv`, `bar chart csv`, `chart from csv`, `csv graph`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/csv_chart.py`

### csv to json

**Usage:** `csv to json <file.csv>`  
**What it does:** Convert a CSV file to JSON (csv to json sales.csv). Writes a new .json next to it.  
**Also found by:** `convert csv`, `csv json`, `csv into json`, `csv file to json`, `turn csv into json`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/csv_to_json.py`

### delete empty folders

**Usage:** `delete empty folders <folder>`  
**What it does:** Remove empty folders inside a folder (add 'preview' to just list them)  
**Behaviour:** asks before running.  
**Also found by:** `empty folders`, `remove empty folders`, `delete empty directories`, `clean empty folders`, `empty directories`, `remove empty dirs`  
**Your words:** passed through untouched  
**Script:** `scripts/delete_empty_folders.py`

### delete old downloads

**Usage:** `delete old downloads [days]`  
**What it does:** Move old files from Downloads to a safe holding folder (delete old downloads 90 days)  
**Behaviour:** asks before running.  
**Also found by:** `old downloads`, `clean old downloads`, `clear downloads older than`, `remove old downloads`, `downloads older than`  
**Your words:** passed through untouched  
**Script:** `scripts/delete_old_downloads.py`

### empty trash

**Usage:** `empty trash [preview]`  
**What it does:** Empty the Recycle Bin / Trash permanently (empty trash preview only looks)  
**Behaviour:** asks before running.  
**Also found by:** `empty recycle bin`, `clear trash`, `clear recycle bin`, `delete trash`, `empty bin`, `purge trash`  
**Script:** `scripts/empty_trash.py`

### file types

**Usage:** `file types in <folder>`  
**What it does:** Count files by type in a folder (file types in downloads)  
**Also found by:** `file extensions`, `what kinds of files`, `extensions in folder`, `types of files`, `count files by type`, `breakdown of files`  
**Script:** `scripts/file_types.py`

### find duplicates

**Usage:** `find duplicates [folder]`  
**What it does:** Find duplicate files in a folder (read-only report)  
**Also found by:** `duplicates`, `duplicate files`, `same files`, `copies`, `identical files`, `repeated files`, `dedupe`  
**Script:** `scripts/find_duplicates.py`

### find file

**Usage:** `find file <name words>`  
**What it does:** Find files by name under your home folder (find file invoice pdf)  
**Also found by:** `search file`, `locate`, `where is`, `find document`, `find my`, `look for file`, `file search`  
**Script:** `scripts/find_file.py`

### find text

**Usage:** `find text <words> in <folder>`  
**What it does:** Search inside text files for a phrase (find text invoice in documents)  
**Also found by:** `search in files`, `grep`, `find in files`, `search inside files`, `text in files`, `search contents`, `which file contains`, `files containing`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/find_text.py`

### folder size

**Usage:** `folder size [folder]`  
**What it does:** Show how big a folder is (folder size downloads)  
**Also found by:** `size of`, `how big`, `directory size`, `space used by`, `how much space`, `du`, `size of folder`  
**Script:** `scripts/folder_size.py`

### folder tree

**Usage:** `folder tree [folder] [depth n]`  
**What it does:** Show a folder as a tree (folder tree documents, tree depth 3)  
**Also found by:** `tree`, `directory tree`, `show tree`, `folder structure`, `directory structure`, `list folder contents`, `show structure`  
**Your words:** passed through untouched  
**Script:** `scripts/folder_tree.py`

### index folder

**Usage:** `index folder <folder> | index status | index update | index remove <folder>`  
**What it does:** Build a searchable index of a folder's text files, notes and Word documents (index folder docs; index status; index update; index remove docs). Nothing leaves your computer.  
**Also found by:** `build index`, `search index build`, `index my files`, `index documents`, `index status`, `update index`, `remove index`, `full text index`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/index_folder.py`

### index lookup

**Usage:** `search index <words>`  
**What it does:** Search the text inside your indexed files, best matches first, with a snippet (search index invoice march).  
**Also found by:** `indexed files`, `fulltext`, `full text search`, `inside files`, `file contents lookup`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/index_lookup.py`

### large files

**Usage:** `large files [folder]`  
**What it does:** Find the biggest files (large files downloads)  
**Also found by:** `biggest files`, `big files`, `space hogs`, `what is using space`, `largest`, `huge files`, `free up space`  
**Script:** `scripts/large_files.py`

### large folders

**Usage:** `large folders [folder]`  
**What it does:** Show which sub-folders take the most space (large folders downloads)  
**Also found by:** `biggest folders`, `what is taking space`, `disk usage by folder`, `space hogs`, `which folder is biggest`, `folder sizes`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/large_folders.py`

### move file

**Usage:** `move file <file> to <folder>`  
**What it does:** Move a file or folder (move file report.pdf to documents)  
**Also found by:** `move folder`, `move to`, `relocate file`, `move this file`, `move document`, `cut and paste file`  
**Your words:** passed through untouched  
**Script:** `scripts/move_file.py`

### open last download

**What it does:** Open the newest file in Downloads  
**Also found by:** `last download`, `latest download`, `newest download`, `most recent download`, `open latest file`, `recent download`, `just downloaded`  
**Script:** `scripts/open_last_download.py`

### organize downloads

**Usage:** `organize downloads [preview]`  
**What it does:** Sort loose files in Downloads into folders by type (add 'preview' to just look)  
**Behaviour:** asks before running.  
**Also found by:** `organize`, `organise`, `sort downloads`, `clean downloads`, `tidy downloads`, `arrange files`, `sort files`, `declutter`  
**Script:** `scripts/organize_downloads.py`

### pdf text

**Usage:** `pdf to text <file.pdf> [pages 2-4]`  
**What it does:** Pull the text out of a PDF into a .txt file (pdf to text report.pdf, pdf to text report.pdf pages 2-4; needs pip install pypdf)  
**Also found by:** `pdf to text`, `extract text from pdf`, `read pdf`, `text from pdf`, `convert pdf to text`, `pdf to txt`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/pdf_text.py`

### recent files

**What it does:** List recently changed files in Documents, Downloads and Desktop  
**Also found by:** `recent`, `latest files`, `recently modified`, `new files`, `what did i change`, `last edited`, `recently downloaded`  
**Script:** `scripts/recent_files.py`

### rename by pattern

**Usage:** `rename files in <folder> as <pattern> [apply]`  
**What it does:** Rename files with a pattern, preview first (rename files in downloads as trip_{n}.{ext}; placeholders {name} {date} {n} {ext}; add 'apply' to do it)  
**Also found by:** `rename pattern`, `rename as`, `rename with pattern`, `name template`, `rename using`, `pattern rename`, `rename files as`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/rename_by_pattern.py`

### rename photos by date

**Usage:** `rename photos by date <folder> [apply]`  
**What it does:** Rename photos to their date taken, e.g. 2026-10-21_143005.jpg (preview first; add 'apply')  
**Also found by:** `rename photos`, `photos by date`, `rename pictures by date`, `date photos`, `photo names`, `rename images by date`, `organise photos by date`, `exif rename`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/rename_photos_by_date.py`

### replace in files

**Usage:** `replace in files <folder> "old" with "new" [preview]`  
**What it does:** Find and replace text in all text files of a folder, with a backup (replace in files docs "old" with "new").  
**Behaviour:** asks before running.  
**Also found by:** `replace text in files`, `bulk replace text`, `change text in many files`, `replace word in files`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/replace_in_files.py`

### stale files

**Usage:** `old large files [size] [age] [folder]`  
**What it does:** Find big files you have not touched for a long time (old large files 100 mb 1 year in downloads)  
**Also found by:** `old files`, `free up space`, `files not used`, `unused files`, `space hogs`, `not touched`, `clean up space`, `unused big files`  
**Your words:** passed through untouched  
**Script:** `scripts/stale_files.py`

### strip exif

**Usage:** `strip exif <photo>`  
**What it does:** Remove hidden location and camera data from a photo (strip exif photo.jpg). Needs Pillow.  
**Also found by:** `exif`, `remove exif`, `remove metadata`, `photo metadata`, `remove location from photo`, `clean photo`, `privacy photo`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/strip_exif.py`

### undo files

**Usage:** `undo`  
**What it does:** Undo your last file move, rename or Downloads tidy (undo, undo move, undo rename)  
**Also found by:** `undo move`, `undo rename`, `undo file change`, `undo last move`, `undo organise`, `revert rename`  
**Script:** `scripts/undo_files.py`

### unzip file

**Usage:** `unzip file <archive>`  
**What it does:** Extract a .zip / .tar.gz safely (unzip file archive.zip)  
**Also found by:** `unzip`, `extract`, `unpack`, `decompress`, `extract zip`, `open zip`, `un zip`, `untar`  
**Script:** `scripts/unzip_file.py`

### watch folder

**Usage:** `watch folder <folder> move <types> to <folder>`  
**What it does:** Watch a folder and move new files of a type into another folder (watch folder downloads move pdf to Documents/PDF). Add 'once' to run a single pass.  
**Behaviour:** asks before running.  
**Also found by:** `folder watcher`, `auto move files`, `auto sort folder`, `monitor folder`, `move new files`, `watch downloads`, `automatic file mover`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/watch_folder.py`

### zip folder

**Usage:** `zip folder <folder>`  
**What it does:** Zip a folder next to itself (zip folder projects)  
**Also found by:** `zip`, `compress`, `compress folder`, `make zip`, `archive`, `pack`  
**Script:** `scripts/zip_folder.py`

### zip with password

**Usage:** `zip with password <file|folder>`  
**What it does:** Make a password-protected AES zip of a file or folder (the password is asked privately, not typed in the command)  
**Behaviour:** never saved in history.  
**Also found by:** `password protect zip`, `encrypted zip`, `lock zip`, `secure zip`, `encrypt files`, `zip and encrypt`, `password zip`  
**Your words:** passed through untouched  
**Script:** `scripts/zip_with_password.py`


## folders

### open desktop

**What it does:** Open the Desktop folder  
**Also found by:** `desktop folder`, `desktop files`  
**Script:** `scripts/open_desktop.py`

### open documents

**What it does:** Open the Documents folder  
**Also found by:** `documents folder`, `docs folder`, `my documents`  
**Script:** `scripts/open_documents.py`

### open downloads

**What it does:** Open the Downloads folder  
**Also found by:** `downloads`, `download folder`, `downloaded`  
**Script:** `scripts/open_downloads.py`

### open file explorer

**What it does:** Open the file manager at your home folder  
**Also found by:** `files`, `explorer`, `finder`, `file manager`, `home folder`, `my files`  
**Script:** `scripts/open_file_explorer.py`

### open music folder

**What it does:** Open the Music folder  
**Also found by:** `music folder`, `songs folder`, `audio files`  
**Script:** `scripts/open_music_folder.py`

### open pictures

**What it does:** Open the Pictures folder  
**Also found by:** `pictures`, `photos folder`, `images folder`, `gallery`  
**Script:** `scripts/open_pictures.py`

### open scripts folder

**What it does:** Open the folder holding these task scripts  
**Also found by:** `scripts folder`, `task folder`, `my scripts`, `tasks folder`, `add script`  
**Script:** `scripts/open_scripts_folder.py`

### open trash

**What it does:** Open the Recycle Bin / Trash  
**Also found by:** `recycle bin`, `trash`, `deleted files`, `bin`, `recycle`  
**Script:** `scripts/open_trash.py`

### open videos folder

**What it does:** Open the Videos folder  
**Also found by:** `videos folder`, `movies folder`, `video files`  
**Script:** `scripts/open_videos_folder.py`


## backup

### backup info

**What it does:** Show when your data was last backed up and how much data you have  
**Also found by:** `backup status`, `last backup`, `when did i back up`, `backup check`, `is my data backed up`, `data size`, `how much data`  
**Script:** `scripts/backup_info.py`

### export data

**Usage:** `export data [folder]`  
**What it does:** Back up all your JeeG data (to-dos, notes, expenses, journal...) into one zip file (export data)  
**Also found by:** `backup data`, `backup my data`, `save my data`, `export everything`, `back up jeeg`, `data backup`, `export backup`, `backup records`  
**Your words:** passed through untouched  
**Script:** `scripts/export_data.py`

### export records

**Usage:** `export records <expenses|journal|todos|habits|birthdays|notes>`  
**What it does:** Save one list as a CSV file for Excel (export records expenses | journal | todos | habits | birthdays | notes)  
**Also found by:** `export csv`, `export expenses`, `export journal`, `export todos`, `export habits`, `export notes`, `save as csv`, `download my records`, `records to excel`  
**Your words:** passed through untouched  
**Script:** `scripts/export_records.py`

### import data

**Usage:** `import data <backup.zip>`  
**What it does:** Restore your data from a backup zip made by 'export data' (current data is saved first)  
**Behaviour:** asks before running.  
**Also found by:** `restore data`, `restore backup`, `restore my data`, `import backup`, `load backup`, `recover data`  
**Your words:** passed through untouched  
**Script:** `scripts/import_data.py`


## clipboard

### clear clipboard

**What it does:** Clear the clipboard  
**Also found by:** `empty clipboard`, `wipe clipboard`, `erase clipboard`  
**Script:** `scripts/clear_clipboard.py`

### clipboard history

**Usage:** `clipboard history [number | clear | search <word>]`  
**What it does:** List saved clipboard items, find one by a word, or copy one back (clipboard history, search clipboard history invoice, clipboard history 2, clear clipboard history)  
**Behaviour:** never saved in history.  
**Also found by:** `search clipboard history`, `find in clipboard history`, `clip history`, `saved clipboard`, `past clipboard`, `earlier copies`, `copy history`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/clipboard_history.py`

### copy to clipboard

**Usage:** `copy to clipboard <text>`  
**What it does:** Copy text to the clipboard (copy hello world)  
**Behaviour:** reads piped text.  
**Also found by:** `copy`, `clipboard`, `copy text`, `put on clipboard`  
**Script:** `scripts/copy_to_clipboard.py`

### save clipboard

**Usage:** `save clipboard`  
**What it does:** Keep what is on the clipboard in your private clipboard history (save clipboard)  
**Behaviour:** never saved in history.  
**Also found by:** `keep clipboard`, `remember clipboard`, `store clipboard`, `clip save`, `snapshot clipboard`  
**Script:** `scripts/save_clipboard.py`

### show clipboard

**What it does:** Show what is on the clipboard  
**Also found by:** `paste`, `clipboard`, `what did i copy`, `read clipboard`, `clipboard contents`  
**Script:** `scripts/show_clipboard.py`

### speak text

**Usage:** `speak <text>`  
**What it does:** Read text aloud (speak hello there)  
**Behaviour:** reads piped text.  
**Also found by:** `speak`, `say`, `read aloud`, `tts`, `text to speech`, `talk`, `voice`, `read out`  
**Script:** `scripts/speak_text.py`


## snippets

### list snippets

**What it does:** List saved snippets  
**Also found by:** `show snippets`, `my snippets`, `saved snippets`, `snippet list`, `all snippets`  
**Script:** `scripts/list_snippets.py`

### paste snippet

**Usage:** `paste snippet <name>`  
**What it does:** Copy a saved snippet to the clipboard (paste snippet email)  
**Also found by:** `use snippet`, `get snippet`, `copy snippet`, `snippet`, `insert text`, `my snippet`  
**Your words:** passed through untouched  
**Script:** `scripts/paste_snippet.py`

### remove snippet

**Usage:** `remove snippet <name>`  
**What it does:** Delete a saved snippet  
**Also found by:** `delete snippet`, `forget snippet`, `erase snippet`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_snippet.py`

### save snippet

**Usage:** `save snippet <name> <text>`  
**What it does:** Save a reusable text snippet (save snippet email me@example.com)  
**Also found by:** `snippet`, `save text`, `remember text`, `store text`, `canned reply`, `template text`, `add snippet`  
**Your words:** passed through untouched  
**Script:** `scripts/save_snippet.py`


## data

### sensor log

**Usage:** `log reading <name> <value> [unit] | show readings <name> | readings chart <name> | alert when <name> above|below <n> | list readings`  
**What it does:** Keep a log of any measurement (log reading temperature 24.5 c), see stats and a chart (show readings temperature), and get alerted past a limit (alert when temperature above 30)  
**Also found by:** `sensor chart`, `measurement log`, `record temperature`, `alert when above`, `log sensor`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/sensor_log.py`

### sqlite query

**Usage:** `database tables <file.db> | query database <file.db> <select ...>`  
**What it does:** Look inside a SQLite database file, read-only (database tables shop.db, query database shop.db select * from sales limit 5)  
**Also found by:** `sqlite`, `query database`, `database tables`, `sql query`, `read database`, `open database`, `db file`, `select from`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/sqlite_query.py`


## security

### breach check

**Usage:** `breach check "<password>"`  
**What it does:** Check if a password has appeared in known data leaks (only a 5-character hash prefix is sent)  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `pwned`, `have i been pwned`, `password leaked`, `password breach`, `leaked password`, `was my password hacked`, `data breach password`, `check leaked password`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/breach_check.py`

### file hash

**Usage:** `file hash <file> [expected hash]`  
**What it does:** Show the SHA-256, SHA-1 and MD5 fingerprint of a file, to check a download (file hash setup.exe)  
**Also found by:** `checksum`, `sha256 of file`, `md5 of file`, `verify download`, `hash of file`, `file checksum`, `check file integrity`, `compute checksum`, `fingerprint of file`  
**Your words:** passed through untouched  
**Script:** `scripts/file_hash.py`

### password strength

**Usage:** `password strength "<password>"`  
**What it does:** Rate how strong a password is, privately (password strength "MyPass123")  
**Behaviour:** never saved in history.  
**Also found by:** `check password`, `how strong is my password`, `test password`, `rate password`, `is my password strong`, `password strong`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/password_strength.py`

### shred file

**Usage:** `shred file <file> [preview]`  
**What it does:** Overwrite a file with random data and delete it (cannot be undone)  
**Behaviour:** asks before running.  
**Also found by:** `secure delete`, `wipe file`, `permanently delete file`, `erase file`, `destroy file`, `shred`, `securely delete`  
**Your words:** passed through untouched  
**Script:** `scripts/shred_file.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
