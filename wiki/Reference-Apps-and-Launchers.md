# Reference: Apps, launchers and linked apps

Opening apps and websites, workspace shortcuts, social and AI sites, and the linked-app and MCP tasks.

113 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [apps](#apps), [apps_setup](#apps-setup), [apps_write](#apps-write), [workspace](#workspace), [social](#social), [ai](#ai), [entertainment](#entertainment), [tools](#tools), [reference](#reference), [food](#food), [utility](#utility)

## apps

### linked apps

**Usage:** `apps | apps <name>`  
**What it does:** List the apps JeeG is linked to (GitHub, Telegram, Discord, Slack, WhatsApp, your own) and what each one can do. "apps github" shows one app's actions.  
**Also found by:** `connected apps`, `apps list`, `which apps`, `what apps can the ai use`, `app connections`, `my apps`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/linked_apps.py`

### linked read

**Usage:** `app read <app> <action> [arguments]`  
**What it does:** Look at something in a linked app without changing it (app read github issues, app read github repo_issues owner/name). Nothing is ever sent or changed.  
**Behaviour:** can use the internet.  
**Also found by:** `app read`, `read from app`, `github issues`, `github notifications`, `read github`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/linked_read.py`

### mcp look

**Usage:** `mcp look <name> <tool> [json arguments]`  
**What it does:** Use a read-only tool of a saved MCP server (mcp look files read_file {"path": "notes.txt"}). Only tools you marked as read run; nothing is changed.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `look with mcp`, `read with mcp`, `mcp read`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mcp_look.py`

### open app

**Usage:** `open app <name>`  
**What it does:** Open any installed app by name (open app <name>)  
**Also found by:** `application`, `program`, `software`, `launch`, `app`  
**Script:** `scripts/open_app.py`

### open bluetooth settings

**What it does:** Open Bluetooth settings  
**Also found by:** `bluetooth`, `pair`, `headphones`, `earbuds`  
**Script:** `scripts/open_bluetooth_settings.py`

### open brave

**What it does:** Open Brave browser  
**Also found by:** `brave`  
**Script:** `scripts/open_brave.py`

### open calculator

**What it does:** Open the calculator  
**Also found by:** `calc`, `calculator`, `math`, `calculate`  
**Script:** `scripts/open_calculator.py`

### open camera

**What it does:** Open the camera  
**Also found by:** `camera`, `webcam`, `photo booth`, `selfie`  
**Script:** `scripts/open_camera.py`

### open chrome

**What it does:** Open Google Chrome  
**Also found by:** `chrome`, `chromium`  
**Script:** `scripts/open_chrome.py`

### open clock

**What it does:** Open the Clock / alarms app  
**Also found by:** `clock`, `alarm`, `timer app`, `stopwatch app`  
**Script:** `scripts/open_clock.py`

### open control panel

**What it does:** Open the classic Control Panel  
**Also found by:** `control panel`, `legacy settings`  
**Script:** `scripts/open_control_panel.py`

### open device manager

**What it does:** Open Device Manager  
**Also found by:** `device manager`, `drivers`, `hardware`, `devices`  
**Script:** `scripts/open_device_manager.py`

### open edge

**What it does:** Open Microsoft Edge  
**Also found by:** `edge`, `msedge`  
**Script:** `scripts/open_edge.py`

### open excel

**What it does:** Open Microsoft Excel / a spreadsheet app  
**Also found by:** `excel`, `spreadsheet editor`, `xls`, `xlsx`  
**Script:** `scripts/open_excel.py`

### open firefox

**What it does:** Open Firefox  
**Also found by:** `firefox`, `mozilla`  
**Script:** `scripts/open_firefox.py`

### open incognito

**What it does:** Open a private / incognito browser window  
**Also found by:** `private`, `incognito`, `secret`, `anonymous`, `window`  
**Script:** `scripts/open_incognito.py`

### open notepad

**What it does:** Open a simple text editor  
**Also found by:** `notes`, `text editor`, `write`, `notepad`, `textedit`  
**Script:** `scripts/open_notepad.py`

### open paint

**What it does:** Open Paint / an image editor  
**Also found by:** `paint`, `mspaint`, `draw`, `drawing`, `image editor`  
**Script:** `scripts/open_paint.py`

### open powerpoint

**What it does:** Open PowerPoint / a presentation app  
**Also found by:** `powerpoint`, `ppt`, `pptx`, `presentation editor`, `slideshow`  
**Script:** `scripts/open_powerpoint.py`

### open powershell

**What it does:** Open PowerShell  
**Also found by:** `powershell`, `ps`, `shell`, `console`  
**Script:** `scripts/open_powershell.py`

### open resource monitor

**What it does:** Open Resource Monitor  
**Also found by:** `resource monitor`, `resmon`, `performance monitor`  
**Script:** `scripts/open_resource_monitor.py`

### open settings

**What it does:** Open system Settings  
**Also found by:** `settings`, `preferences`, `configuration`, `setup`  
**Script:** `scripts/open_settings.py`

### open snipping tool

**What it does:** Open the snipping / screenshot tool  
**Also found by:** `snip`, `snipping`, `clip`, `screenshot tool`, `crop screen`  
**Script:** `scripts/open_snipping_tool.py`

### open taskmanager

**What it does:** Open Task Manager / system monitor  
**Also found by:** `task manager`, `processes`, `performance`, `system monitor`, `activity monitor`  
**Script:** `scripts/open_taskmanager.py`

### open terminal

**What it does:** Open a terminal / command prompt  
**Also found by:** `terminal`, `command prompt`, `cmd`, `shell`, `console`, `bash`  
**Script:** `scripts/open_terminal.py`

### open vlc

**What it does:** Open VLC media player  
**Also found by:** `vlc`, `video player`, `media player`, `movie player`  
**Script:** `scripts/open_vlc.py`

### open vscode

**What it does:** Open Visual Studio Code  
**Also found by:** `vscode`, `visual studio`, `code`, `editor`, `ide`, `programming`, `vs`  
**Script:** `scripts/open_vscode.py`

### open wifi settings

**What it does:** Open Wi-Fi settings  
**Also found by:** `wifi settings`, `wireless`, `network settings`  
**Script:** `scripts/open_wifi_settings.py`

### open word

**What it does:** Open Microsoft Word / a word processor  
**Also found by:** `word`, `document editor`, `doc editor`  
**Script:** `scripts/open_word.py`


## apps-setup

### event rules

**Usage:** `rule add <name> when <app> <read-action> [args] changes [every N minutes] then <task words> | rules list | rule remove <name> | rules run once | rules run`  
**What it does:** Run a task when something new shows up in a linked app: rule add issues when github issues changes then say new issue {new}. Lists, removes and runs rules (rules run once | rules run). Terminal only.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `rule add`, `rules list`, `when something new`, `on new item`, `trigger a task`, `watch an app`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/event_rules.py`

### linked setup

**Usage:** `app login <app> [device client_id=...] | app preset list|add <name> [base=...] | app keystore on|off | app ai allow|deny <app> | app ai list|reset|dry on|off | app logout <app> | app add <name> <https://base> [none|bearer|basic|header:NAME|query:NAME] | app add <name> command | app action <app> <name> <GET|POST|...> </path> [params=a,b] [format="{x}"] [list=path] [body='{"k":"{a}"}'] [desc="..."] | app remove <name>`  
**What it does:** Link JeeG to an app: log in (app login github), add your own app by its web address (app add trello https://api.trello.com/1 query:key), define what it can do (app action ...), log out or remove, use ready-made presets, keep logins in the system keychain, choose which apps an AI may use. Terminal only: an AI cannot do this.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `app login`, `app logout`, `app add`, `app action`, `app remove`, `app preset`, `app keystore`, `app ai`, `link app`, `connect app`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/linked_setup.py`


## apps-write

### linked do

**Usage:** `app do <app> <action> [arguments] [preview]`  
**What it does:** Do something in a linked app that changes things: comment on GitHub, send a Telegram, Discord or Slack message, open a WhatsApp chat (app do telegram send chat=123 hello). Always asks first; add "preview" to see the request without sending.  
**Behaviour:** asks before running; can use the internet; never saved in history.  
**Also found by:** `app do`, `act in app`, `send through app`, `comment on github`, `send telegram message`, `post to discord`, `post to slack`, `whatsapp message`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/linked_do.py`


## workspace

### add event

**Usage:** `add event <words>`  
**What it does:** Add a Google Calendar event (words become the title)  
**Also found by:** `new event`, `schedule`, `remind`, `reminder`, `meeting`, `appointment`  
**Script:** `scripts/add_event.py`

### new document

**What it does:** Create a new Google Doc  
**Also found by:** `new doc`, `blank document`, `create document`, `write`  
**Script:** `scripts/new_document.py`

### new meeting

**What it does:** Start an instant Google Meet  
**Also found by:** `instant meeting`, `start call`, `new call`, `video call`  
**Script:** `scripts/new_meeting.py`

### new presentation

**What it does:** Create a new Google Slides deck  
**Also found by:** `new slides`, `blank presentation`, `create presentation`  
**Script:** `scripts/new_presentation.py`

### new spreadsheet

**What it does:** Create a new Google Sheet  
**Also found by:** `new sheet`, `blank spreadsheet`, `create spreadsheet`  
**Script:** `scripts/new_spreadsheet.py`

### open calendar

**What it does:** Open Google Calendar  
**Also found by:** `schedule`, `events`, `meeting`, `meetings`, `agenda`  
**Script:** `scripts/open_calendar.py`

### open canva

**What it does:** Open Canva  
**Also found by:** `design`, `poster`, `graphic`, `logo`  
**Script:** `scripts/open_canva.py`

### open classroom

**What it does:** Open Google Classroom  
**Also found by:** `google classroom`, `class`, `school`, `assignment`  
**Script:** `scripts/open_classroom.py`

### open docs

**What it does:** Open Google Docs  
**Also found by:** `google docs`, `document`, `word`  
**Script:** `scripts/open_docs.py`

### open drive

**What it does:** Open Google Drive  
**Also found by:** `google drive`, `cloud`, `storage`, `files`  
**Script:** `scripts/open_drive.py`

### open figma

**What it does:** Open Figma  
**Also found by:** `design`, `ui`, `prototype`  
**Script:** `scripts/open_figma.py`

### open keep

**What it does:** Open Google Keep notes  
**Also found by:** `google keep`, `notes`, `memo`, `sticky`  
**Script:** `scripts/open_keep.py`

### open meet

**What it does:** Open Google Meet  
**Also found by:** `google meet`, `video call`, `meeting`, `call`  
**Script:** `scripts/open_meet.py`

### open notion

**What it does:** Open Notion  
**Also found by:** `notes`, `wiki`, `workspace`, `docs`  
**Script:** `scripts/open_notion.py`

### open office

**What it does:** Open Microsoft Office online  
**Also found by:** `microsoft`, `word`, `excel`, `powerpoint`, `365`  
**Script:** `scripts/open_office.py`

### open onedrive

**What it does:** Open OneDrive  
**Also found by:** `microsoft cloud`, `storage`, `files`  
**Script:** `scripts/open_onedrive.py`

### open outlook

**What it does:** Open Outlook mail  
**Also found by:** `microsoft mail`, `hotmail`, `email`  
**Script:** `scripts/open_outlook.py`

### open photos

**What it does:** Open Google Photos  
**Also found by:** `google photos`, `pictures`, `gallery`  
**Script:** `scripts/open_photos.py`

### open sheets

**What it does:** Open Google Sheets  
**Also found by:** `google sheets`, `spreadsheet`, `excel`  
**Script:** `scripts/open_sheets.py`

### open slack

**What it does:** Open Slack  
**Also found by:** `work chat`, `team`, `workspace`  
**Script:** `scripts/open_slack.py`

### open slides

**What it does:** Open Google Slides  
**Also found by:** `google slides`, `presentation`, `ppt`, `powerpoint`  
**Script:** `scripts/open_slides.py`

### open teams

**What it does:** Open Microsoft Teams  
**Also found by:** `microsoft teams`, `meeting`, `call`, `chat`  
**Script:** `scripts/open_teams.py`

### open trello

**What it does:** Open Trello  
**Also found by:** `boards`, `kanban`, `tasks`, `project`  
**Script:** `scripts/open_trello.py`

### open zoom

**What it does:** Open Zoom  
**Also found by:** `video call`, `meeting`, `call`  
**Script:** `scripts/open_zoom.py`


## social

### add contact

**Usage:** `add contact <name> <number>`  
**What it does:** Save a contact for WhatsApp (add contact mom 9876543210)  
**Also found by:** `contact`, `save contact`, `new contact`, `save number`, `remember number`, `phone book`  
**Your words:** passed through untouched  
**Script:** `scripts/add_contact.py`

### add email address

**Usage:** `add email <name> <address>`  
**What it does:** Save an email address for a contact (add email mom mom@example.com)  
**Also found by:** `add email`, `save email address`, `email address of`, `set email`, `contact email`  
**Your words:** passed through untouched  
**Script:** `scripts/add_email_address.py`

### find contact

**Usage:** `find contact <name>`  
**What it does:** Look up a saved contact by name (find contact mom)  
**Also found by:** `look up contact`, `whose number`, `number of`, `phone number of`, `contact number`  
**Your words:** passed through untouched  
**Script:** `scripts/find_contact.py`

### open discord

**What it does:** Open Discord  
**Also found by:** `chat`, `server`, `gaming`, `social`  
**Script:** `scripts/open_discord.py`

### open facebook

**What it does:** Open Facebook  
**Also found by:** `fb`, `social`, `meta`  
**Script:** `scripts/open_facebook.py`

### open instagram

**What it does:** Open Instagram  
**Also found by:** `insta`, `ig`, `social`, `reels`  
**Script:** `scripts/open_instagram.py`

### open linkedin

**What it does:** Open LinkedIn  
**Also found by:** `network`, `professional`, `social`  
**Script:** `scripts/open_linkedin.py`

### open pinterest

**Usage:** `open pinterest <words>`  
**What it does:** Open Pinterest or search it  
**Also found by:** `pins`, `ideas`, `social`, `search`  
**Script:** `scripts/open_pinterest.py`

### open reddit

**Usage:** `open reddit <words>`  
**What it does:** Open Reddit or search it  
**Also found by:** `subreddit`, `social`, `search`  
**Script:** `scripts/open_reddit.py`

### open snapchat

**What it does:** Open Snapchat Web  
**Also found by:** `snap`, `social`  
**Script:** `scripts/open_snapchat.py`

### open telegram

**What it does:** Open Telegram Web  
**Also found by:** `chat`, `message`, `social`  
**Script:** `scripts/open_telegram.py`

### open twitter

**Usage:** `open twitter <words>`  
**What it does:** Open X (Twitter)  
**Also found by:** `x`, `tweet`, `social`  
**Script:** `scripts/open_twitter.py`

### open whatsapp

**What it does:** Open WhatsApp Web  
**Also found by:** `chat`, `message`, `messages`, `wa`, `whatsapp web`  
**Script:** `scripts/open_whatsapp.py`

### remove contact

**Usage:** `remove contact <name>`  
**What it does:** Delete a saved contact (remove contact mom)  
**Behaviour:** asks before running.  
**Also found by:** `delete contact`, `forget contact`, `erase contact`, `remove number`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_contact.py`

### send whatsapp

**Usage:** `send whatsapp <contact|number> <message>`  
**What it does:** Start a WhatsApp message to a saved contact or number (send whatsapp to mom hello)  
**Also found by:** `whatsapp message`, `message`, `text someone`, `wa`, `send message`, `whatsapp number`, `chat with`, `msg`  
**Your words:** passed through untouched  
**Script:** `scripts/send_whatsapp.py`

### show contacts

**What it does:** List your saved contacts  
**Also found by:** `contacts`, `my contacts`, `list contacts`, `phone book`, `saved numbers`  
**Script:** `scripts/show_contacts.py`


## ai

### open chatgpt

**What it does:** Open ChatGPT  
**Also found by:** `ai`, `openai`, `gpt`, `chatbot`, `chat`  
**Script:** `scripts/open_chatgpt.py`

### open claude

**What it does:** Open Claude  
**Also found by:** `ai`, `anthropic`, `assistant`, `chatbot`  
**Script:** `scripts/open_claude.py`

### open gemini

**What it does:** Open Google Gemini  
**Also found by:** `ai`, `google ai`, `bard`, `assistant`  
**Script:** `scripts/open_gemini.py`

### open perplexity

**Usage:** `open perplexity <words>`  
**What it does:** Open Perplexity (or ask it)  
**Also found by:** `ai`, `answer`, `ask`, `search`  
**Script:** `scripts/open_perplexity.py`


## entertainment

### movie info

**Usage:** `movie info <title>`  
**What it does:** Look up a movie or show on IMDb (movie info inception)  
**Also found by:** `imdb`, `movie rating`, `movie details`, `film info`, `cast of`, `movie reviews`, `show rating`, `web series info`, `find movie`  
**Your words:** passed through untouched  
**Script:** `scripts/movie_info.py`

### open hotstar

**What it does:** Open JioHotstar  
**Also found by:** `hotstar`, `jio`, `cricket`, `movies`, `watch`, `disney`  
**Script:** `scripts/open_hotstar.py`

### open jiosaavn

**Usage:** `open jiosaavn <words>`  
**What it does:** Open JioSaavn music  
**Also found by:** `music`, `songs`, `saavn`, `hindi songs`  
**Script:** `scripts/open_jiosaavn.py`

### open netflix

**Usage:** `open netflix <words>`  
**What it does:** Open Netflix  
**Also found by:** `movies`, `series`, `shows`, `watch`, `stream`  
**Script:** `scripts/open_netflix.py`

### open primevideo

**What it does:** Open Amazon Prime Video  
**Also found by:** `prime`, `movies`, `series`, `watch`, `amazon prime`  
**Script:** `scripts/open_primevideo.py`

### open spotify

**Usage:** `open spotify <words>`  
**What it does:** Open Spotify web player or search it  
**Also found by:** `music`, `songs`, `playlist`, `search`  
**Script:** `scripts/open_spotify.py`

### open twitch

**Usage:** `open twitch <words>`  
**What it does:** Open Twitch  
**Also found by:** `streams`, `gaming`, `live`  
**Script:** `scripts/open_twitch.py`

### open youtube

**Usage:** `open youtube <words>`  
**What it does:** Open YouTube or search it  
**Also found by:** `video`, `videos`, `watch`, `search`, `yt`  
**Script:** `scripts/open_youtube.py`

### open youtube music

**Usage:** `open youtube music <words>`  
**What it does:** Open YouTube Music or search it  
**Also found by:** `music`, `songs`, `listen`, `search`  
**Script:** `scripts/open_youtube_music.py`

### play song

**Usage:** `play <song name> [on spotify|youtube]`  
**What it does:** Play a song: searches YouTube Music (or 'on spotify' / 'on youtube'); plain 'play' toggles play/pause  
**Also found by:** `play`, `song`, `songs`, `listen`, `track`, `music`, `put on`, `sing`, `play music`, `by artist`  
**Your words:** passed through untouched  
**Script:** `scripts/play_song.py`

### recipe lookup

**Usage:** `recipe <dish>`  
**What it does:** Find a recipe (recipe paneer butter masala)  
**Also found by:** `recipe`, `find recipe`, `how to cook`, `cooking`, `how to make food`, `dish recipe`, `ingredients for`, `cook`, `recipes`  
**Your words:** passed through untouched  
**Script:** `scripts/recipe_lookup.py`

### song lyrics

**Usage:** `lyrics <song>`  
**What it does:** Find the lyrics of a song (lyrics shape of you)  
**Also found by:** `lyrics`, `find lyrics`, `words of song`, `lyrics of`, `song words`  
**Your words:** passed through untouched  
**Script:** `scripts/song_lyrics.py`


## tools

### open ilovepdf

**What it does:** Open iLovePDF (merge, split, compress PDFs)  
**Also found by:** `pdf`, `merge pdf`, `split pdf`, `compress pdf`, `convert pdf`  
**Script:** `scripts/open_ilovepdf.py`

### open removebg

**What it does:** Open remove.bg background remover  
**Also found by:** `remove background`, `background remover`, `transparent`  
**Script:** `scripts/open_removebg.py`

### open tinypng

**What it does:** Open TinyPNG image compressor  
**Also found by:** `compress image`, `compress photo`, `reduce image size`  
**Script:** `scripts/open_tinypng.py`

### open virustotal

**What it does:** Open VirusTotal file/URL scanner  
**Also found by:** `scan`, `virus`, `malware`, `check file`, `check link`  
**Script:** `scripts/open_virustotal.py`


## reference

### open wikipedia

**Usage:** `open wikipedia <words>`  
**What it does:** Open Wikipedia or look up an article  
**Also found by:** `wiki`, `encyclopedia`, `search`, `article`  
**Script:** `scripts/open_wikipedia.py`


## food

### open swiggy

**What it does:** Open Swiggy  
**Also found by:** `food`, `order food`, `restaurant`, `delivery`, `instamart`  
**Script:** `scripts/open_swiggy.py`

### open zomato

**What it does:** Open Zomato  
**Also found by:** `food`, `order food`, `restaurant`, `delivery`  
**Script:** `scripts/open_zomato.py`


## utility

### calculate

**Usage:** `calculate <expression>`  
**What it does:** Calculate anything (calculate 15% of 200, 12 * (3+4), sqrt 144)  
**Also found by:** `calc`, `math`, `maths`, `compute`, `solve`, `evaluate`, `plus`, `minus`, `times`, `divided`  
**Your words:** passed through untouched  
**Script:** `scripts/calculate.py`

### convert units

**Usage:** `convert <n> <unit> to <unit>`  
**What it does:** Convert units offline (convert 5 km to miles, 100 f to c); falls back to Google for currency  
**Behaviour:** can use the internet.  
**Also found by:** `convert`, `conversion`, `converter`, `unit`, `units`, `currency`, `exchange`, `how many`, `in miles`, `in km`  
**Your words:** passed through untouched  
**Script:** `scripts/convert_units.py`

### cooking convert

**Usage:** `cooking convert <amount> <unit> [ingredient] to <unit>`  
**What it does:** Convert cooking measures, with grams for common ingredients (cooking convert 2 cups flour to grams)  
**Also found by:** `cup to grams`, `grams to cups`, `tablespoon to ml`, `teaspoon to ml`, `recipe conversion`, `convert cups`, `cooking measures`, `how many grams in a cup`, `baking conversion`  
**Your words:** passed through untouched  
**Script:** `scripts/cooking_convert.py`

### count words

**Usage:** `count words <text|file>`  
**What it does:** Count words, lines and characters in text or a file  
**Behaviour:** reads piped text.  
**Also found by:** `word count`, `characters`, `lines`, `length`, `how many words`, `text statistics`, `wc`  
**Script:** `scripts/count_words.py`

### decode base64

**Usage:** `decode base64 <text>`  
**What it does:** Decode Base64 text  
**Behaviour:** reads piped text.  
**Also found by:** `decode`, `b64 decode`, `base64 decode`, `decrypt base64`  
**Script:** `scripts/decode_base64.py`

### encode base64

**Usage:** `encode base64 <text>`  
**What it does:** Base64-encode text  
**Behaviour:** reads piped text.  
**Also found by:** `base64`, `encode`, `b64`  
**Script:** `scripts/encode_base64.py`

### flip coin

**What it does:** Flip a coin  
**Also found by:** `coin`, `flip`, `heads`, `tails`, `toss`, `coin toss`, `flip a coin`  
**Script:** `scripts/flip_coin.py`

### generate password

**Usage:** `generate password [length]`  
**What it does:** Generate a strong random password (generate password 20)  
**Also found by:** `password`, `passwd`, `random password`, `strong password`, `new password`, `secure password`, `generate`  
**Your words:** passed through untouched  
**Script:** `scripts/generate_password.py`

### generate uuid

**What it does:** Generate a random UUID  
**Also found by:** `uuid`, `guid`, `unique id`, `random id`  
**Script:** `scripts/generate_uuid.py`

### hash text

**Usage:** `hash text <text|file>`  
**What it does:** SHA-256 / SHA-1 / MD5 of text or a file  
**Behaviour:** reads piped text.  
**Also found by:** `hash`, `checksum`, `sha256`, `sha1`, `md5`, `sha`, `file hash`, `digest`  
**Script:** `scripts/hash_text.py`

### json format

**Usage:** `json format <file>`  
**What it does:** Pretty-print and validate a JSON file, or JSON piped in (type data.json | jeeg format json)  
**Behaviour:** reads piped text.  
**Also found by:** `json`, `pretty print json`, `format json`, `validate json`, `beautify json`, `json file`  
**Script:** `scripts/json_format.py`

### my habits

**Usage:** `my habits [month|year]`  
**What it does:** See which phrases and tasks you use most, which often fail, and shortcuts worth saving (my habits; habits month)  
**Behaviour:** never saved in history.  
**Also found by:** `usage report`, `most used tasks`, `what do i use most`, `habit report`, `usage stats`, `jeeg stats`, `shortcut suggestions`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/my_habits.py`

### random choice

**Usage:** `random choice a, b, c`  
**What it does:** Pick one option at random (random choice pizza, burger, pasta)  
**Also found by:** `choose`, `pick`, `decide`, `choice`, `either`, `help me decide`, `which one`  
**Your words:** passed through untouched  
**Script:** `scripts/random_choice.py`

### random number

**Usage:** `random number [min] [max]`  
**What it does:** Random number (random number 1 to 50)  
**Also found by:** `random`, `number`, `pick a number`, `between`, `lottery`, `rand`  
**Your words:** passed through untouched  
**Script:** `scripts/random_number.py`

### roll dice

**Usage:** `roll <n>d<sides>`  
**What it does:** Roll dice (roll dice, roll 2d6, roll d20)  
**Also found by:** `dice`, `roll`, `die`, `d6`, `d20`, `ludo`  
**Your words:** passed through untouched  
**Script:** `scripts/roll_dice.py`

### var define

**Usage:** `set var <name> = <value>`  
**What it does:** Save a value under a name and use it in any phrase as $name (set var rate = 18, then gst 1000 $rate).  
**Also found by:** `define variable`, `store value`, `remember value as`, `named value`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/var_define.py`

### var list

**Usage:** `vars`  
**What it does:** Show your saved variables (vars, show variables).  
**Also found by:** `vars`, `variables`, `show vars`, `list variables`, `my variables`, `show my variables`  
**Script:** `scripts/var_list.py`

### var remove

**Usage:** `remove var <name>`  
**What it does:** Delete a saved variable (remove var rate).  
**Also found by:** `unset variable`, `forget variable`, `clear variable`, `delete variable`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/var_remove.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
