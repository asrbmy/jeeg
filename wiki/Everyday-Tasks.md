# Everyday Tasks

A guided tour by area. The [Task Catalog](Task-Catalog) lists every task with its exact usage; `list <category>` does the same in the terminal.

## Open things
- Websites: `open youtube`, `open gmail`, `open github.com`, `search cats`, `search images golden retriever`, `search news election`.
- Apps: `open chrome`, `open vscode`, `open settings`, or `open <any installed app>`.
- Folders: `open downloads`, `open documents`, `open desktop`.
- Only `http`, `https`, `mailto`, `tel`, `sms` and `whatsapp` links are ever opened.

## Music and messages
- `play shape of you` (YouTube Music search), `play shape of you on spotify`, `play`, `next song`, `previous song`.
- `add contact mom 9876543210`, then `send whatsapp to mom see you at 5`. WhatsApp opens the chat ready; you press Send (WhatsApp offers no safe way to send for you). Ten-digit numbers are taken as Indian (+91).
- `email mom about dinner` opens a Gmail draft; you press send.

## Money (Indian digit grouping, checked against independent calculations)
`emi loan 25 lakh 8.5% 20 years`, `sip growth 5000 12% 15 years`, `compound interest ...`, `gst amount 1000 18%`, `split bill 2450 among 4`, `percentage change 80 to 100`, `discount price 2999 30%`, `rd 5000 6.5 2 years`, `salary breakup`, `compare loans`, `profit margin`, `freelance rate`, `tip 1200 10%`, `unit price 500g 45 vs 1kg 80`. Online: `currency convert 100 usd to inr`, `crypto price bitcoin`, `exchange rates`, `gold price`.

## Dates and time
`time in london and tokyo`, `what day is 15 aug 2027`, `week number 25 dec 2026`, `add 45 days to 1 jan 2027`, `3 months from today`, `10 days ago`, `days between ... and ...` (also working days), `days until 25 dec 2026`, `age calculator 14 aug 2001`, `meeting time 9 am india in london`, `sunrise delhi`, `moon phase`, `public holidays india 2026`, `unix timestamp`. Month arithmetic clamps to the last day of a month.

## Files and media
- Find: `find file invoice`, `find text invoice in documents`, `folder size downloads`, `large files`, `find duplicates`, `recent files`, `folder tree documents depth 3`.
- Organise: `organize downloads preview`, `backup folder documents`, `zip folder x`, `unzip file x.zip`, `move file a.txt to documents`, `copy file a.txt to desktop`, `open last download`.
- Rename and clean: `bulk rename downloads replace img with photo` (preview, then add `apply`), `rename files in trip as holiday_{n}.{ext}`, `delete empty folders downloads preview`, `delete old downloads 90 days` (moves into a holding folder, never deletes). `undo` reverses moves and renames.
- Pictures (Pillow): `resize image photo.jpg to 800`, `convert image a.png to jpg`, `images to pdf`, `compress pictures downloads quality 60`, `strip exif photo.jpg`. Output goes next to the original; nothing is overwritten.
- PDF (pypdf): `merge pdf a.pdf b.pdf`, `split pdf report.pdf pages 2-4`, `pdf to text`, rotate, compress, watermark.
- Video (ffmpeg): `compress video movie.mp4`, `extract audio movie.mp4`.
- Bare file names are looked up in the current folder, then Downloads, Desktop and Documents. Quote names with spaces.
- Search inside your files: `index folder Documents`, then `search index invoice march` (private index; skips hidden folders, binaries and secret-looking files).

## System
- Status: `system info`, `memory usage`, `cpu usage`, `battery status`, `disk space`, `running processes`, `show uptime`, `cpu temperature`, `gpu info`, `usb devices`, `startup programs`.
- Control: `lock screen`, `shutdown pc`, `restart pc`, `sleep pc`, `cancel shutdown`, `schedule shutdown 45 minutes`, `set volume 40`, `mute`, `set brightness 60`, `take screenshot`, `toggle dark mode`, `keep awake 2 hours`.
- Process control: `kill process notepad`, `kill port 3000` (both ask first; critical system processes are refused).

## Network
`check internet`, `show ip`, `wifi info`, `ping host google.com`, `dns lookup x.com`, `port check host 443`, `check website github.com`, `listening ports`, `trace route x.com`, `network doctor`. More in [Programs, Network and Shop](Programs-Network-and-Shop).

## Security
`password strength "MyPass123"` (offline estimate), `breach check "..."` (sends only the first 5 characters of a hash to Have I Been Pwned), `generate password 20`, `compare files a b`, `file hash setup.exe`, `shred file x` (cannot be guaranteed on SSDs or synced folders). Password tasks are never written to history.

## Text tools
`uppercase`, `lowercase`, `title case`, `reverse text`, `sort lines`, `remove duplicates`, `word frequency`, `number to words 1234567` (Indian and international), `roman numeral 2026`, `binary 1010`, `hex ff`, `lorem ipsum 3 paragraphs`, `qr code <text>`, `encode base64`, `hash text hello`, `json format`, `url encode`, `readability`, `regex test "a+" on "caaat"`. Most use the clipboard when you give no text and copy the result back.

## Developer
`git status/diff/log/commit/pull/push/branch/stash/checkout`, `undo last commit` (refuses if pushed), `new project demo flask`, `create gitignore python`, `create venv`, `pip install requests`, `serve folder`, `lines of code`, `json to csv`, `csv summary`, `http get <url>`, `env variables`, `docker ps`, `kill port 3000`, `run tests`, `who uses port 3000`.

## Fun and learning
`guess the number`, `rock paper scissors`, `typing test`, `quiz me` (from a text file of `question | answer` lines), `flashcards <file>`, `tell joke`, `daily quote`, `flip coin`, `roll 2d6`, `random choice a, b, c`.

## Looking things up (needs internet)
`weather in pune`, `wiki summary python`, `define serendipity`, `news headlines`, `pincode 560001`, `translate good morning`. These open a search in your browser: `cricket score india`, `stock price tcs`, `recipe <dish>`, `directions to taj mahal`, `flight status 6E 204`, `train status 12951`. Offline they say so plainly.
