# Task Catalog

Every task in JeeG, by category (602 tasks). Generated from the real task list; do not edit by hand (`python tools/make_wiki.py`).

In **Usage**, `<...>` is something you fill in and `[...]` is optional. A star `*` means the task asks before running; *online* means it can use the internet. For more detail on each task (flags, other wording that finds it, script file) see the reference pages: [Money and business](Reference-Money-and-Business), [Files, folders, backups and the clipboard](Reference-Files-and-Folders), [System, power, hardware and home](Reference-System-and-Hardware), [Network, web, search and travel](Reference-Network-Web-and-Search), [Developer tools](Reference-Developer-Tools), [Apps, launchers and linked apps](Reference-Apps-and-Launchers), [Time, reminders and personal records](Reference-Time-Reminders-and-Records), [Health, study, media and fun](Reference-Health-Study-and-Fun). In the terminal, `list <category>` shows the same, and `explain <words>` shows how a phrase would be matched.

## Categories

[ai (7)](#ai) | [apps (29)](#apps) | [apps_setup (2)](#apps-setup) | [apps_write (1)](#apps-write) | [backup (5)](#backup) | [birthdays (3)](#birthdays) | [browser (3)](#browser) | [clipboard (7)](#clipboard) | [data (2)](#data) | [developer (68)](#developer) | [email (6)](#email) | [entertainment (12)](#entertainment) | [files (40)](#files) | [folders (9)](#folders) | [food (2)](#food) | [fun (5)](#fun) | [habits (2)](#habits) | [hardware (14)](#hardware) | [health (13)](#health) | [home (6)](#home) | [info (12)](#info) | [journal (3)](#journal) | [learning (5)](#learning) | [links (4)](#links) | [lists (8)](#lists) | [maps (4)](#maps) | [media (14)](#media) | [money (53)](#money) | [network (41)](#network) | [notes (6)](#notes) | [personal (1)](#personal) | [power (7)](#power) | [productivity (12)](#productivity) | [reference (1)](#reference) | [reminders (14)](#reminders) | [routines (11)](#routines) | [search (8)](#search) | [security (9)](#security) | [selfcheck (1)](#selfcheck) | [shopping (3)](#shopping) | [snippets (4)](#snippets) | [social (16)](#social) | [study (12)](#study) | [system (31)](#system) | [text (16)](#text) | [time (13)](#time) | [tools (4)](#tools) | [travel (7)](#travel) | [utility (18)](#utility) | [web (2)](#web) | [work (2)](#work) | [workspace (24)](#workspace)

## ai

| Task | Usage | What it does |
|---|---|---|
| agent *(online)* | `agent goal <goal> careful (checks its own answer) \| agent stats \| agent setup [backup] \| agent goal <what you want> [read\|ask\|safe] [steps 8] [for 10 minutes] [plan first] \| agent plan <goal> \| agent last \| agent history \| agent again <n> \| agent audit \| agent template list\|run <name> \| agent schedule add\|list\|run\|on\|off\|remove \| agent limit <calls> \| agent status \| agent test \| agent forget` | Give JeeG a goal and a model you chose (Ollama, LM Studio, or your own Claude/ChatGPT/DeepSeek key) plans the steps; JeeG runs them and asks you before anything risky. agent setup \| goal \| plan \| last \| history \| again \| audit \| template \| schedule \| limit \| status \| forget |
| open chatgpt |  | Open ChatGPT |
| open claude |  | Open Claude |
| open gemini |  | Open Google Gemini |
| open perplexity | `open perplexity <words>` | Open Perplexity (or ask it) |
| remember | `remember <fact> [for 30 days] \| remember review \| remember list \| remember search <words> \| remember forget <number\|all>` | Tell JeeG facts or preferences to remember on this computer (remember I prefer metric units); the agent uses them. remember list \| remember search <words> \| remember forget <number\|all>. Never keeps passwords. |
| skill | `skill pack list\|show\|install <pack> \| skill improve <name> \| skill undo <name> \| skill add <name> = <step> ; <step> \| skill run <name> [read\|ask\|safe] \| skill list \| skill show <name> \| skill describe <name> = <text> \| skill remove <name> \| skill export <name> \| skill import <file>` | Save a list of plain-words steps as a skill and run it any time (skill add morning = show reminders ; what is due). The agent can use your skills. skill add \| run \| list \| show \| remove \| describe \| share |

## apps

| Task | Usage | What it does |
|---|---|---|
| linked apps | `apps \| apps <name>` | List the apps JeeG is linked to (GitHub, Telegram, Discord, Slack, WhatsApp, your own) and what each one can do. "apps github" shows one app's actions. |
| linked read *(online)* | `app read <app> <action> [arguments]` | Look at something in a linked app without changing it (app read github issues, app read github repo_issues owner/name). Nothing is ever sent or changed. |
| mcp look *(online)* | `mcp look <name> <tool> [json arguments]` | Use a read-only tool of a saved MCP server (mcp look files read_file {"path": "notes.txt"}). Only tools you marked as read run; nothing is changed. |
| open app | `open app <name>` | Open any installed app by name (open app <name>) |
| open bluetooth settings |  | Open Bluetooth settings |
| open brave |  | Open Brave browser |
| open calculator |  | Open the calculator |
| open camera |  | Open the camera |
| open chrome |  | Open Google Chrome |
| open clock |  | Open the Clock / alarms app |
| open control panel |  | Open the classic Control Panel |
| open device manager |  | Open Device Manager |
| open edge |  | Open Microsoft Edge |
| open excel |  | Open Microsoft Excel / a spreadsheet app |
| open firefox |  | Open Firefox |
| open incognito |  | Open a private / incognito browser window |
| open notepad |  | Open a simple text editor |
| open paint |  | Open Paint / an image editor |
| open powerpoint |  | Open PowerPoint / a presentation app |
| open powershell |  | Open PowerShell |
| open resource monitor |  | Open Resource Monitor |
| open settings |  | Open system Settings |
| open snipping tool |  | Open the snipping / screenshot tool |
| open taskmanager |  | Open Task Manager / system monitor |
| open terminal |  | Open a terminal / command prompt |
| open vlc |  | Open VLC media player |
| open vscode |  | Open Visual Studio Code |
| open wifi settings |  | Open Wi-Fi settings |
| open word |  | Open Microsoft Word / a word processor |

## apps_setup

| Task | Usage | What it does |
|---|---|---|
| event rules *(online)* | `rule add <name> when <app> <read-action> [args] changes [every N minutes] then <task words> \| rules list \| rule remove <name> \| rules run once \| rules run` | Run a task when something new shows up in a linked app: rule add issues when github issues changes then say new issue {new}. Lists, removes and runs rules (rules run once \| rules run). Terminal only. |
| linked setup *(online)* | `app login <app> [device client_id=...] \| app preset list\|add <name> [base=...] \| app keystore on\|off \| app ai allow\|deny <app> \| app ai list\|reset\|dry on\|off \| app logout <app> \| app add <name> <https://base> [none\|bearer\|basic\|header:NAME\|query:NAME] \| app add <name> command \| app action <app> <name> <GET\|POST\|...> </path> [params=a,b] [format="{x}"] [list=path] [body='{"k":"{a}"}'] [desc="..."] \| app remove <name>` | Link JeeG to an app: log in (app login github), add your own app by its web address (app add trello https://api.trello.com/1 query:key), define what it can do (app action ...), log out or remove, use ready-made presets, keep logins in the system keychain, choose which apps an AI may use. Terminal only: an AI cannot do this. |

## apps_write

| Task | Usage | What it does |
|---|---|---|
| linked do *(online)* \* | `app do <app> <action> [arguments] [preview]` | Do something in a linked app that changes things: comment on GitHub, send a Telegram, Discord or Slack message, open a WhatsApp chat (app do telegram send chat=123 hello). Always asks first; add "preview" to see the request without sending. |

## backup

| Task | Usage | What it does |
|---|---|---|
| backup info |  | Show when your data was last backed up and how much data you have |
| backup share *(online)* \* | `backup share <computer>` | Share a backup zip of your JeeG data to a paired computer over the encrypted link (backup share kitchen-pc). It arrives in their Downloads/JeeG received folder. Asks first. |
| export data | `export data [folder]` | Back up all your JeeG data (to-dos, notes, expenses, journal...) into one zip file (export data) |
| export records | `export records <expenses\|journal\|todos\|habits\|birthdays\|notes>` | Save one list as a CSV file for Excel (export records expenses \| journal \| todos \| habits \| birthdays \| notes) |
| import data \* | `import data <backup.zip>` | Restore your data from a backup zip made by 'export data' (current data is saved first) |

## birthdays

| Task | Usage | What it does |
|---|---|---|
| add birthday | `add birthday <name> <date>` | Save a birthday (add birthday mom 14 aug, add birthday raj 3 march 1999) |
| remove birthday | `remove birthday <name>` | Delete a saved birthday |
| upcoming birthdays |  | Show birthdays in the next 60 days |

## browser

| Task | Usage | What it does |
|---|---|---|
| browser do *(online)* \* | `browser click <number> \| browser type <number> <text> \| browser press <key> \| browser select <number> <option> \| browser flow run <name> \| browser type text <label> = <words> \| browser tick <number> \| browser hover <number> \| browser click text <words>  (add the word preview to only see what it would do)` | Act on a page in the real browser, by the numbers that  browser look  shows (browser click 4, browser type 2 hello, browser press enter, browser select 3 Red, browser tick 5). Asks first. |
| browser look *(online)* | `browser table [n] \| browser pdf \| browser watch <address> \| browser changes \| browser open <address> \| browser look \| browser read \| browser find <text> \| browser tabs \| browser tab <number> \| browser newtab [address] \| browser screenshot \| browser back \| browser forward \| browser scroll down\|up \| browser wait <seconds> \| browser wait for <text> \| browser status` | Look at websites in a real browser (browser open example.com, browser look, browser read, browser find price, browser tabs, browser screenshot, browser back). Nothing on the page is changed. |
| browser setup *(online)* | `browser start [hidden] \| browser close \| browser allow <site> \| browser deny <site> \| browser forget <site> \| browser policy \| browser secret <number> \| browser flow add <name> = <step> \| <step> \| browser flow list\|show\|remove <name> \| browser upload <number> <file>` | Set up the real browser (browser start, browser start hidden, browser close, browser allow example.com, browser deny example.com, browser policy, browser secret 3 to type a password yourself). You do this in a terminal. |

## clipboard

| Task | Usage | What it does |
|---|---|---|
| clear clipboard |  | Clear the clipboard |
| clipboard history | `clipboard history [number \| clear \| search <word>]` | List saved clipboard items, find one by a word, or copy one back (clipboard history, search clipboard history invoice, clipboard history 2, clear clipboard history) |
| copied text | `clipboard clean \| links \| csv \| sort \| count` | Work on what you copied (clipboard clean, clipboard links, clipboard csv, clipboard sort, clipboard count) |
| copy to clipboard | `copy to clipboard <text>` | Copy text to the clipboard (copy hello world) |
| save clipboard | `save clipboard` | Keep what is on the clipboard in your private clipboard history (save clipboard) |
| show clipboard |  | Show what is on the clipboard |
| speak text | `speak <text>` | Read text aloud (speak hello there) |

## data

| Task | Usage | What it does |
|---|---|---|
| sensor log | `log reading <name> <value> [unit] \| show readings <name> \| readings chart <name> \| alert when <name> above\|below <n> \| list readings` | Keep a log of any measurement (log reading temperature 24.5 c), see stats and a chart (show readings temperature), and get alerted past a limit (alert when temperature above 30) |
| sqlite query | `database tables <file.db> \| query database <file.db> <select ...>` | Look inside a SQLite database file, read-only (database tables shop.db, query database shop.db select * from sales limit 5) |

## developer

| Task | Usage | What it does |
|---|---|---|
| check versions |  | Show installed versions of Python, Node, Git, Docker, Java |
| color convert | `color <#hex \| rgb r g b \| hsl h s l>` | Convert colours between hex, RGB and HSL (color #ff8800; color rgb 255 136 0; color hsl 32 100 50) |
| configure app *(online)* \* | `configure git [name N] [email E] [branch B] \| configure ssh key \| configure vscode extension <id> \| configure python project` | Set up common tools: git name and email, an ssh key, a VS Code extension, a Python virtual environment (configure git name Ravi email r@x.com; add "preview" to see what would run) |
| count lines of code | `lines of code [folder]` | Count lines of code by language in a folder (lines of code myproject) |
| create gitignore | `create gitignore [python\|node\|java]` | Create or extend a .gitignore for a language (create gitignore python \| node \| java) |
| create venv |  | Create a Python virtual environment (.venv) here |
| cron explain | `cron <minute hour day month weekday>` | Explain a cron schedule in words (cron 30 9 * * 1-5) |
| csv preview | `csv preview <file.csv>` | Show the first rows of a CSV file as a table (csv preview data.csv) |
| csv summary | `csv summary <file.csv>` | Summarise a CSV: rows, columns, number totals and common values (csv summary data.csv) |
| docker ps |  | List running Docker containers |
| docker stop all \* |  | Stop all running Docker containers |
| env check | `env check [folder]` | Compare a .env file with .env.example and list missing keys, without showing secrets (env check; env check myapp) |
| env diff | `env diff <file1> <file2>` | Compare two .env files and show which keys are missing or different, without printing the values (env diff .env.example .env) |
| find todo | `find todo [folder]` | List TODO, FIXME and HACK comments in a project folder (find todo myproject) |
| git branch |  | List git branches |
| git checkout | `git checkout <branch> \| git checkout new <branch>` | Switch to a git branch, or create one (git switch main, git checkout new feature-x) |
| git clone *(online)* | `git clone <url>` | Clone a repository (git clone https://github.com/user/repo) |
| git commit \* | `git commit <message>` | Stage everything and commit (git commit fix login bug) |
| git contributors |  | Who has committed to this git project, and how much (git contributors) |
| git diff |  | Summarise uncommitted git changes |
| git log |  | Show the last 10 git commits |
| git pull *(online)* |  | Pull the latest changes (fast-forward only) |
| git push *(online)* \* |  | Push commits to the remote |
| git recent changes | `git recent changes [days]` | What changed in this git project recently (git recent changes, git recent changes 14 days) |
| git stash | `git stash [pop\|list\|save <note>]` | Stash or restore uncommitted changes (git stash, git stash pop, git stash list) |
| git status |  | Show git status of the current folder |
| git undo commit \* |  | Undo the last commit but keep your changes (git undo last commit) |
| github inbox *(online)* | `github login \| github inbox \| github issues <owner/repo> \| github forget` | See your GitHub notifications or a repo's open issues (github login, github inbox, github issues owner/repo). Token asked privately. |
| http get *(online)* | `http get <url>` | Fetch a URL and show status, headers and the start of the body (http get https://example.com) |
| json diff | `json diff <old.json> <new.json>` | Compare two JSON files and list what changed (json diff a.json b.json) |
| json minify | `json minify <file.json>` | Shrink a JSON file onto one line (json minify data.json) |
| json to csv | `json to csv <file.json>` | Convert a JSON file (a list of records) to CSV (json to csv data.json) |
| json to yaml | `json to yaml <file.json>` | Convert a JSON file to YAML (json to yaml config.json) |
| jwt decode | `jwt <token>` | Read what is inside a JWT token, without sending it anywhere (jwt eyJ...) |
| kill port \* | `kill port <number>` | Stop whatever is listening on a port (kill port 3000) |
| log analyze | `log analyze <file>` | Summarise a log file: counts by level, the most common errors, and the busiest minutes (log analyze app.log) |
| mcp call *(online)* \* | `mcp call <name> <tool> [json arguments] [preview]` | Use any tool of a saved MCP server (mcp call files write_file {"path": "a.txt", "content": "hi"}). Asks first. Add the word preview to see what would be sent. |
| mcp servers *(online)* | `mcp catalog \| mcp add <catalog name> [argument] \| mcp add <name> = <command or https address> \| mcp list \| mcp tools <name> \| mcp login <name> [ENV_VAR ...] \| mcp logout <name> \| mcp mark <name> <tool,tool> read\|write \| mcp remove <name>` | Let JeeG use other MCP servers (mcp catalog, mcp add filesystem ~/Documents, mcp add files = npx some-server, mcp login <name>, mcp tools <name>, mcp mark <name> <tool> read) |
| new project | `new project <name> [python\|node\|html\|flask]` | Create a starter project folder (new project myapp python \| node \| html \| flask) |
| open codepen |  | Open CodePen |
| open dockerhub | `open dockerhub <words>` | Open Docker Hub |
| open github | `open github <words>` | Open GitHub or search it |
| open gitlab |  | Open GitLab |
| open huggingface | `open huggingface <words>` | Open Hugging Face |
| open kaggle | `open kaggle <words>` | Open Kaggle |
| open leetcode | `open leetcode <words>` | Open LeetCode |
| open localhost | `open localhost [port]` | Open http://localhost:<port> in the browser |
| open mdn | `open mdn <words>` | Open MDN Web Docs or search it |
| open npm | `open npm <words>` | Open npm or search Node packages |
| open pypi | `open pypi <words>` | Open PyPI or search Python packages |
| open stackoverflow | `open stackoverflow <words>` | Open Stack Overflow or search it |
| open vscode here |  | Open the current folder in VS Code |
| open w3schools |  | Open W3Schools |
| pip install *(online)* \* | `pip install <packages>` | Install Python packages (pip install requests) |
| pip list |  | List installed Python packages |
| pip outdated *(online)* |  | List Python packages that have updates |
| regex explain | `regex explain <pattern>` | Explain a regular expression in plain words (regex explain ^\d{3}-\w+$) |
| regex tester | `regex test "<pattern>" on "<text>"` | Try a regular expression on some text and see the matches (regex test "\d+" on "abc 123 def 45") |
| response headers *(online)* | `http headers <url>` | Show a website's response headers and which security headers it sets (http headers https://example.com) (needs internet) |
| run tests |  | Run the tests of the project in this folder (run tests): pytest, unittest, npm, go or cargo is detected |
| semver compare | `semver <version> vs <version>` | Compare two version numbers the way package managers do (semver 1.2.3 vs 1.10.0) |
| serve folder *(online)* | `serve folder [port]` | Serve the current folder at http://localhost:8000 |
| show env variables | `env variables [filter]` | List environment variables (secrets hidden); add a word to filter (env variables java) |
| show path |  | Show the folders in your PATH, one per line, marking missing ones |
| text diff | `text diff <file1> <file2>` | Show the differences between two text files (text diff a.txt b.txt) |
| toml to json | `toml to json <file>` | Convert a TOML file (such as pyproject.toml) to JSON (toml to json pyproject.toml). Needs Python 3.11 or newer. |
| verify checksum | `verify checksum <file> <checksum>` | Check a file against a checksum you were given (verify checksum setup.exe 9f86d0...) |
| yaml to json | `yaml to json <file.yaml>` | Convert a YAML file to JSON (yaml to json config.yaml) |

## email

| Task | Usage | What it does |
|---|---|---|
| compose email | `compose email <words>` | Compose a Gmail message (words become the subject) |
| email to | `email <contact\|address> [about <subject>]` | Start an email to a saved contact or address (email mom about dinner) |
| mail inbox *(online)* | `mail inbox [how many]` | Show your unread mail (sender, subject, date). Reads only the headers and marks nothing as read. Needs  mail setup. |
| mailbox post *(online)* \* | `mail send <to> \| <subject> \| <body>` | Send a mail from your saved account (mail send bob@example.com \| Subject \| Body). It asks first. Needs  mail setup. |
| mailbox setup *(online)* | `mail setup <address> <imap host> <smtp host> \| mail status \| mail forget` | Save your mail account for mail tasks (mail setup you@gmail.com imap.gmail.com smtp.gmail.com). Uses an app password, asked privately. |
| open gmail |  | Open Gmail |

## entertainment

| Task | Usage | What it does |
|---|---|---|
| movie info | `movie info <title>` | Look up a movie or show on IMDb (movie info inception) |
| open hotstar |  | Open JioHotstar |
| open jiosaavn | `open jiosaavn <words>` | Open JioSaavn music |
| open netflix | `open netflix <words>` | Open Netflix |
| open primevideo |  | Open Amazon Prime Video |
| open spotify | `open spotify <words>` | Open Spotify web player or search it |
| open twitch | `open twitch <words>` | Open Twitch |
| open youtube | `open youtube <words>` | Open YouTube or search it |
| open youtube music | `open youtube music <words>` | Open YouTube Music or search it |
| play song | `play <song name> [on spotify\|youtube]` | Play a song: searches YouTube Music (or 'on spotify' / 'on youtube'); plain 'play' toggles play/pause |
| recipe lookup | `recipe <dish>` | Find a recipe (recipe paneer butter masala) |
| song lyrics | `lyrics <song>` | Find the lyrics of a song (lyrics shape of you) |

## files

| Task | Usage | What it does |
|---|---|---|
| backup folder | `backup folder <folder>` | Zip a folder into ~/Backups with a timestamp (backup folder documents) |
| bulk rename | `bulk rename <folder> replace <old> with <new>` | Rename many files at once, with a preview first (bulk rename downloads replace img with photo) |
| clean temp files \* | `clean temp files [preview]` | Delete temporary files older than 24 hours (clean temp files preview shows what would go) |
| compare files | `compare files <a> <b>` | Compare two files: same or different, and what changed (compare files a.txt b.txt) |
| compare folders | `compare folders <a> <b>` | Compare two folders: what is only in one, and what differs (compare folders a b) |
| contact sheet | `contact sheet <folder>` | Make one picture with small thumbnails of every photo in a folder (contact sheet <folder>). Needs Pillow. |
| convert encoding | `convert encoding <file>` | Fix garbled text by saving a file as UTF-8 (convert encoding old.txt) |
| copy file | `copy file <file> to <folder>` | Copy a file or folder (copy file report.pdf to desktop) |
| copy path | `copy path of <file>` | Copy a file or folder's full path to the clipboard (copy path of report.pdf) |
| create folder | `create folder <name>` | Create a new folder on your Desktop (create folder projects) |
| csv chart | `chart csv <file.csv>` | Make a bar chart (HTML page) from a CSV: first text column vs first number column (chart csv sales.csv). |
| csv to json | `csv to json <file.csv>` | Convert a CSV file to JSON (csv to json sales.csv). Writes a new .json next to it. |
| delete empty folders \* | `delete empty folders <folder>` | Remove empty folders inside a folder (add 'preview' to just list them) |
| delete old downloads \* | `delete old downloads [days]` | Move old files from Downloads to a safe holding folder (delete old downloads 90 days) |
| empty trash \* | `empty trash [preview]` | Empty the Recycle Bin / Trash permanently (empty trash preview only looks) |
| file types | `file types in <folder>` | Count files by type in a folder (file types in downloads) |
| find duplicates | `find duplicates [folder]` | Find duplicate files in a folder (read-only report) |
| find file | `find file <name words>` | Find files by name under your home folder (find file invoice pdf) |
| find text | `find text <words> in <folder>` | Search inside text files for a phrase (find text invoice in documents) |
| folder size | `folder size [folder]` | Show how big a folder is (folder size downloads) |
| folder tree | `folder tree [folder] [depth n]` | Show a folder as a tree (folder tree documents, tree depth 3) |
| index folder | `index folder <folder> \| index status \| index update \| index remove <folder>` | Build a searchable index of a folder's text files, notes and Word documents (index folder docs; index status; index update; index remove docs). Nothing leaves your computer. |
| index lookup | `search index <words>` | Search the text inside your indexed files, best matches first, with a snippet (search index invoice march). |
| large files | `large files [folder]` | Find the biggest files (large files downloads) |
| large folders | `large folders [folder]` | Show which sub-folders take the most space (large folders downloads) |
| move file | `move file <file> to <folder>` | Move a file or folder (move file report.pdf to documents) |
| open last download |  | Open the newest file in Downloads |
| organize downloads \* | `organize downloads [preview]` | Sort loose files in Downloads into folders by type (add 'preview' to just look) |
| pdf text | `pdf to text <file.pdf> [pages 2-4]` | Pull the text out of a PDF into a .txt file (pdf to text report.pdf, pdf to text report.pdf pages 2-4; needs pip install pypdf) |
| recent files |  | List recently changed files in Documents, Downloads and Desktop |
| rename by pattern | `rename files in <folder> as <pattern> [apply]` | Rename files with a pattern, preview first (rename files in downloads as trip_{n}.{ext}; placeholders {name} {date} {n} {ext}; add 'apply' to do it) |
| rename photos by date | `rename photos by date <folder> [apply]` | Rename photos to their date taken, e.g. 2026-10-21_143005.jpg (preview first; add 'apply') |
| replace in files \* | `replace in files <folder> "old" with "new" [preview]` | Find and replace text in all text files of a folder, with a backup (replace in files docs "old" with "new"). |
| stale files | `old large files [size] [age] [folder]` | Find big files you have not touched for a long time (old large files 100 mb 1 year in downloads) |
| strip exif | `strip exif <photo>` | Remove hidden location and camera data from a photo (strip exif photo.jpg). Needs Pillow. |
| undo files | `undo` | Undo your last file move, rename or Downloads tidy (undo, undo move, undo rename) |
| unzip file | `unzip file <archive>` | Extract a .zip / .tar.gz safely (unzip file archive.zip) |
| watch folder \* | `watch folder <folder> move <types> to <folder>` | Watch a folder and move new files of a type into another folder (watch folder downloads move pdf to Documents/PDF). Add 'once' to run a single pass. |
| zip folder | `zip folder <folder>` | Zip a folder next to itself (zip folder projects) |
| zip with password | `zip with password <file\|folder>` | Make a password-protected AES zip of a file or folder (the password is asked privately, not typed in the command) |

## folders

| Task | Usage | What it does |
|---|---|---|
| open desktop |  | Open the Desktop folder |
| open documents |  | Open the Documents folder |
| open downloads |  | Open the Downloads folder |
| open file explorer |  | Open the file manager at your home folder |
| open music folder |  | Open the Music folder |
| open pictures |  | Open the Pictures folder |
| open scripts folder |  | Open the folder holding these task scripts |
| open trash |  | Open the Recycle Bin / Trash |
| open videos folder |  | Open the Videos folder |

## food

| Task | Usage | What it does |
|---|---|---|
| open swiggy |  | Open Swiggy |
| open zomato |  | Open Zomato |

## fun

| Task | Usage | What it does |
|---|---|---|
| guess number | `guess number [max]` | Play 'guess the number' (guess number, or guess number 1000) |
| multiplication table | `multiplication table <n> [up to <m>]` | Print a multiplication table (table of 7, multiplication table 12 up to 20) |
| quiz notes | `quiz notes [file]` | Quiz yourself from a notes file of 'question \| answer' lines (quiz notes myfile.txt) |
| rock paper scissors |  | Play rock paper scissors against the computer |
| typing test |  | Test your typing speed and accuracy |

## habits

| Task | Usage | What it does |
|---|---|---|
| habit done | `habit done <name>` | Tick a habit for today (habit done gym) |
| habit streak |  | Show all habits with current streak and the last 14 days |

## hardware

| Task | Usage | What it does |
|---|---|---|
| android adb | `android devices \| android battery \| android screenshot \| android open <web address>` | Look at an Android phone over USB or Wi-Fi with adb (android devices, android battery, android screenshot, android open https://example.com) |
| bluetooth devices | `bluetooth list \| bluetooth connect <name> \| bluetooth disconnect <name>` | List paired Bluetooth devices and connect or disconnect one (bluetooth list, bluetooth connect headphones). Uses the system's own tools; Linux needs bluetoothctl, macOS needs blueutil for connect. |
| mute volume |  | Mute or unmute the sound |
| next track |  | Skip to the next song |
| play pause |  | Play or pause the current media |
| previous track |  | Go back to the previous song |
| serial port | `serial ports \| serial send <port> <text> [baud 9600] \| serial read <port> [seconds]` | List serial ports or send a line to a device such as an Arduino (serial ports, serial send COM3 hello). Needs pip install pyserial. |
| set brightness | `set brightness <0-100>` | Set screen brightness (set brightness 60) |
| set volume | `set volume <0-100>` | Set the volume to a level (set volume 40) |
| show desktop |  | Minimise everything and show the desktop |
| take screenshot |  | Save a screenshot to your Pictures folder |
| toggle dark mode | `dark mode on\|off` | Switch dark/light mode (dark mode on, dark mode off, or toggle) |
| volume down | `volume down [amount]` | Lower the volume |
| volume up | `volume up [amount]` | Raise the volume |

## health

| Task | Usage | What it does |
|---|---|---|
| add medicine | `add medicine <name> at <time> [and <time>]` | Save a medicine and its times (add medicine metformin at 8am and 8pm) |
| bmi calculator | `bmi <weight> kg <height> cm` | Body mass index from weight and height (bmi 70 kg 175 cm, bmi 70 5 ft 9 in) |
| calorie calculator | `calorie calculator <male\|female> <age> years <kg> kg <cm> cm [activity]` | Estimate daily calories you burn (calorie calculator male 30 years 70 kg 175 cm moderate) |
| fasting timer | `fast start \| fast status \| fast end \| fast history` | Time a fast (fast start; fast status; fast end) |
| health log | `bp <sys>/<dia> \| sugar <value> [fasting\|after meal] \| health summary [month]` | Log blood pressure and blood sugar, see a weekly summary (bp 120/80; sugar 105 fasting; health summary) |
| heart rate zones | `heart rate zones age <years>` | Heart rate zones for your age (heart rate zones age 30) |
| macro split | `macros <calories> [high protein \| low carb]` | Split daily calories into protein, carbs and fat (macros 2000 calories) |
| medicine stock | `medicine stock add <name> <count> [<n> a day] \| medicine stock \| medicine refill <name> <count>` | Track how many pills are left and when to refill (medicine stock add metformin 30 2 a day; pills left; medicine refill metformin 60) |
| medicine today | `medicine today \| medicine taken <name> \| medicine remind \| remove medicine <name>` | Today's medicine list; tick one off, or get alerts for the rest of today (medicine today, medicine taken metformin, medicine remind, remove medicine metformin) |
| sleep log | `sleep log <hours> \| sleep show` | Log how long you slept and see your recent average (sleep log 7.5 hours, sleep show) |
| vaccine tracker | `add vaccine <person> <name> <date> \| vaccines \| remove vaccine <person> <name>` | Keep vaccine due dates for the family (add vaccine asha polio 12 nov 2026, vaccines, remove vaccine asha polio) |
| water log | `water log <amount> [ml\|glasses\|bottles] \| water today \| water goal <ml>` | Log water you drank and see today's total; a glass is 250 ml, a bottle 500 ml (water log 500 ml, water log 2 glasses, water today, water goal 3000) |
| weight log | `weight <kg> \| weight history \| weight goal <kg>` | Log your weight and see the trend (weight 72.5 kg, weight history, weight goal 70) |

## home

| Task | Usage | What it does |
|---|---|---|
| electricity bill | `electricity bill <units> at <rate> [fixed <amt>]` | Estimate an electricity bill (electricity bill 250 units at 7) |
| gas cylinder | `cylinder changed [date] \| cylinder \| cylinder remove` | Track gas cylinder changes and when the next one is due (cylinder changed; cylinder; cylinder history) |
| service log | `<item> <qty> [at <price>] \| <item> absent [date] \| <item> summary [month]` | Keep a daily log for milk, maid, newspaper and similar (milk 1.5 at 60; maid absent 3 nov; milk summary) |
| subscription tracker | `add subscription <name> <date> \| subscriptions \| remove subscription <name>` | Track subscriptions and renewal dates (add subscription netflix 15 dec 2026, subscriptions) |
| vehicle dues | `add vehicle due <what> <date> \| vehicle dues \| remove vehicle due <what>` | Track insurance, pollution certificate and service dates (add vehicle due insurance bike 15 dec 2026, vehicle dues) |
| warranty tracker | `add warranty <item> <date> \| warranties \| remove warranty <item>` | Keep warranty end dates and see what expires soon (add warranty laptop 12 mar 2027, warranties, remove warranty laptop) |

## info

| Task | Usage | What it does |
|---|---|---|
| check weather | `check weather <words>` | Weather for a city (e.g. weather mumbai) |
| daily quote |  | Show an inspiring quote |
| define word *(online)* | `meaning of <word>` | Dictionary meaning in the terminal (meaning of ephemeral); opens Google if offline |
| moon phase |  | Today's moon phase and the next new and full moon (moon phase) |
| news headlines *(online)* | `news headlines [topic]` | Top news headlines in the terminal (news headlines, news cricket) (needs internet) |
| pincode lookup *(online)* | `pincode <PIN>` | Look up an Indian PIN code (pincode 110001) (needs internet) |
| public holidays *(online)* | `public holidays [country] [year] \| next holiday` | Public holidays for a country and year (public holidays india 2026, holidays in us) |
| random fact |  | Show an interesting fact |
| sunrise sunset | `sunrise [city] [tomorrow\|date]` | Sunrise, sunset and day length for a city (sunrise delhi, sunset mumbai tomorrow) |
| tell joke |  | Tell a clean joke |
| weather report *(online)* | `weather report [city]` | Weather as text in the terminal (weather report mumbai) (needs internet) |
| wiki summary *(online)* | `wiki summary <topic>` | Short Wikipedia summary (wiki summary einstein) (needs internet) |

## journal

| Task | Usage | What it does |
|---|---|---|
| journal add | `journal add <text>` | Add a dated diary entry (journal had a great day) |
| journal prompt | `journal prompt` | Give a question to write about in your journal (journal prompt) |
| journal show | `journal show [days\|word]` | Read your journal (last 7 days; or a number of days, or a word to search) |

## learning

| Task | Usage | What it does |
|---|---|---|
| open coursera | `open coursera <words>` | Open Coursera |
| open duolingo |  | Open Duolingo |
| open khanacademy | `open khanacademy <words>` | Open Khan Academy |
| open nptel |  | Open NPTEL |
| open udemy | `open udemy <words>` | Open Udemy |

## links

| Task | Usage | What it does |
|---|---|---|
| list links |  | List saved bookmarks |
| open link | `open link <name>` | Open a saved bookmark by name (open link code) |
| remove link | `remove link <name>` | Delete a saved bookmark |
| save link | `save link <url> <name>` | Save a bookmark (save link github.com my code) |

## lists

| Task | Usage | What it does |
|---|---|---|
| document expiry | `add document <name> <expiry date> \| documents \| remove document <name>` | Remember when passports, licences and IDs expire (add document passport 12 mar 2031, documents, remove document passport) |
| family board *(online)* | `board add <text> \| board list \| board done <number> \| board undo <number>` | A shared to-do board for a family or small team. Items sync to the paired computers you share the 'board' channel with (board add buy milk, board list, board done 2, channel share board with kitchen-pc) |
| meal planner | `meal plan <day> <meals> \| meal plan \| meal today \| meal clear` | Plan the week's meals (meal plan monday dal rice, meal plan, meal today, meal clear) |
| my calendar | `calendar file <title> <date> [time] [for <minutes>]` | Make a .ics calendar event file that opens in any calendar app (calendar file dentist 25 dec 4pm) |
| shopping add | `shopping add <items>` | Add items to the shopping list (shopping add milk, eggs and bread) |
| shopping clear \* |  | Clear the whole shopping list |
| shopping list |  | Show the shopping list |
| shopping remove | `shopping remove <n\|name>` | Cross an item off (shopping remove 2, or shopping remove milk) |

## maps

| Task | Usage | What it does |
|---|---|---|
| get directions | `get directions <words>` | Directions to a place in Google Maps |
| open maps | `open maps <words>` | Open Google Maps or search a place |
| pharmacy near me | `pharmacy near me \| pharmacy in <place>` | Find a medical store or pharmacy near you or in a place (pharmacy near me) |
| restaurants near me | `restaurants near me \| restaurants in <place>` | Find restaurants near you or in a place (restaurants near me, restaurants in pune) |

## media

| Task | Usage | What it does |
|---|---|---|
| compress pdf | `compress pdf <file>` | Make a PDF smaller (compress pdf big.pdf) - needs: pip install pypdf (Pillow shrinks pictures too) |
| compress video | `compress video <file>` | Make a video file smaller with ffmpeg (compress video movie.mp4) |
| convert picture | `convert image <file> to <format>` | Convert a picture to another format (convert image photo.png to jpg) |
| extract audio | `extract audio <video file>` | Save the sound of a video as MP3 (extract audio movie.mp4) |
| merge pdf | `merge pdf <file> <file> ...` | Join PDF files into one (merge pdf a.pdf b.pdf) |
| ocr text | `read text from <picture>` | Read the text in a picture or screenshot (read text from scan.png; needs pip install pytesseract pillow and the Tesseract program) |
| pictures to pdf | `images to pdf <folder\|files>` | Combine pictures into one PDF (images to pdf <folder or files>) |
| render pdf | `pdf to images <file> [jpg] [<n> dpi]` | Save each PDF page as a picture (pdf to images report.pdf; pdf to images report.pdf 200 dpi) - needs: pip install pypdfium2 Pillow |
| resize picture | `resize image <file> to <width>` | Resize a picture (resize image photo.jpg to 800 wide, or 50%) |
| rotate pdf | `rotate pdf <file> [90\|180\|270\|left] [pages 1-3]` | Rotate PDF pages (rotate pdf scan.pdf 90; rotate pdf scan.pdf 180 pages 1-3) - needs: pip install pypdf |
| screen text | `screen text` | Take a screenshot, read the text in it and copy it to the clipboard (needs pillow, pytesseract and the Tesseract program) |
| shrink photos | `compress pictures <folder> [quality 60] [width 1600]` | Make every picture in a folder smaller into a new 'compressed' folder; originals untouched (compress pictures downloads, compress pictures trip quality 60 width 1600; needs pip install pillow) |
| split pdf | `split pdf <file> [pages 2-4]` | Split a PDF into pages, or pull out some pages (split pdf report.pdf pages 2-4) |
| watermark pdf | `watermark pdf <file> <text>` | Stamp text across every PDF page (watermark pdf report.pdf CONFIDENTIAL) - needs: pip install pypdf |

## money

| Task | Usage | What it does |
|---|---|---|
| add bill | `add bill <name> <day> [amount]` | Remember a monthly bill's due day (add bill electricity 15 1200) |
| add expense | `add expense <amount> <category> [note]` | Record spending (spent 450 on groceries, add expense 200 food lunch) |
| bank import | `import bank <file.csv>` | Import a bank statement CSV into your expenses (import bank statement.csv); guesses categories, skips duplicates |
| borrow money | `borrow <amount> from <name>` | Note money you borrowed from someone (borrow 300 from asha) |
| budget report | `budget report` | Show this month's spending against your budgets (budget report) |
| card dues | `add card <name> <date> \| cards \| remove card <name>` | Track credit card payment due dates (add card visa 15 nov, cards, remove card visa) |
| compound interest | `compound interest <amount> <rate%> <years>` | Compound interest (compound interest 10000 7 3 years [monthly]) |
| crypto price *(online)* | `crypto price <coin>` | Live cryptocurrency price (crypto price bitcoin) (needs internet) |
| currency convert *(online)* | `currency <amount> <from> to <to>` | Live currency conversion (currency 100 usd to inr) (needs internet) |
| discount price | `discount <price> <percent> [more %]` | Price after discount(s) (discount 2000 30% off, discount 2000 30 10) |
| emi loan | `emi <amount> <rate%> <years>` | Loan EMI (emi 5 lakh 8.5 5 years) |
| exchange rates *(online)* | `exchange rates [base currency]` | Table of today's exchange rates against the rupee (exchange rates, exchange rates eur) |
| expense total | `expense total [month]` | Spending totals by category (expense total, expense total last month) |
| freelance rate | `freelance rate income <n> expenses <n> hours <n>` | Work out the hourly rate you need (freelance rate income 4000 expenses 800 hours 25 weeks off 6). |
| fuel cost | `fuel cost <km> km <mileage> kmpl <price>` | Trip fuel cost from distance, mileage and price (fuel cost 250 km 18 kmpl 105 per litre) |
| gst amount | `gst <amount> [rate] [inclusive]` | GST add or remove (gst 1000 18, gst 1180 18 inclusive) |
| home meter | `meter add <name> <reading> \| meter list <name> \| meter use <name>` | Log meter readings and see use per day (meter add electricity 12450, meter list electricity, meter use electricity) |
| house split | `flat members <names> \| flat add <what> <amount> paid by <name> [split <names>] \| flat summary \| flat clear` | Share house costs between flatmates and see who pays whom (flat members amit ravi sam; flat add rent 18000 paid by amit; flat summary) |
| hra exemption | `hra basic <amt> hra <amt> rent <amt> [metro]` | HRA tax exemption (hra basic 50000 hra 20000 rent 18000 metro) |
| income tax | `income tax <income> [deductions <amount>]` | Income tax, new vs old regime (income tax 12 lakh; income tax 18 lakh deductions 2 lakh) |
| interest tax | `interest tax <interest> tax <rate %>   \|   interest tax deposit <amount> rate <%> tax <%>` | Tax on interest earned (interest tax deposit 10000 rate 5 tax 25; interest tax 800 tax 15) |
| inventory | `stock add <item> <qty> [min <n>] \| stock sell\|remove <item> <qty> \| stock set <item> <qty> \| stock list \| low stock \| stock delete <item>` | Keep a simple stock list for a shop or home (stock add rice 20 min 5, stock sell rice 3, stock list, low stock) |
| lend money | `lend <amount> to <name> [note]` | Note money you lent to someone (lend 500 to ravi for lunch) |
| loan compare | `compare loans <amt> <rate> <years> vs <rate> <years>` | Compare two loan offers side by side (compare loans 500000 8.5% 5y vs 9% 4y). |
| make invoice | `invoice <customer>: <qty> <item> at <rate>, ... [gst 18]` | Make a simple GST invoice page (invoice Ravi Traders: 3 pens at 10, 2 books at 150 gst 18) |
| mileage log | `mileage add <km> [note] \| mileage report [month] \| mileage rate <per km>` | Log trips and work out what you can claim (mileage add 25 km office, mileage report, mileage rate 8) |
| monthly report | `monthly report [YYYY-MM]` | Make a one-page report of this month (spending, budgets, recurring costs, mileage, 80C) you can open or print to PDF (monthly report) |
| payment reminder | `payment reminder <name in your ledger \| name amount [invoice X] [by date]>` | Write a polite payment-reminder message and copy it (payment reminder ravi, or: payment reminder Ravi Traders 5000 invoice INV-0012 by 15 nov) |
| percentage change | `percentage change <old> to <new>` | Percentage change between two numbers (percentage change 80 to 100) |
| ppf maturity | `ppf <amount a year> [years] [rate %]` | PPF maturity (ppf 1.5 lakh a year; ppf 50000 a year 15 years) |
| profit margin | `profit margin cost <c> price <p>` | Profit margin and markup, or the price you need for a target margin (profit margin cost 60 price 100 \| price for 30% margin cost 70). |
| rd maturity | `rd <monthly amount> <rate %> <years>` | Recurring deposit maturity (rd 5000 a month 6.5% 2 years) |
| receipts | `receipt add <amount> <category> <shop...> [date YYYY-MM-DD] \| receipt attach <id> <file> \| receipt list [YYYY[-MM]] \| receipt total [YYYY[-MM]] \| receipt report <YYYY> \| receipt remove <id>` | Keep receipts for tax time: receipt add 450 groceries "Big Bazaar", receipt attach 3 photo.jpg, receipt list 2026-11, receipt total 2026-11, receipt report 2026 |
| recurring costs | `recurring add <amount> <name> [category] \| recurring list \| recurring apply \| recurring remove <name>` | Costs that repeat every month (recurring add 649 netflix entertainment, recurring list, recurring apply, recurring remove netflix) |
| remove bill | `remove bill <name>` | Delete a saved bill (remove bill electricity) |
| remove budget | `remove budget <category>` | Remove a category budget (remove budget food) |
| salary breakup | `salary breakup <amount> [a month\|a year] [tax %] [pension %] [insurance %] [other <amount>]` | Take-home pay from gross salary (salary breakup 5000 a month tax 20 pension 5; salary 60000 a year tax 22) |
| set budget | `set budget <category> <amount>` | Set a monthly spending limit for a category (set budget food 5000) |
| settle ledger | `settle <name> [amount]` | Mark a debt as paid (settle ravi, settle ravi 200 for a part payment) |
| severance pay | `severance <years> years salary <amount> [a year] [weeks <n>]` | Estimate severance or end-of-service pay (severance 5 years salary 4000 a month weeks 2) |
| show expenses | `show expenses [category] [month]` | List expenses (show expenses, show expenses food, show expenses last month) |
| show ledger | `ledger [name]` | See who owes you and who you owe (ledger, who owes me, show ledger ravi) |
| sip goal | `sip goal <amount> in <years> years [at <rate>%]` | Monthly saving needed to reach a goal (sip goal 1 million in 15 years at 8%; how much to save for 50000 in 3 years) |
| sip growth | `sip <monthly> <return%> <years>` | SIP growth (sip 5000 12 10 years: monthly amount, yearly return %, years) |
| spending anomalies | `spending anomalies` | Find unusually large or possibly duplicated expenses (spending anomalies). |
| spending forecast | `spending forecast` | Predict this month's total spending from your pace so far, against your budgets (spending forecast). |
| spending trends | `spending trends` | Month-by-month spending, and which categories grew or shrank (spending trends). |
| split bill | `split bill <amount> among <n> [tip %]` | Split a bill (split bill 2400 among 4 tip 10%) |
| tax saving | `80c add <amount> <what> \| 80c \| 80c remove <what>` | Track your Section 80C investments against the 1,50,000 limit (80c add 50000 ppf, 80c, 80c remove ppf) |
| tip calculator | `tip <bill> [percent%] [split <people>]` | Work out a tip and split the bill (tip 1200 10%, tip 2450 12% split 4) |
| undo expense \* |  | Remove the last recorded expense |
| unit price | `unit price <qty><unit> <price> vs <qty><unit> <price>` | Which pack is cheaper per kg or litre (unit price 500g 45 vs 1kg 80) |
| upcoming bills | `upcoming bills [days]` | Bills due soon (upcoming bills, upcoming bills 30) |

## network

| Task | Usage | What it does |
|---|---|---|
| ai channel *(online)* | `channel export <name> [file] \| channel search <word> \| channel list \| channel post <name> [as <label>:] <text> \| channel read <name> [n] \| channel wait <name> [seconds] \| channel share <name> with <computer> \| channel unshare <name> with <computer> \| channel pull <name> from <computer> \| channel remove <name>` | Shared message boards that people and AIs on different JeeG computers read and write (channel post lab hello, channel read lab, channel share lab with kitchen-pc). Messages from others are information, never commands. |
| bridge *(online)* | `bridge add <name> when <source> [if contains <word>] then <step> ; <step> \| bridge list \| bridge remove <name> \| bridge test <name> <message> \| bridge run [minutes]` | Rules that connect things: when a message arrives from MQTT, a webhook, UDP/TCP, serial, WebSocket, a channel or a chat, do steps on something else (bridge add door when mqtt home door/front if contains open then ha on light.hall ; channel post lab door opened). Run them with: bridge run. Terminal only. |
| check internet *(online)* |  | Check whether the internet is working |
| check speed *(online)* |  | Test internet speed (Speedtest) |
| check website *(online)* | `check website <url>` | Check if a website is up (check website github.com) |
| dns lookup *(online)* | `dns lookup <domain>` | Look up the IP addresses of a domain |
| fetch file *(online)* \* | `download <https address> [preview]` | Download a file from a web address into your Downloads folder (download https://example.com/a.pdf); asks first, refuses programs and scripts |
| fleet check *(online)* \* | `check all computers` | Ask every saved computer (see "computer add") for its health at once: disk, memory, uptime. Needs JeeG and an ssh key on each. |
| flush dns \* |  | Clear the DNS cache |
| handoff *(online)* | `handoff allow <computer> \| handoff ask <computer> <request> \| handoff inbox \| handoff reply <id> <text> \| handoff result <id> [seconds] \| handoff list` | Ask the AI or person at another JeeG computer to do a job and get the answer back (handoff ask kitchen-pc summarise report.pdf, then handoff result <id>). Both sides must run: handoff allow <computer> |
| home assistant *(online)* | `ha add <name> <address> \| ha states [filter] \| ha on\|off\|toggle <entity> \| ha call <domain.service> <entity> [json] \| ha list \| ha remove <name>` | Control Home Assistant (add it once with ha add home http://homeassistant.local:8123, then ha states light, ha on light.kitchen, ha call switch.turn_off switch.fan). The access token is asked for and kept private. |
| iot hub *(online)* | `iot list \| iot status \| iot scene add <name> = <step> ; <step> \| iot scene run <name> \| iot scene list \| iot scene remove <name>` | One place for your home devices and computers: see everything (iot list) and save scenes that do several things at once (iot scene add night = device off lamp ; mqtt publish home lights/hall off) |
| listening ports |  | Show which programs are listening on network ports |
| live network speed | `live network speed [seconds]` | Watch your current download/upload speed for a few seconds (live network speed) |
| modbus device *(online)* | `modbus read <host[:502]> holding\|input\|coil\|discrete <address> [count] [unit N]` | Read Modbus TCP devices on your network such as PLCs and energy meters (modbus read 192.168.1.60 holding 0 2). Writing is a separate task that asks first: modbus write ... |
| modbus write *(online)* \* | `modbus write <host[:502]> holding <address> <value> \| modbus write <host[:502]> coil <address> on\|off` | Write to a Modbus TCP device (modbus write 192.168.1.60 coil 5 on, modbus write 192.168.1.60 holding 10 500). Asks first. |
| mqtt message *(online)* | `mqtt add <name> <host[:port]> [user] \| mqtt publish <name> <topic> <message> \| mqtt listen <name> <topic> [seconds] \| mqtt list \| mqtt remove <name>` | Send or listen to MQTT messages (mqtt add home 192.168.1.2, mqtt publish home lights/kitchen on, mqtt listen home sensors/#) |
| network doctor *(online)* | `network doctor` | Find out why the internet is slow or down: checks your network, router, name lookup and the internet, then says what to try |
| peer jeeg *(online)* | `peer add <name> <link from 'connect ai'> \| peer run <name> <task> \| peer list \| peer remove <name>` | Talk to a JeeG on another computer through its AI-mode link (peer add office <link>, peer run office disk space) |
| ping host *(online)* | `ping host <name or ip>` | Ping a host (ping google.com) |
| port check *(online)* | `port check <host> <port>` | Check if a port is open (port check example.com 443) |
| port owner | `who uses port <number>` | Which program is using a port (who uses port 3000) |
| rest api *(online)* | `rest add <name> <https address> [bearer\|header <Header-Name>\|none] \| rest get <name> [path] \| rest list \| rest remove <name>` | Save a web service once (rest add shop https://api.example.com bearer, you are asked for the key) and call it (rest get shop /orders, rest post shop /items {"name":"x"}). |
| rest post *(online)* \* | `rest post <name> <path> <json>` | Send JSON to a saved web service (rest post shop /items {"name":"x"}). Asks first. Save the service with: rest add |
| rss feed *(online)* | `feed add <url> [name] \| feed list \| feed remove <n> \| read feeds [n]` | Follow blogs and news sites by their RSS/Atom feed (feed add https://site/feed, read feeds, feed list, feed remove 2) |
| save page *(online)* | `save page <url>` | Save a web page as readable text for offline reading (save page https://example.com/article). Saved in Documents/JeeG pages. |
| scan network *(online)* | `who is on my wifi [scan]` | List the devices on your home network (who is on my wifi). Add "scan" to wake the quiet ones first. Only your own private network. |
| setup home *(online)* | `setup home [192.168.1 \| 192.168.1.50]` | Look on your home network for Home Assistant, MQTT brokers, Shelly and Tasmota plugs, and print the exact commands to save them (setup home, or setup home 192.168.1) |
| share file *(online)* | `send <file> to my phone` | Send one file to your phone or another computer on the same Wi-Fi: shows a link and QR code, serves that one file once, then stops |
| show ip *(online)* |  | Show your local and public IP address |
| smart device *(online)* | `device add <name> <shelly\|tasmota> <ip> \| device on\|off\|toggle\|status <name> \| device list \| device remove <name>` | Control smart plugs on your home network (device add lamp shelly 192.168.1.50, then: device on lamp / device off lamp / device status lamp) |
| socket tools *(online)* | `tcp send <host:port> <text> \| tcp read <host:port> [seconds] \| udp send <host:port> <text> \| udp listen <port> [seconds] \| ws send <ws://address> <text> \| ws read <ws://address> [seconds]` | Talk to devices over plain TCP, UDP or WebSocket on your own network (tcp send 192.168.1.40:9000 hello, udp send 192.168.1.40:4210 on, udp listen 4210 10, ws send ws://192.168.1.5:81 hi) |
| ssh hosts | `computer add <name> <user@host> \| computer list \| computer remove <name>` | Save other computers you can reach with ssh (computer add pi pi@192.168.1.20), then run JeeG tasks on them |
| ssh task *(online)* \* | `on <name> run <task>` | Run a JeeG task on another computer over ssh (on pi run disk space). Needs JeeG there and an ssh key (no password prompts). |
| ssl expiry *(online)* | `ssl expiry <site>` | Show how many days a site's https certificate has left (ssl expiry mysite.com) |
| trace route *(online)* | `trace route <host>` | Trace the network route to a host |
| wake on lan *(online)* | `wake <name \| MAC address> \| wake add <name> <MAC> \| wake list \| wake remove <name>` | Turn on a computer on your network with a Wake-on-LAN packet (wake add nas AA:BB:CC:DD:EE:FF, then: wake nas) |
| watch site *(online)* | `watch page\|price\|site\|ssl\|release <target> [name] \| watch list \| watch remove <n> \| check watches` | Watch a web page, a price, a site being up, a certificate, or a GitHub release; "check watches" reports what changed (watch page https://x.com/news, watch price https://shop.com/item, watch site https://mysite.com, watch ssl mysite.com, watch release owner/repo) |
| webhook *(online)* | `webhook add <name> <https address> \| webhook send <name> <text> \| webhook list \| webhook remove <name>` | Save web addresses (Slack, Discord, Zapier, n8n ...) and send them a message (webhook add team https://..., webhook send team deploy done) |
| wifi info |  | Show the Wi-Fi network you are connected to |
| zigbee devices *(online)* | `zigbee devices <broker> \| zigbee on\|off\|toggle <broker> <device> \| zigbee set <broker> <device> <key> <value> \| zigbee get <broker> <device>` | Switch Zigbee devices through zigbee2mqtt over your saved MQTT broker (zigbee devices home, zigbee on home hall-lamp, zigbee off home hall-lamp, zigbee set home hall-lamp brightness 120). Save the broker first: mqtt add |

## notes

| Task | Usage | What it does |
|---|---|---|
| vault | `vault copy [<note> \| find <words>] \| vault plan [edit block] \| vault set [folder] \| vault search <words> \| vault read <note> \| vault list [folder] \| vault recent` | Search and read your Obsidian notes (a folder of .md files): vault set, vault search <words>, vault read <note>, vault list, vault recent, vault copy <note \| find words \| nothing> (puts a note and AI instructions on the clipboard to paste into claude.ai, DeepSeek or ChatGPT), vault plan (shows what an AI's edit block would change, without changing anything). Read-only. |
| vault apply \* | `vault apply [edit block] \| vault undo` | Apply the edit block an AI gave you (copied from claude.ai, DeepSeek, ChatGPT...) to your Obsidian notes, with a backup: vault apply (reads the clipboard) or vault apply <json>. vault undo puts the last change back. Asks first. |
| vault edit \* | `vault replace <note> \| <old> \| <new>   or   vault cut <note> \| <text>   or   vault prepend <note> \| <text>` | Edit one Obsidian note: vault replace <note> \| <old text> \| <new text>, vault cut <note> \| <text to remove>, vault prepend <note> \| <text>. Backs up first (vault undo). Asks first. |
| vault listen | `vault listen [count]` | Leave this running while you chat with claude.ai, DeepSeek or ChatGPT: when you copy an AI's edit block, JeeG shows what it would change and asks y/n to apply it. Ctrl+C to stop. Terminal only. |
| vault trash \* | `vault trash <note>` | Move an Obsidian note to the vault's .trash folder (never deleted for good): vault trash <note>. Can be undone with vault undo. Asks first. |
| vault write \* | `vault append <note> \| <text>   or   vault new <note> \| <text>` | Add text to the end of an Obsidian note or make a new one: vault append <note> \| <text>, vault new <note> \| <text>. Never overwrites or deletes; backs up first (vault undo). Asks first. |

## personal

| Task | Usage | What it does |
|---|---|---|
| reading list | `add book <title> \| books \| finished book <title> \| remove book <title>` | Keep a list of books to read and finished (add book Atomic Habits, books, finished book atomic habits) |

## power

| Task | Usage | What it does |
|---|---|---|
| cancel shutdown |  | Cancel a pending shutdown or restart |
| lock screen |  | Lock the computer |
| log out \* |  | Sign out of the current user |
| restart pc \* |  | Restart the computer (30 second delay, can be cancelled) |
| schedule shutdown \* | `schedule shutdown <minutes>` | Shut down after N minutes (schedule shutdown 45 minutes) |
| shutdown pc \* |  | Shut the computer down (30 second delay, can be cancelled) |
| sleep pc \* |  | Put the computer to sleep |

## productivity

| Task | Usage | What it does |
|---|---|---|
| life report | `life report [last month \| year]` | A visual page of your month: spending bars, habit heat-map, water, sleep, to-dos (life report, life report last month, life report year) |
| my data lookup | `search my data <words>` | Search your notes, journal, to-dos, expenses and other saved records (search my data milk) |
| note add | `add note <text>` | Save a quick note (note add call dentist at 5) |
| note list | `show notes [word]` | Show your recent notes (optionally filter by a word) |
| playbook | `playbook add <name> = <step> ; <step> \| playbook run <name> \| playbook list \| playbook show <name> \| playbook remove <name>` | Save a reviewed multi-step job under a name and run it any time, by you or by an AI that is allowed to run but not change it (playbook add morning = show reminders ; what is due ; playbook run morning). Adding and removing are terminal only. |
| study log | `study log <subject> <time> \| study report` | Log study time and see where it goes (study log maths 45 min, study report) |
| todo add | `add todo <text>` | Add a to-do item (add todo buy milk) |
| todo clear |  | Remove finished items from the to-do list |
| todo done | `todo done <number\|text>` | Mark a to-do done (todo done 3, or part of its text) |
| todo list |  | Show your to-do list |
| weekly summary | `weekly summary \| monthly summary` | One-page summary of your week or month: spending, habits, journal, to-dos, water and sleep (weekly summary, monthly summary) |
| work tracker | `track start <task> \| track stop \| track status \| track report [today\|week]` | Track how long you work on things (track start report, track stop, track status, track report week) |

## reference

| Task | Usage | What it does |
|---|---|---|
| open wikipedia | `open wikipedia <words>` | Open Wikipedia or look up an article |

## reminders

| Task | Usage | What it does |
|---|---|---|
| add countdown | `add countdown <event> <date>` | Count the days to an event (add countdown exam 12 dec 2026) |
| calendar feed *(online)* | `calendar feed add <name> <https address \| file.ics> \| calendar feed upcoming [name] [days] \| calendar feed list \| calendar feed remove <name>` | Show upcoming events from a calendar link or .ics file (calendar feed add work <secret iCal address>, calendar feed upcoming). Works with Google/Outlook secret iCal links, no sign-in. |
| eye break | `eye break [minutes]` | 20-20-20 eye break reminder every 20 minutes |
| notify due | `notify due` | Pop up a notification for what is due: birthdays, bills, countdowns, medicine (what is due, notify due) |
| notify me | `notify <text>` | Show a desktop notification (notify me dinner is ready, notify Front door opened) |
| pomodoro | `pomodoro [rounds] [N work] [N break]` | Pomodoro focus timer: 25 min work / 5 min break (pomodoro 4 rounds) |
| remind me | `remind me <when> <what>` | Background reminder (remind me at 5:30pm to call mom / in 20 minutes ... / every 2 hours ...) |
| remove countdown | `remove countdown <event>` | Delete a countdown (remove countdown exam) |
| set alarm | `set alarm <time>` | Set an alarm for a clock time (set alarm 6:30 am) |
| show countdowns | `show countdowns` | Show the days left for your events (show countdowns) |
| show reminders |  | List active background reminders and alarms |
| stop reminders |  | Cancel all background reminders and alarms |
| stretch reminder | `stretch reminder [minutes]` | Remind you to stand up and stretch every 45 minutes |
| water reminder | `water reminder [minutes]` | Remind you to drink water every 30 minutes |

## routines

| Task | Usage | What it does |
|---|---|---|
| daily briefing *(online)* | `daily briefing [city]` | Daily briefing (say: morning briefing): date, weather, to-dos, birthdays, reminders |
| edit routines |  | Open the routines file to add or change routines |
| end work day |  | Routine: show to-dos then lock the screen after 5 s (editable) |
| kit install \* | `kit install <file>` | Install a kit file made by 'kit export' (kit install file). Asks first; keeps anything you already have; check it first with 'kit show' |
| kit share | `kit export <name> \| kit show <file>` | Share your routines, aliases and variables as one file, or look inside someone else's (kit export mykit, kit show file) |
| list routines |  | List your routines and their steps |
| meeting mode |  | Routine: open Meet and your calendar (editable) |
| night mode |  | Routine: dark mode, dim screen, low volume (editable) |
| run routine | `run routine <name> [words]` | Run any routine from your routines file (run routine <name> [words]; steps can use {1} {2} {args}) |
| start work day |  | Routine: open mail and calendar, show your to-dos (editable) |
| study mode |  | Routine: notes app, low volume, 25-minute study timer (editable) |

## search

| Task | Usage | What it does |
|---|---|---|
| cricket score | `cricket score [team]` | Open live cricket scores (cricket score india, cricket score csk) |
| gold price | `gold price [city] \| silver price [city]` | Look up gold or silver rates (gold price, silver price delhi) |
| search google | `search google <words>` | Search Google (or open it) |
| search images | `search images <words>` | Search Google Images |
| search news | `search news <words>` | Search Google News / latest headlines |
| search scholar | `search scholar <words>` | Search Google Scholar for papers |
| stock price | `stock price <company>` | Look up a share price (stock price tcs, stock price apple) |
| translate text | `translate text <words>` | Translate text with Google Translate |

## security

| Task | Usage | What it does |
|---|---|---|
| audit log | `audit show [n] \| audit summary \| audit ai \| audit export [file.csv]` | See and export what JeeG ran and who asked (you or an AI): audit show 20, audit summary, audit export. Task names and results only, never what you typed. |
| breach check *(online)* | `breach check "<password>"` | Check if a password has appeared in known data leaks (only a 5-character hash prefix is sent) |
| file hash | `file hash <file> [expected hash]` | Show the SHA-256, SHA-1 and MD5 fingerprint of a file, to check a download (file hash setup.exe) |
| find secrets | `find secrets [folder]` | Look for passwords, API keys and private keys left in a project folder before you share it (find secrets myproject). Values are hidden in the answer. |
| identify file | `identify file <file>` | Tell what a file really is from its first bytes, not its name, and warn if the name is misleading (identify file report.pdf) |
| integrity baseline | `integrity save <folder> \| integrity check <folder> \| integrity list \| integrity forget <folder>` | Save the fingerprints of a folder, then check later which files were added, changed or removed (integrity save myfolder, integrity check myfolder) |
| password strength | `password strength "<password>"` | Rate how strong a password is, privately (password strength "MyPass123") |
| shred file \* | `shred file <file> [preview]` | Overwrite a file with random data and delete it (cannot be undone) |
| ssh key audit | `ssh key audit` | Check your SSH keys and folder for weak or risky settings (old key types, no passphrase, loose permissions). Reads only; never shows a key. |

## selfcheck

| Task | Usage | What it does |
|---|---|---|
| realtest *(online)* | `real test list \| real test run <group\|id\|all> \| real test show <id> \| real test compare \| real test report \| real test ai \| real test manual \| real test clear` | Test JeeG on this real computer, by yourself or with an AI you connected (Claude.ai...). Harmless checks only; makes a private report you can share. real test list \| run <group> \| report \| ai \| manual |

## shopping

| Task | Usage | What it does |
|---|---|---|
| open amazon | `open amazon <words>` | Open Amazon India or search it |
| open flipkart | `open flipkart <words>` | Open Flipkart or search it |
| open myntra | `open myntra <words>` | Open Myntra or search it |

## snippets

| Task | Usage | What it does |
|---|---|---|
| list snippets |  | List saved snippets |
| paste snippet | `paste snippet <name>` | Copy a saved snippet to the clipboard (paste snippet email) |
| remove snippet | `remove snippet <name>` | Delete a saved snippet |
| save snippet | `save snippet <name> <text>` | Save a reusable text snippet (save snippet email me@example.com) |

## social

| Task | Usage | What it does |
|---|---|---|
| add contact | `add contact <name> <number>` | Save a contact for WhatsApp (add contact mom 9876543210) |
| add email address | `add email <name> <address>` | Save an email address for a contact (add email mom mom@example.com) |
| find contact | `find contact <name>` | Look up a saved contact by name (find contact mom) |
| open discord |  | Open Discord |
| open facebook |  | Open Facebook |
| open instagram |  | Open Instagram |
| open linkedin |  | Open LinkedIn |
| open pinterest | `open pinterest <words>` | Open Pinterest or search it |
| open reddit | `open reddit <words>` | Open Reddit or search it |
| open snapchat |  | Open Snapchat Web |
| open telegram |  | Open Telegram Web |
| open twitter | `open twitter <words>` | Open X (Twitter) |
| open whatsapp |  | Open WhatsApp Web |
| remove contact \* | `remove contact <name>` | Delete a saved contact (remove contact mom) |
| send whatsapp | `send whatsapp <contact\|number> <message>` | Start a WhatsApp message to a saved contact or number (send whatsapp to mom hello) |
| show contacts |  | List your saved contacts |

## study

| Task | Usage | What it does |
|---|---|---|
| add class | `add class <subject> <day> <time>` | Add a weekly class or lesson (add class maths mon 9:00, add class physics tue 2:30 pm room 4) |
| attendance percentage | `attendance <attended> of <total> [need <percent>]` | Attendance percentage and classes you can skip (attendance 42 of 50; need 75) |
| cgpa to percentage | `cgpa <value> [out of 4]` | Convert CGPA to percentage (cgpa 8.2 to percentage; cbse 9.4) |
| flashcards | `flashcards [count] [file]` | Spaced-repetition flashcards from a 'question \| answer' file; cards you miss come back sooner (flashcards, flashcards 5 myfile.txt) |
| gpa planner | `gpa planner current <gpa> credits <done> target <gpa> next <credits> [scale 10]` | What you must score next to reach a target GPA (gpa planner current 3.2 credits 90 target 3.4 next 30) |
| make citation | `cite <book\|article\|web> <author>; <title>; <year or source>; ...` | Format a citation in APA and MLA (cite book Smith, John; Deep Learning; 2020; MIT Press) |
| marks percentage | `marks <obtained> out of <total>` | Percentage from marks (marks 432 out of 500) |
| reading time | `reading time <file>` | How long a text file or PDF takes to read (reading time notes.txt) |
| remove class | `remove class <subject> [day]` | Remove a class from the timetable (remove class maths mon) |
| show timetable |  | Show your weekly timetable |
| study planner | `study plan <n> subjects <n> days <n> hours` | Plan study hours per day (study plan 5 subjects 20 days 6 hours) |
| todays classes | `todays classes \| tomorrows classes` | Classes you have today or tomorrow (todays classes, tomorrows classes) |

## system

| Task | Usage | What it does |
|---|---|---|
| battery status |  | Show battery level and charging state |
| check updates *(online)* \* |  | Check which programs and system updates are waiting (does not install) |
| cpu temperature |  | Show processor temperature (where the computer allows it) |
| cpu usage |  | Show current CPU load |
| desktop input \* | `desktop type <text> \| desktop key <combo> \| desktop click <x> <y> \| add 'preview' to see what would happen` | Type, press keys or click at a screen position in whatever window is in front (desktop type hello, desktop key ctrl+s, desktop click 500 300). Asks first; you only, never an AI. Windows built in; Linux needs xdotool; macOS needs cliclick for clicks. |
| disk space |  | Show free space on your drives |
| env variable \* | `set env variable NAME to VALUE \| remove env variable NAME \| add <folder> to path` | Save an environment variable for good (set env variable API_URL to https://x.com) or add a folder to PATH (add C:\tools to path). Add "preview" to see what would change. New terminals pick it up. |
| find software *(online)* | `search app [words]` | Find an app in your package manager (search app video editor), or list the apps I can install by short name (search app) |
| gpu info |  | Show graphics card details |
| health check |  | One-screen check of your computer: disk, memory, CPU, battery, uptime, with warnings |
| install app *(online)* \* | `install <app> [and <app> ...] [preview]` | Install an app or program by name with your system's package manager (install vlc, install chrome and git; add "preview" to see the command only) |
| install bundle *(online)* \* | `install <dev\|office\|media\|student\|privacy> bundle [preview]` | Install a set of apps in one go (install dev bundle: git, python, vscode, nodejs; also office, media, student, privacy). Add "preview" to see the commands only. |
| installed programs | `installed programs [name]` | List installed programs, or search them (installed programs chrome) |
| is installed | `is <app> installed \| version of <app>` | Check whether a program is installed and which version (is git installed, which version of python, do i have vlc) |
| keep awake | `keep awake [2 hours]` | Stop the computer sleeping for a while (keep awake 2 hours) |
| kill process \* | `kill process <name>` | Close a program by name (e.g. kill process notepad) |
| memory usage |  | Show RAM usage |
| print file \* | `print <file> [preview]` | Print a file on your default printer (print report.pdf; add "preview" to see the command only) |
| restart explorer \* |  | Restart Windows Explorer when the taskbar or desktop freezes |
| running processes |  | List the programs using the most memory |
| screen off |  | Turn the screen off without sleeping |
| screen resolution |  | Show your screen resolution |
| setup check *(online)* | `setup check` | Check your saved devices, paired computers, bridge rules, ports and optional tools, and say what to fix (setup check). For the basic JeeG self-check use: doctor |
| show printers | `show printers` | List your printers and whether they are ready, and the default one |
| show uptime |  | Show how long the computer has been on |
| startup programs |  | List programs that start with your computer |
| system info *(online)* |  | Show OS, CPU, memory, disk and uptime |
| uninstall app \* | `uninstall <app> [preview]` | Uninstall an app by name with your system's package manager (uninstall vlc; add "preview" to see the command only) |
| update apps *(online)* \* | `update all apps \| update app <name> [preview]` | Update all your installed apps (update all apps), or one (update app vlc); add "preview" to see the command only |
| usb devices |  | List connected USB devices |
| window control | `windows list \| window focus\|minimize\|maximize\|restore\|close <part of title> \| window snap <part of title> left\|right\|full` | List and control open windows (windows list, window focus chrome, window minimize notepad, window snap chrome left, window close notepad). Windows built in; Linux needs wmctrl or xdotool; macOS uses System Events. |

## text

| Task | Usage | What it does |
|---|---|---|
| binary hex | `binary\|hex\|octal <number>` | Convert a number between decimal, binary, hex and octal (binary 1010, hex ff, 255) |
| dedupe lines | `remove duplicates <items>` | Remove duplicate lines or items, keeping the first (remove duplicates a, b, a, c) |
| lorem ipsum | `lorem ipsum [3 paragraphs\|50 words]` | Generate placeholder text (lorem ipsum 3 paragraphs, or 50 words) |
| lowercase text | `lowercase <text>` | lowercase some text (lowercase HELLO World) |
| number to words | `number to words <number>` | Write a number in words, Indian and international style (number to words 1234567) |
| qr code | `qr code <text or link>` | Make a QR code picture from text or a link (qr code https://example.com) |
| readability score | `readability <text or file>` | Reading level of a text or file (Flesch score and grade). Works with piped text. |
| reverse text | `reverse text <text>` | Reverse text (reverse text hello) |
| roman numerals | `roman numeral <number\|numeral>` | Convert between Roman numerals and numbers (roman numeral 2026, or roman numeral MCMXC) |
| sort lines | `sort lines <items>` | Sort a list alphabetically or by number (sort lines pear, apple, fig); add 'reverse' for Z-A |
| summarize text | `summarize <file \| clipboard> [sentences]` | Pick the key sentences from a text file, PDF or the clipboard (summarize notes.txt, summarize clipboard 5). Not AI: it scores sentences by word frequency. |
| title case text | `title case <text>` | Title Case Some Text (title case the quick brown fox) |
| uppercase text | `uppercase <text>` | UPPERCASE some text (uppercase hello world); with no text it uses the clipboard |
| url decode | `url decode <text>` | Turn a percent-encoded web address back into readable text (url decode hello%20world) |
| url encode | `url encode <text>` | Make text safe for use in a web address (url encode hello world & more) |
| word frequency | `word frequency <text\|file>` | Most common words in some text or a text file (word frequency notes.txt) |

## time

| Task | Usage | What it does |
|---|---|---|
| add days | `add <n> days to <date>` | Date arithmetic (add 45 days to 1 jan 2027, 3 months from today, 10 days ago) |
| age calculator |  | Work out an age from a birth date |
| convert time zone | `meeting time <time> <place> in <place>[, <place>]` | Convert a meeting time between places (meeting time 9 am india in london, 3 pm new york to mumbai) |
| date difference | `days between <date> and <date>` | Days between two dates (days between 1 jan 2027 and 25 dec 2027) |
| days until |  | Days until a date (days until 25 dec 2026) |
| set timer | `set timer <duration> [label]` | Countdown timer with a beep (set timer 10 minutes tea) |
| show calendar |  | Show a month calendar (show calendar march 2027) |
| show time |  | Show the current time and date |
| stopwatch |  | Start a stopwatch (press Enter to stop) |
| unix timestamp | `unix timestamp [number\|date]` | Unix timestamp now, or convert one (unix timestamp 1700000000, or a date) |
| week number | `week number [date]` | ISO week number, day of year and quarter (week number, week number 25 dec 2026) |
| weekday of | `what day is <date>` | Which weekday a date falls on (what day is 15 aug 2027) |
| world time | `time in <city>[, <city>]` | Current time in cities (time in london, tokyo and new york) |

## tools

| Task | Usage | What it does |
|---|---|---|
| open ilovepdf |  | Open iLovePDF (merge, split, compress PDFs) |
| open removebg |  | Open remove.bg background remover |
| open tinypng |  | Open TinyPNG image compressor |
| open virustotal |  | Open VirusTotal file/URL scanner |

## travel

| Task | Usage | What it does |
|---|---|---|
| flight status | `flight status <number>` | Check a flight's status (flight status 6E 204) |
| open irctc |  | Open IRCTC train booking |
| open makemytrip |  | Open MakeMyTrip |
| open uber |  | Open Uber |
| pnr status | `pnr status <10-digit pnr>` | Check an Indian Railways PNR status (pnr status 1234567890) |
| train status | `train status <number>` | Check a train's live running status (train status 12951) |
| trip budget | `trip budget <days> days <n> people <amount> a day [fare <amount>]` | Estimate a trip budget (trip budget 4 days 2 people 3000 a day) |

## utility

| Task | Usage | What it does |
|---|---|---|
| calculate | `calculate <expression>` | Calculate anything (calculate 15% of 200, 12 * (3+4), sqrt 144) |
| convert units *(online)* | `convert <n> <unit> to <unit>` | Convert units offline (convert 5 km to miles, 100 f to c); falls back to Google for currency |
| cooking convert | `cooking convert <amount> <unit> [ingredient] to <unit>` | Convert cooking measures, with grams for common ingredients (cooking convert 2 cups flour to grams) |
| count words | `count words <text\|file>` | Count words, lines and characters in text or a file |
| decode base64 | `decode base64 <text>` | Decode Base64 text |
| encode base64 | `encode base64 <text>` | Base64-encode text |
| flip coin |  | Flip a coin |
| generate password | `generate password [length]` | Generate a strong random password (generate password 20) |
| generate uuid |  | Generate a random UUID |
| hash text | `hash text <text\|file>` | SHA-256 / SHA-1 / MD5 of text or a file |
| json format | `json format <file>` | Pretty-print and validate a JSON file, or JSON piped in (type data.json \| jeeg format json) |
| my habits | `my habits [month\|year]` | See which phrases and tasks you use most, which often fail, and shortcuts worth saving (my habits; habits month) |
| random choice | `random choice a, b, c` | Pick one option at random (random choice pizza, burger, pasta) |
| random number | `random number [min] [max]` | Random number (random number 1 to 50) |
| roll dice | `roll <n>d<sides>` | Roll dice (roll dice, roll 2d6, roll d20) |
| var define | `set var <name> = <value>` | Save a value under a name and use it in any phrase as $name (set var rate = 18, then gst 1000 $rate). |
| var list | `vars` | Show your saved variables (vars, show variables). |
| var remove | `remove var <name>` | Delete a saved variable (remove var rate). |

## web

| Task | Usage | What it does |
|---|---|---|
| open browser |  | Open the default web browser |
| open website | `open website <address>` | Open any website (open website github.com) |

## work

| Task | Usage | What it does |
|---|---|---|
| action items | `action items <notes file \| text>` | Pull the to-do lines out of meeting notes (action items notes.txt, or paste text after it). Simple rules, no AI. |
| meeting notes | `meeting notes [title]` | Create a dated meeting-notes file from a template (meeting notes weekly sync) |

## workspace

| Task | Usage | What it does |
|---|---|---|
| add event | `add event <words>` | Add a Google Calendar event (words become the title) |
| new document |  | Create a new Google Doc |
| new meeting |  | Start an instant Google Meet |
| new presentation |  | Create a new Google Slides deck |
| new spreadsheet |  | Create a new Google Sheet |
| open calendar |  | Open Google Calendar |
| open canva |  | Open Canva |
| open classroom |  | Open Google Classroom |
| open docs |  | Open Google Docs |
| open drive |  | Open Google Drive |
| open figma |  | Open Figma |
| open keep |  | Open Google Keep notes |
| open meet |  | Open Google Meet |
| open notion |  | Open Notion |
| open office |  | Open Microsoft Office online |
| open onedrive |  | Open OneDrive |
| open outlook |  | Open Outlook mail |
| open photos |  | Open Google Photos |
| open sheets |  | Open Google Sheets |
| open slack |  | Open Slack |
| open slides |  | Open Google Slides |
| open teams |  | Open Microsoft Teams |
| open trello |  | Open Trello |
| open zoom |  | Open Zoom |

Back to [Home](Home).
