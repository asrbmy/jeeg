# Reference: Health, study, media and fun

Health logs and calculators, study tools, pictures, PDF and video, learning sites, games and quizzes.

64 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [health](#health), [study](#study), [learning](#learning), [media](#media), [fun](#fun), [text](#text)

## health

### add medicine

**Usage:** `add medicine <name> at <time> [and <time>]`  
**What it does:** Save a medicine and its times (add medicine metformin at 8am and 8pm)  
**Behaviour:** never saved in history.  
**Also found by:** `medicine schedule`, `save medicine`, `new medicine`, `pill schedule`, `tablet times`, `add pill`  
**Your words:** passed through untouched  
**Script:** `scripts/add_medicine.py`

### bmi calculator

**Usage:** `bmi <weight> kg <height> cm`  
**What it does:** Body mass index from weight and height (bmi 70 kg 175 cm, bmi 70 5 ft 9 in)  
**Also found by:** `bmi`, `body mass index`, `check bmi`, `my bmi`, `am i overweight`, `weight and height`, `ideal weight`  
**Your words:** passed through untouched  
**Script:** `scripts/bmi_calculator.py`

### calorie calculator

**Usage:** `calorie calculator <male|female> <age> years <kg> kg <cm> cm [activity]`  
**What it does:** Estimate daily calories you burn (calorie calculator male 30 years 70 kg 175 cm moderate)  
**Also found by:** `calories`, `bmr`, `daily calories`, `calories needed`, `maintenance calories`, `tdee`, `how many calories do i burn`, `metabolic rate`  
**Your words:** passed through untouched  
**Script:** `scripts/calorie_calculator.py`

### fasting timer

**Usage:** `fast start | fast status | fast end | fast history`  
**What it does:** Time a fast (fast start; fast status; fast end)  
**Behaviour:** never saved in history.  
**Also found by:** `fasting`, `fast start`, `fast status`, `fast end`, `intermittent fasting`, `break fast`, `how long have i fasted`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/fasting_timer.py`

### health log

**Usage:** `bp <sys>/<dia> | sugar <value> [fasting|after meal] | health summary [month]`  
**What it does:** Log blood pressure and blood sugar, see a weekly summary (bp 120/80; sugar 105 fasting; health summary)  
**Behaviour:** never saved in history.  
**Also found by:** `bp log`, `blood pressure`, `blood sugar`, `glucose log`, `sugar reading`, `health summary`, `bp reading`, `diabetes log`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/health_log.py`

### heart rate zones

**Usage:** `heart rate zones age <years>`  
**What it does:** Heart rate zones for your age (heart rate zones age 30)  
**Also found by:** `max heart rate`, `target heart rate`, `hr zones`, `pulse zones`  
**Your words:** passed through untouched  
**Script:** `scripts/heart_rate_zones.py`

### macro split

**Usage:** `macros <calories> [high protein | low carb]`  
**What it does:** Split daily calories into protein, carbs and fat (macros 2000 calories)  
**Also found by:** `macros`, `protein carbs fat`, `daily macros`, `macro calculator`, `nutrient split`  
**Your words:** passed through untouched  
**Script:** `scripts/macro_split.py`

### medicine stock

**Usage:** `medicine stock add <name> <count> [<n> a day] | medicine stock | medicine refill <name> <count>`  
**What it does:** Track how many pills are left and when to refill (medicine stock add metformin 30 2 a day; pills left; medicine refill metformin 60)  
**Behaviour:** never saved in history.  
**Also found by:** `pills left`, `tablets left`, `medicine supply`, `refill medicine`, `medicine refill`, `days of medicine left`, `running out of medicine`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/medicine_stock.py`

### medicine today

**Usage:** `medicine today | medicine taken <name> | medicine remind | remove medicine <name>`  
**What it does:** Today's medicine list; tick one off, or get alerts for the rest of today (medicine today, medicine taken metformin, medicine remind, remove medicine metformin)  
**Behaviour:** never saved in history.  
**Also found by:** `medicine taken`, `took medicine`, `medicine remind`, `remove medicine`, `medicine list`, `which medicine`, `pills today`  
**Your words:** passed through untouched  
**Script:** `scripts/medicine_today.py`

### sleep log

**Usage:** `sleep log <hours> | sleep show`  
**What it does:** Log how long you slept and see your recent average (sleep log 7.5 hours, sleep show)  
**Also found by:** `log sleep`, `i slept`, `hours of sleep`, `sleep tracker`, `sleep hours`, `sleep show`, `my sleep`, `track sleep`  
**Your words:** passed through untouched  
**Script:** `scripts/sleep_log.py`

### vaccine tracker

**Usage:** `add vaccine <person> <name> <date> | vaccines | remove vaccine <person> <name>`  
**What it does:** Keep vaccine due dates for the family (add vaccine asha polio 12 nov 2026, vaccines, remove vaccine asha polio)  
**Behaviour:** never saved in history.  
**Also found by:** `vaccine`, `vaccines`, `vaccination`, `add vaccine`, `vaccine due`, `vaccination schedule`, `shots due`, `booster due`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/vaccine_tracker.py`

### water log

**Usage:** `water log <amount> [ml|glasses|bottles] | water today | water goal <ml>`  
**What it does:** Log water you drank and see today's total; a glass is 250 ml, a bottle 500 ml (water log 500 ml, water log 2 glasses, water today, water goal 3000)  
**Also found by:** `log water`, `drank water`, `water intake`, `water today`, `how much water`, `water goal`, `hydration log`, `track water`  
**Your words:** passed through untouched  
**Script:** `scripts/water_log.py`

### weight log

**Usage:** `weight <kg> | weight history | weight goal <kg>`  
**What it does:** Log your weight and see the trend (weight 72.5 kg, weight history, weight goal 70)  
**Behaviour:** never saved in history.  
**Also found by:** `log weight`, `my weight`, `weigh in`, `weight history`, `weight goal`, `body weight`, `i weigh`  
**Your words:** passed through untouched  
**Script:** `scripts/weight_log.py`


## study

### add class

**Usage:** `add class <subject> <day> <time>`  
**What it does:** Add a weekly class or lesson (add class maths mon 9:00, add class physics tue 2:30 pm room 4)  
**Also found by:** `add lesson`, `timetable add`, `new class`, `add subject`, `class schedule`, `add period`, `add lecture`  
**Your words:** passed through untouched  
**Script:** `scripts/add_class.py`

### attendance percentage

**Usage:** `attendance <attended> of <total> [need <percent>]`  
**What it does:** Attendance percentage and classes you can skip (attendance 42 of 50; need 75)  
**Also found by:** `attendance`, `bunk`, `classes can i skip`, `minimum attendance`, `attendance calculator`  
**Your words:** passed through untouched  
**Script:** `scripts/attendance_percentage.py`

### cgpa to percentage

**Usage:** `cgpa <value> [out of 4]`  
**What it does:** Convert CGPA to percentage (cgpa 8.2 to percentage; cbse 9.4)  
**Also found by:** `cgpa`, `cgpa percentage`, `convert cgpa`, `sgpa to percentage`  
**Your words:** passed through untouched  
**Script:** `scripts/cgpa_to_percentage.py`

### flashcards

**Usage:** `flashcards [count] [file]`  
**What it does:** Spaced-repetition flashcards from a 'question | answer' file; cards you miss come back sooner (flashcards, flashcards 5 myfile.txt)  
**Also found by:** `flash cards`, `spaced repetition`, `revise cards`, `memorize`, `memory cards`, `leitner`, `learn cards`, `review cards`, `study cards`  
**Your words:** passed through untouched  
**Script:** `scripts/flashcards.py`

### gpa planner

**Usage:** `gpa planner current <gpa> credits <done> target <gpa> next <credits> [scale 10]`  
**What it does:** What you must score next to reach a target GPA (gpa planner current 3.2 credits 90 target 3.4 next 30)  
**Also found by:** `target gpa`, `gpa needed`, `required gpa`, `raise my gpa`, `what gpa do i need`, `cgpa target`  
**Your words:** passed through untouched  
**Script:** `scripts/gpa_planner.py`

### make citation

**Usage:** `cite <book|article|web> <author>; <title>; <year or source>; ...`  
**What it does:** Format a citation in APA and MLA (cite book Smith, John; Deep Learning; 2020; MIT Press)  
**Also found by:** `cite`, `citation`, `bibliography`, `apa citation`, `mla citation`, `reference format`, `cite book`, `cite website`, `make reference`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/make_citation.py`

### marks percentage

**Usage:** `marks <obtained> out of <total>`  
**What it does:** Percentage from marks (marks 432 out of 500)  
**Also found by:** `percentage of marks`, `marks to percentage`, `exam percentage`, `score percentage`  
**Your words:** passed through untouched  
**Script:** `scripts/marks_percentage.py`

### reading time

**Usage:** `reading time <file>`  
**What it does:** How long a text file or PDF takes to read (reading time notes.txt)  
**Behaviour:** reads piped text.  
**Also found by:** `how long to read`, `read time`, `minutes to read`, `word count and reading time`, `time to read`, `how long will it take to read`, `speaking time`  
**Your words:** passed through untouched  
**Script:** `scripts/reading_time.py`

### remove class

**Usage:** `remove class <subject> [day]`  
**What it does:** Remove a class from the timetable (remove class maths mon)  
**Also found by:** `delete class`, `drop class`, `remove lesson`, `delete subject`, `cancel class`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_class.py`

### show timetable

**What it does:** Show your weekly timetable  
**Also found by:** `my timetable`, `weekly schedule`, `class schedule`, `show classes`, `list classes`, `time table`, `weekly classes`  
**Script:** `scripts/show_timetable.py`

### study planner

**Usage:** `study plan <n> subjects <n> days <n> hours`  
**What it does:** Plan study hours per day (study plan 5 subjects 20 days 6 hours)  
**Also found by:** `study plan`, `plan my study`, `exam plan`, `revision plan`, `study schedule hours`  
**Your words:** passed through untouched  
**Script:** `scripts/study_planner.py`

### todays classes

**Usage:** `todays classes | tomorrows classes`  
**What it does:** Classes you have today or tomorrow (todays classes, tomorrows classes)  
**Also found by:** `classes today`, `tomorrow classes`, `tomorrows classes`, `what classes do i have`, `class today`, `schedule today`, `next class`, `lectures today`  
**Your words:** passed through untouched  
**Script:** `scripts/todays_classes.py`


## learning

### open coursera

**Usage:** `open coursera <words>`  
**What it does:** Open Coursera  
**Also found by:** `course`, `courses`, `learn`, `study`, `certificate`  
**Script:** `scripts/open_coursera.py`

### open duolingo

**What it does:** Open Duolingo  
**Also found by:** `language`, `learn language`, `practice`  
**Script:** `scripts/open_duolingo.py`

### open khanacademy

**Usage:** `open khanacademy <words>`  
**What it does:** Open Khan Academy  
**Also found by:** `study`, `learn`, `lessons`, `maths`, `science`  
**Script:** `scripts/open_khanacademy.py`

### open nptel

**What it does:** Open NPTEL  
**Also found by:** `courses`, `iit`, `learn`, `engineering`  
**Script:** `scripts/open_nptel.py`

### open udemy

**Usage:** `open udemy <words>`  
**What it does:** Open Udemy  
**Also found by:** `course`, `courses`, `learn`, `study`, `tutorial`  
**Script:** `scripts/open_udemy.py`


## media

### compress pdf

**Usage:** `compress pdf <file>`  
**What it does:** Make a PDF smaller (compress pdf big.pdf) - needs: pip install pypdf (Pillow shrinks pictures too)  
**Also found by:** `shrink pdf`, `reduce pdf size`, `pdf smaller`, `pdf too big`, `optimize pdf`, `make pdf lighter`  
**Your words:** passed through untouched  
**Script:** `scripts/compress_pdf.py`

### compress video

**Usage:** `compress video <file>`  
**What it does:** Make a video file smaller with ffmpeg (compress video movie.mp4)  
**Also found by:** `shrink video`, `reduce video size`, `make video smaller`, `video compress`, `small video`, `ffmpeg compress`  
**Your words:** passed through untouched  
**Script:** `scripts/compress_video.py`

### convert picture

**Usage:** `convert image <file> to <format>`  
**What it does:** Convert a picture to another format (convert image photo.png to jpg)  
**Also found by:** `convert image`, `image to jpg`, `png to jpg`, `jpg to png`, `webp to png`, `change image format`, `convert photo`, `image format`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/convert_picture.py`

### extract audio

**Usage:** `extract audio <video file>`  
**What it does:** Save the sound of a video as MP3 (extract audio movie.mp4)  
**Also found by:** `video to mp3`, `mp4 to mp3`, `get audio from video`, `rip audio`, `convert video to audio`, `save audio`  
**Your words:** passed through untouched  
**Script:** `scripts/extract_audio.py`

### merge pdf

**Usage:** `merge pdf <file> <file> ...`  
**What it does:** Join PDF files into one (merge pdf a.pdf b.pdf)  
**Also found by:** `combine pdf`, `join pdf`, `pdf merge`, `append pdf`, `put pdfs together`, `merge pdfs`  
**Your words:** passed through untouched  
**Script:** `scripts/merge_pdf.py`

### ocr text

**Usage:** `read text from <picture>`  
**What it does:** Read the text in a picture or screenshot (read text from scan.png; needs pip install pytesseract pillow and the Tesseract program)  
**Also found by:** `ocr`, `picture text`, `read text from picture`, `text from image`, `image to text`, `scan to text`, `read screenshot`, `extract text from image`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/ocr_text.py`

### pictures to pdf

**Usage:** `images to pdf <folder|files>`  
**What it does:** Combine pictures into one PDF (images to pdf <folder or files>)  
**Also found by:** `images to pdf`, `photos to pdf`, `jpg to pdf`, `make pdf from images`, `combine images into pdf`, `scan to pdf`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/pictures_to_pdf.py`

### render pdf

**Usage:** `pdf to images <file> [jpg] [<n> dpi]`  
**What it does:** Save each PDF page as a picture (pdf to images report.pdf; pdf to images report.pdf 200 dpi) - needs: pip install pypdfium2 Pillow  
**Also found by:** `pdf to png`, `pdf to jpg`, `render pdf pages`, `pdf screenshot`, `save pdf pages`  
**Your words:** passed through untouched  
**Script:** `scripts/render_pdf.py`

### resize picture

**Usage:** `resize image <file> to <width>`  
**What it does:** Resize a picture (resize image photo.jpg to 800 wide, or 50%)  
**Also found by:** `resize image`, `resize photo`, `shrink image`, `make image smaller`, `scale image`, `image width`, `reduce image size`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/resize_picture.py`

### rotate pdf

**Usage:** `rotate pdf <file> [90|180|270|left] [pages 1-3]`  
**What it does:** Rotate PDF pages (rotate pdf scan.pdf 90; rotate pdf scan.pdf 180 pages 1-3) - needs: pip install pypdf  
**Also found by:** `turn pdf`, `pdf rotate`, `flip pdf pages`, `sideways pdf`, `fix pdf orientation`  
**Your words:** passed through untouched  
**Script:** `scripts/rotate_pdf.py`

### screen text

**Usage:** `screen text`  
**What it does:** Take a screenshot, read the text in it and copy it to the clipboard (needs pillow, pytesseract and the Tesseract program)  
**Behaviour:** never saved in history.  
**Also found by:** `read my screen`, `text on my screen`, `copy text from screen`, `screen to text`, `screenshot to text`, `grab text from screen`  
**Script:** `scripts/screen_text.py`

### shrink photos

**Usage:** `compress pictures <folder> [quality 60] [width 1600]`  
**What it does:** Make every picture in a folder smaller into a new 'compressed' folder; originals untouched (compress pictures downloads, compress pictures trip quality 60 width 1600; needs pip install pillow)  
**Also found by:** `compress pictures`, `compress photos`, `compress images`, `reduce photo size`, `make photos smaller`, `bulk resize`, `batch compress`  
**Your words:** passed through untouched  
**Script:** `scripts/shrink_photos.py`

### split pdf

**Usage:** `split pdf <file> [pages 2-4]`  
**What it does:** Split a PDF into pages, or pull out some pages (split pdf report.pdf pages 2-4)  
**Also found by:** `extract pages`, `pdf pages`, `split pages`, `pdf split`, `take pages from pdf`, `separate pdf pages`  
**Your words:** passed through untouched  
**Script:** `scripts/split_pdf.py`

### watermark pdf

**Usage:** `watermark pdf <file> <text>`  
**What it does:** Stamp text across every PDF page (watermark pdf report.pdf CONFIDENTIAL) - needs: pip install pypdf  
**Also found by:** `stamp pdf`, `add watermark`, `pdf watermark`, `mark pdf draft`, `confidential stamp`  
**Your words:** passed through untouched  
**Script:** `scripts/watermark_pdf.py`


## fun

### guess number

**Usage:** `guess number [max]`  
**What it does:** Play 'guess the number' (guess number, or guess number 1000)  
**Also found by:** `guess the number`, `number game`, `guessing game`, `play guess`, `higher or lower`, `number guessing`  
**Your words:** passed through untouched  
**Script:** `scripts/guess_number.py`

### multiplication table

**Usage:** `multiplication table <n> [up to <m>]`  
**What it does:** Print a multiplication table (table of 7, multiplication table 12 up to 20)  
**Also found by:** `times table`, `table of`, `maths table`, `tables`, `print table`, `multiply table`, `pahada`  
**Your words:** passed through untouched  
**Script:** `scripts/multiplication_table.py`

### quiz notes

**Usage:** `quiz notes [file]`  
**What it does:** Quiz yourself from a notes file of 'question | answer' lines (quiz notes myfile.txt)  
**Also found by:** `quiz`, `quiz me`, `test myself`, `revision quiz`, `study quiz`, `practice questions`, `self test`  
**Your words:** passed through untouched  
**Script:** `scripts/quiz_notes.py`

### rock paper scissors

**What it does:** Play rock paper scissors against the computer  
**Also found by:** `rps`, `play rock paper`, `paper scissors`, `stone paper scissors`, `hand game`, `play rps`  
**Script:** `scripts/rock_paper_scissors.py`

### typing test

**What it does:** Test your typing speed and accuracy  
**Also found by:** `typing speed`, `wpm`, `test typing`, `how fast do i type`, `typing practice`, `words per minute`, `typing game`  
**Script:** `scripts/typing_test.py`


## text

### binary hex

**Usage:** `binary|hex|octal <number>`  
**What it does:** Convert a number between decimal, binary, hex and octal (binary 1010, hex ff, 255)  
**Also found by:** `binary`, `hex`, `hexadecimal`, `octal`, `decimal to binary`, `binary to decimal`, `hex to decimal`, `convert base`, `number base`, `bits`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/binary_hex.py`

### dedupe lines

**Usage:** `remove duplicates <items>`  
**What it does:** Remove duplicate lines or items, keeping the first (remove duplicates a, b, a, c)  
**Behaviour:** reads piped text.  
**Also found by:** `remove duplicates`, `dedupe`, `unique lines`, `duplicate lines`, `delete duplicates`, `remove repeated`, `uniq`, `unique items`, `remove repeats`  
**Your words:** passed through untouched  
**Script:** `scripts/dedupe_lines.py`

### lorem ipsum

**Usage:** `lorem ipsum [3 paragraphs|50 words]`  
**What it does:** Generate placeholder text (lorem ipsum 3 paragraphs, or 50 words)  
**Also found by:** `dummy text`, `placeholder text`, `filler text`, `sample text`, `fake text`, `random paragraph`, `lorem`  
**Your words:** passed through untouched  
**Script:** `scripts/lorem_ipsum.py`

### lowercase text

**Usage:** `lowercase <text>`  
**What it does:** lowercase some text (lowercase HELLO World)  
**Behaviour:** reads piped text.  
**Also found by:** `lowercase`, `lower case`, `small letters`, `make lowercase`, `to lowercase`, `no caps`, `all small`  
**Your words:** passed through untouched  
**Script:** `scripts/lowercase_text.py`

### number to words

**Usage:** `number to words <number>`  
**What it does:** Write a number in words, Indian and international style (number to words 1234567)  
**Also found by:** `write number in words`, `spell number`, `number in words`, `cheque amount in words`, `amount in words`, `say number`, `rupees in words`, `digits to words`  
**Your words:** passed through untouched  
**Script:** `scripts/number_to_words.py`

### qr code

**Usage:** `qr code <text or link>`  
**What it does:** Make a QR code picture from text or a link (qr code https://example.com)  
**Also found by:** `qrcode`, `make qr`, `generate qr`, `create qr code`, `qr for url`, `qr image`, `barcode`  
**Your words:** passed through untouched  
**Script:** `scripts/qr_code.py`

### readability score

**Usage:** `readability <text or file>`  
**What it does:** Reading level of a text or file (Flesch score and grade). Works with piped text.  
**Behaviour:** reads piped text.  
**Also found by:** `readability`, `reading level`, `flesch`, `grade level`, `how easy to read`, `reading ease`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/readability_score.py`

### reverse text

**Usage:** `reverse text <text>`  
**What it does:** Reverse text (reverse text hello)  
**Behaviour:** reads piped text.  
**Also found by:** `reverse string`, `flip text`, `backwards text`, `mirror text`, `text backwards`, `reverse words`  
**Your words:** passed through untouched  
**Script:** `scripts/reverse_text.py`

### roman numerals

**Usage:** `roman numeral <number|numeral>`  
**What it does:** Convert between Roman numerals and numbers (roman numeral 2026, or roman numeral MCMXC)  
**Also found by:** `roman numeral`, `to roman`, `from roman`, `roman number`, `convert roman`, `what is xiv`, `roman digits`  
**Your words:** passed through untouched  
**Script:** `scripts/roman_numerals.py`

### sort lines

**Usage:** `sort lines <items>`  
**What it does:** Sort a list alphabetically or by number (sort lines pear, apple, fig); add 'reverse' for Z-A  
**Behaviour:** reads piped text.  
**Also found by:** `sort list`, `alphabetical order`, `sort alphabetically`, `sort items`, `order list`, `sort names`, `sort numbers`, `sort words`  
**Your words:** passed through untouched  
**Script:** `scripts/sort_lines.py`

### title case text

**Usage:** `title case <text>`  
**What it does:** Title Case Some Text (title case the quick brown fox)  
**Behaviour:** reads piped text.  
**Also found by:** `title case`, `capitalize words`, `capitalise`, `title text`, `capitalize each word`, `make title`, `proper case`  
**Your words:** passed through untouched  
**Script:** `scripts/title_case_text.py`

### uppercase text

**Usage:** `uppercase <text>`  
**What it does:** UPPERCASE some text (uppercase hello world); with no text it uses the clipboard  
**Behaviour:** reads piped text.  
**Also found by:** `uppercase`, `upper case`, `capital letters`, `all caps`, `capitalize all`, `make uppercase`, `to uppercase`, `caps`  
**Your words:** passed through untouched  
**Script:** `scripts/uppercase_text.py`

### url decode

**Usage:** `url decode <text>`  
**What it does:** Turn a percent-encoded web address back into readable text (url decode hello%20world)  
**Behaviour:** reads piped text.  
**Also found by:** `percent decode`, `decode url`, `urldecode`, `decode percent`, `unescape url`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/url_decode.py`

### url encode

**Usage:** `url encode <text>`  
**What it does:** Make text safe for use in a web address (url encode hello world & more)  
**Behaviour:** reads piped text.  
**Also found by:** `percent encode`, `encode url`, `urlencode`, `encode for url`, `escape url`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/url_encode.py`

### word frequency

**Usage:** `word frequency <text|file>`  
**What it does:** Most common words in some text or a text file (word frequency notes.txt)  
**Behaviour:** reads piped text.  
**Also found by:** `most common words`, `word count by word`, `frequent words`, `top words`, `count each word`, `repeated words`, `which words repeat`  
**Your words:** passed through untouched  
**Script:** `scripts/word_frequency.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
