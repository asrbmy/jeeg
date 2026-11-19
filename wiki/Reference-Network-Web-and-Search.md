# Reference: Network, web, search and travel

Network checks, watching pages, feeds, looking things up, maps, travel, mail and the real browser.

74 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [network](#network), [web](#web), [search](#search), [maps](#maps), [travel](#travel), [info](#info), [email](#email), [links](#links), [browser](#browser)

## network

### check internet

**What it does:** Check whether the internet is working  
**Behaviour:** can use the internet.  
**Also found by:** `internet`, `connection`, `online`, `connected`, `offline`, `network`, `wifi working`, `net`  
**Script:** `scripts/check_internet.py`

### check speed

**What it does:** Test internet speed (Speedtest)  
**Behaviour:** can use the internet.  
**Also found by:** `speedtest`, `internet`, `bandwidth`, `wifi`, `mbps`, `download`, `upload`  
**Script:** `scripts/check_speed.py`

### check website

**Usage:** `check website <url>`  
**What it does:** Check if a website is up (check website github.com)  
**Behaviour:** can use the internet.  
**Also found by:** `website`, `site`, `up`, `down`, `status`, `is down`, `http`, `response`, `website status`, `uptime check`  
**Script:** `scripts/check_website.py`

### dns lookup

**Usage:** `dns lookup <domain>`  
**What it does:** Look up the IP addresses of a domain  
**Behaviour:** can use the internet.  
**Also found by:** `dns`, `lookup`, `resolve`, `domain`, `nslookup`, `ip of`, `ip address of website`  
**Script:** `scripts/dns_lookup.py`

### fleet check

**Usage:** `check all computers`  
**What it does:** Ask every saved computer (see "computer add") for its health at once: disk, memory, uptime. Needs JeeG and an ssh key on each.  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `check all computers`, `all my computers`, `status of all computers`, `check my servers`, `all machines`, `health of all computers`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/fleet_check.py`

### flush dns

**What it does:** Clear the DNS cache  
**Behaviour:** asks before running.  
**Also found by:** `clear dns`, `dns cache`, `reset dns`, `dns problem`  
**Script:** `scripts/flush_dns.py`

### listening ports

**What it does:** Show which programs are listening on network ports  
**Also found by:** `open ports`, `ports in use`, `listening`, `netstat`, `which ports`, `active ports`, `show ports`  
**Script:** `scripts/listening_ports.py`

### live network speed

**Usage:** `live network speed [seconds]`  
**What it does:** Watch your current download/upload speed for a few seconds (live network speed)  
**Also found by:** `network usage`, `bandwidth`, `download speed now`, `current speed`, `data usage now`, `upload speed now`, `network monitor`, `internet usage`  
**Your words:** passed through untouched  
**Script:** `scripts/live_network_speed.py`

### mqtt message

**Usage:** `mqtt add <name> <host[:port]> [user] | mqtt publish <name> <topic> <message> | mqtt listen <name> <topic> [seconds] | mqtt list | mqtt remove <name>`  
**What it does:** Send or listen to MQTT messages (mqtt add home 192.168.1.2, mqtt publish home lights/kitchen on, mqtt listen home sensors/#)  
**Behaviour:** can use the internet.  
**Also found by:** `mqtt`, `mqtt publish`, `mqtt listen`, `mqtt broker`, `send mqtt message`, `home assistant mqtt`, `iot message`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mqtt_message.py`

### network doctor

**Usage:** `network doctor`  
**What it does:** Find out why the internet is slow or down: checks your network, router, name lookup and the internet, then says what to try  
**Behaviour:** can use the internet.  
**Also found by:** `why is my internet slow`, `internet not working`, `wifi not working`, `diagnose network`, `fix my internet`, `network problem`, `no internet`, `wifi slow`  
**Script:** `scripts/network_doctor.py`

### peer jeeg

**Usage:** `peer add <name> <link from 'connect ai'> | peer run <name> <task> | peer list | peer remove <name>`  
**What it does:** Talk to a JeeG on another computer through its AI-mode link (peer add office <link>, peer run office disk space)  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `peer`, `other jeeg`, `jeeg peer`, `run on another jeeg`, `remote jeeg`, `jeeg to jeeg`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/peer_jeeg.py`

### ping host

**Usage:** `ping host <name or ip>`  
**What it does:** Ping a host (ping google.com)  
**Behaviour:** can use the internet.  
**Also found by:** `ping`, `latency`, `reachable`, `ping test`, `response time`, `is up`  
**Script:** `scripts/ping_host.py`

### port check

**Usage:** `port check <host> <port>`  
**What it does:** Check if a port is open (port check example.com 443)  
**Behaviour:** can use the internet.  
**Also found by:** `port`, `open port`, `tcp`, `listening`, `reachable port`, `connect`  
**Script:** `scripts/port_check.py`

### port owner

**Usage:** `who uses port <number>`  
**What it does:** Which program is using a port (who uses port 3000)  
**Also found by:** `who uses port`, `what is using port`, `which program uses port`, `port in use`, `what is on port`, `process on port`, `what is running on port`  
**Your words:** passed through untouched  
**Script:** `scripts/port_owner.py`

### rss feed

**Usage:** `feed add <url> [name] | feed list | feed remove <n> | read feeds [n]`  
**What it does:** Follow blogs and news sites by their RSS/Atom feed (feed add https://site/feed, read feeds, feed list, feed remove 2)  
**Behaviour:** can use the internet.  
**Also found by:** `rss`, `feed`, `news feed`, `add feed`, `read feeds`, `blog feed`, `subscribe`, `my feeds`, `feed list`, `atom`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/rss_feed.py`

### save page

**Usage:** `save page <url>`  
**What it does:** Save a web page as readable text for offline reading (save page https://example.com/article). Saved in Documents/JeeG pages.  
**Behaviour:** can use the internet.  
**Also found by:** `save web page`, `offline page`, `read later offline`, `download page text`, `archive page`, `save article`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/save_page.py`

### scan network

**Usage:** `who is on my wifi [scan]`  
**What it does:** List the devices on your home network (who is on my wifi). Add "scan" to wake the quiet ones first. Only your own private network.  
**Behaviour:** can use the internet.  
**Also found by:** `who is on my wifi`, `devices on my network`, `network devices`, `connected devices`, `find devices`, `who is connected to my wifi`, `lan scan`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/scan_network.py`

### share file

**Usage:** `send <file> to my phone`  
**What it does:** Send one file to your phone or another computer on the same Wi-Fi: shows a link and QR code, serves that one file once, then stops  
**Behaviour:** can use the internet.  
**Also found by:** `send file to phone`, `send file over wifi`, `file to phone`, `share with phone`, `qr download`, `transfer file to phone`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/share_file.py`

### show ip

**What it does:** Show your local and public IP address  
**Behaviour:** can use the internet.  
**Also found by:** `ip`, `address`, `my ip`, `public ip`, `local ip`, `ip address`, `hostname`  
**Script:** `scripts/show_ip.py`

### smart device

**Usage:** `device add <name> <shelly|tasmota> <ip> | device on|off|toggle|status <name> | device list | device remove <name>`  
**What it does:** Control smart plugs on your home network (device add lamp shelly 192.168.1.50, then: device on lamp / device off lamp / device status lamp)  
**Behaviour:** can use the internet.  
**Also found by:** `smart plug`, `device on`, `device off`, `shelly`, `tasmota`, `switch device`, `home device`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/smart_device.py`

### ssh hosts

**Usage:** `computer add <name> <user@host> | computer list | computer remove <name>`  
**What it does:** Save other computers you can reach with ssh (computer add pi pi@192.168.1.20), then run JeeG tasks on them  
**Also found by:** `host add`, `saved hosts`, `ssh host list`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/ssh_hosts.py`

### ssh task

**Usage:** `on <name> run <task>`  
**What it does:** Run a JeeG task on another computer over ssh (on pi run disk space). Needs JeeG there and an ssh key (no password prompts).  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `remote task`, `task on my pi`, `task on my server`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/ssh_task.py`

### ssl expiry

**Usage:** `ssl expiry <site>`  
**What it does:** Show how many days a site's https certificate has left (ssl expiry mysite.com)  
**Behaviour:** can use the internet.  
**Also found by:** `certificate expiry`, `ssl certificate`, `when does certificate expire`, `https certificate days left`, `check ssl`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/ssl_expiry.py`

### trace route

**Usage:** `trace route <host>`  
**What it does:** Trace the network route to a host  
**Behaviour:** can use the internet.  
**Also found by:** `traceroute`, `tracert`, `route`, `hops`, `path to`, `trace`  
**Script:** `scripts/trace_route.py`

### wake on lan

**Usage:** `wake <name | MAC address> | wake add <name> <MAC> | wake list | wake remove <name>`  
**What it does:** Turn on a computer on your network with a Wake-on-LAN packet (wake add nas AA:BB:CC:DD:EE:FF, then: wake nas)  
**Behaviour:** can use the internet.  
**Also found by:** `wake pc`, `wake computer`, `wake up pc`, `wake my nas`, `magic packet`, `power on pc over network`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/wake_on_lan.py`

### watch site

**Usage:** `watch page|price|site|ssl|release <target> [name] | watch list | watch remove <n> | check watches`  
**What it does:** Watch a web page, a price, a site being up, a certificate, or a GitHub release; "check watches" reports what changed (watch page https://x.com/news, watch price https://shop.com/item, watch site https://mysite.com, watch ssl mysite.com, watch release owner/repo)  
**Behaviour:** can use the internet.  
**Also found by:** `watch page`, `watch price`, `watch website`, `price drop`, `page changed`, `check watches`, `ssl watch`, `release watch`, `tell me when page changes`, `watch list`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/watch_site.py`

### webhook

**Usage:** `webhook add <name> <https address> | webhook send <name> <text> | webhook list | webhook remove <name>`  
**What it does:** Save web addresses (Slack, Discord, Zapier, n8n ...) and send them a message (webhook add team https://..., webhook send team deploy done)  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `post to webhook`, `send to slack`, `send to discord`, `notify webhook`, `zapier`, `ifttt`, `n8n`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/webhook.py`

### wifi info

**What it does:** Show the Wi-Fi network you are connected to  
**Also found by:** `wifi`, `wi-fi`, `ssid`, `wireless`, `signal`, `wifi name`, `which wifi`, `network name`  
**Script:** `scripts/wifi_info.py`


## web

### open browser

**What it does:** Open the default web browser  
**Also found by:** `web`, `surf`, `www`, `default`, `website`, `online`  
**Script:** `scripts/open_browser.py`

### open website

**Usage:** `open website <address>`  
**What it does:** Open any website (open website github.com)  
**Also found by:** `website`, `site`, `url`, `link`, `visit`, `browse`, `go to`, `webpage`, `web page`, `address`  
**Script:** `scripts/open_website.py`


## search

### cricket score

**Usage:** `cricket score [team]`  
**What it does:** Open live cricket scores (cricket score india, cricket score csk)  
**Also found by:** `live score`, `cricket`, `match score`, `ipl score`, `ipl`, `who is winning`, `test match score`, `cricket live`  
**Your words:** passed through untouched  
**Script:** `scripts/cricket_score.py`

### gold price

**Usage:** `gold price [city] | silver price [city]`  
**What it does:** Look up gold or silver rates (gold price, silver price delhi)  
**Also found by:** `gold rate`, `silver price`, `silver rate`, `price of gold`, `bullion`, `gold rate today`, `sone ka bhav`, `22 carat`, `24 carat`  
**Your words:** passed through untouched  
**Script:** `scripts/gold_price.py`

### search google

**Usage:** `search google <words>`  
**What it does:** Search Google (or open it)  
**Also found by:** `find`, `lookup`, `look up`, `web`, `google`  
**Script:** `scripts/search_google.py`

### search images

**Usage:** `search images <words>`  
**What it does:** Search Google Images  
**Also found by:** `pictures`, `photos`, `pics`, `image`  
**Script:** `scripts/search_images.py`

### search news

**Usage:** `search news <words>`  
**What it does:** Search Google News / latest headlines  
**Also found by:** `headlines`, `latest`, `current`, `events`  
**Script:** `scripts/search_news.py`

### search scholar

**Usage:** `search scholar <words>`  
**What it does:** Search Google Scholar for papers  
**Also found by:** `papers`, `research`, `academic`, `paper`, `journal`  
**Script:** `scripts/search_scholar.py`

### stock price

**Usage:** `stock price <company>`  
**What it does:** Look up a share price (stock price tcs, stock price apple)  
**Also found by:** `share price`, `stock quote`, `stocks`, `nse`, `bse`, `nifty`, `sensex`, `share market`, `market price of share`, `stock`  
**Your words:** passed through untouched  
**Script:** `scripts/stock_price.py`

### translate text

**Usage:** `translate text <words>`  
**What it does:** Translate text with Google Translate  
**Also found by:** `translator`, `translation`, `language`  
**Script:** `scripts/translate_text.py`


## maps

### get directions

**Usage:** `get directions <words>`  
**What it does:** Directions to a place in Google Maps  
**Also found by:** `route`, `navigate`, `navigation`, `direction`, `way`, `destination`  
**Script:** `scripts/get_directions.py`

### open maps

**Usage:** `open maps <words>`  
**What it does:** Open Google Maps or search a place  
**Also found by:** `map`, `location`, `place`, `nearby`, `search`, `navigate`, `where`  
**Script:** `scripts/open_maps.py`

### pharmacy near me

**Usage:** `pharmacy near me | pharmacy in <place>`  
**What it does:** Find a medical store or pharmacy near you or in a place (pharmacy near me)  
**Also found by:** `medical store`, `chemist`, `medicine shop`, `pharmacy`, `drugstore`, `chemist near me`, `medical shop nearby`, `medicine near me`  
**Your words:** passed through untouched  
**Script:** `scripts/pharmacy_near_me.py`

### restaurants near me

**Usage:** `restaurants near me | restaurants in <place>`  
**What it does:** Find restaurants near you or in a place (restaurants near me, restaurants in pune)  
**Also found by:** `restaurant`, `food near me`, `places to eat`, `nearby restaurants`, `where to eat`, `hotels near me food`, `cafes near me`, `eat nearby`  
**Your words:** passed through untouched  
**Script:** `scripts/restaurants_near_me.py`


## travel

### flight status

**Usage:** `flight status <number>`  
**What it does:** Check a flight's status (flight status 6E 204)  
**Also found by:** `flight tracker`, `track flight`, `is my flight on time`, `flight delayed`, `flight number`, `flight info`, `check flight`  
**Your words:** passed through untouched  
**Script:** `scripts/flight_status.py`

### open irctc

**What it does:** Open IRCTC train booking  
**Also found by:** `train`, `railway`, `ticket`, `book train`, `pnr`  
**Script:** `scripts/open_irctc.py`

### open makemytrip

**What it does:** Open MakeMyTrip  
**Also found by:** `flight`, `hotel`, `trip`, `travel`, `book`  
**Script:** `scripts/open_makemytrip.py`

### open uber

**What it does:** Open Uber  
**Also found by:** `cab`, `taxi`, `ride`, `book cab`  
**Script:** `scripts/open_uber.py`

### pnr status

**Usage:** `pnr status <10-digit pnr>`  
**What it does:** Check an Indian Railways PNR status (pnr status 1234567890)  
**Also found by:** `pnr`, `check pnr`, `ticket status`, `train ticket status`, `railway pnr`, `irctc pnr`, `booking status`, `waiting list status`  
**Your words:** passed through untouched  
**Script:** `scripts/pnr_status.py`

### train status

**Usage:** `train status <number>`  
**What it does:** Check a train's live running status (train status 12951)  
**Also found by:** `train running status`, `live train`, `where is my train`, `train live status`, `train delay`, `train tracker`, `track train`, `train number`  
**Your words:** passed through untouched  
**Script:** `scripts/train_status.py`

### trip budget

**Usage:** `trip budget <days> days <n> people <amount> a day [fare <amount>]`  
**What it does:** Estimate a trip budget (trip budget 4 days 2 people 3000 a day)  
**Also found by:** `travel budget`, `trip cost estimate`, `holiday budget`, `vacation budget`  
**Your words:** passed through untouched  
**Script:** `scripts/trip_budget.py`


## info

### check weather

**Usage:** `check weather <words>`  
**What it does:** Weather for a city (e.g. weather mumbai)  
**Also found by:** `weather`, `forecast`, `temperature`, `rain`, `climate`  
**Script:** `scripts/check_weather.py`

### daily quote

**What it does:** Show an inspiring quote  
**Also found by:** `quote`, `quotes`, `motivation`, `inspire`, `inspiration`, `motivate me`, `wisdom`, `quote of the day`, `thought of the day`  
**Script:** `scripts/daily_quote.py`

### define word

**Usage:** `meaning of <word>`  
**What it does:** Dictionary meaning in the terminal (meaning of ephemeral); opens Google if offline  
**Behaviour:** can use the internet.  
**Also found by:** `meaning`, `dictionary`, `definition`, `define`, `means`, `word meaning`, `what does`, `synonym`  
**Your words:** passed through untouched  
**Script:** `scripts/define_word.py`

### moon phase

**What it does:** Today's moon phase and the next new and full moon (moon phase)  
**Also found by:** `moon today`, `full moon`, `new moon`, `phase of the moon`, `is it a full moon`, `next full moon`, `purnima`, `amavasya`, `lunar phase`  
**Script:** `scripts/moon_phase.py`

### news headlines

**Usage:** `news headlines [topic]`  
**What it does:** Top news headlines in the terminal (news headlines, news cricket) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `news`, `headlines`, `latest`, `top stories`, `breaking`, `today news`, `current affairs`, `what is happening`  
**Your words:** passed through untouched  
**Script:** `scripts/news_headlines.py`

### pincode lookup

**Usage:** `pincode <PIN>`  
**What it does:** Look up an Indian PIN code (pincode 110001) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `pincode`, `pin code`, `postal code`, `zip`, `post office`, `postcode`, `area code`  
**Your words:** passed through untouched  
**Script:** `scripts/pincode_lookup.py`

### public holidays

**Usage:** `public holidays [country] [year] | next holiday`  
**What it does:** Public holidays for a country and year (public holidays india 2026, holidays in us)  
**Behaviour:** can use the internet.  
**Also found by:** `holidays`, `national holidays`, `bank holidays`, `holiday list`, `holiday calendar`, `next holiday`, `is it a holiday`, `government holidays`  
**Your words:** passed through untouched  
**Script:** `scripts/public_holidays.py`

### random fact

**What it does:** Show an interesting fact  
**Also found by:** `fact`, `facts`, `trivia`, `interesting`, `did you know`, `fun fact`, `tell me something`, `learn something`  
**Script:** `scripts/random_fact.py`

### sunrise sunset

**Usage:** `sunrise [city] [tomorrow|date]`  
**What it does:** Sunrise, sunset and day length for a city (sunrise delhi, sunset mumbai tomorrow)  
**Also found by:** `sunrise`, `sunset`, `sun rise`, `sun set`, `when does the sun rise`, `daylight hours`, `day length`, `sunrise time`, `sunset time`, `golden hour`  
**Your words:** passed through untouched  
**Script:** `scripts/sunrise_sunset.py`

### tell joke

**What it does:** Tell a clean joke  
**Also found by:** `joke`, `funny`, `laugh`, `make me laugh`, `humour`, `humor`, `cheer me up`  
**Script:** `scripts/tell_joke.py`

### weather report

**Usage:** `weather report [city]`  
**What it does:** Weather as text in the terminal (weather report mumbai) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `forecast`, `text weather`, `weather today`, `temperature`, `rain chance`, `humidity`  
**Your words:** passed through untouched  
**Script:** `scripts/weather_report.py`

### wiki summary

**Usage:** `wiki summary <topic>`  
**What it does:** Short Wikipedia summary (wiki summary einstein) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `wiki`, `wikipedia`, `summary`, `who is`, `what is`, `tell me about`, `about`, `encyclopedia`, `explain`  
**Your words:** passed through untouched  
**Script:** `scripts/wiki_summary.py`


## email

### compose email

**Usage:** `compose email <words>`  
**What it does:** Compose a Gmail message (words become the subject)  
**Also found by:** `write email`, `new email`, `send email`, `send mail`, `mail someone`, `draft`, `new mail`, `compose`  
**Script:** `scripts/compose_email.py`

### email to

**Usage:** `email <contact|address> [about <subject>]`  
**What it does:** Start an email to a saved contact or address (email mom about dinner)  
**Also found by:** `mail to`, `email mom`, `email address of`  
**Your words:** passed through untouched  
**Script:** `scripts/email_to.py`

### mail inbox

**Usage:** `mail inbox [how many]`  
**What it does:** Show your unread mail (sender, subject, date). Reads only the headers and marks nothing as read. Needs  mail setup.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `unread mail`, `unread emails`, `mail unread`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mail_inbox.py`

### mailbox post

**Usage:** `mail send <to> | <subject> | <body>`  
**What it does:** Send a mail from your saved account (mail send bob@example.com | Subject | Body). It asks first. Needs  mail setup.  
**Behaviour:** asks before running; can use the internet; never saved in history.  
**Also found by:** `post mail from my mailbox`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mailbox_post.py`

### mailbox setup

**Usage:** `mail setup <address> <imap host> <smtp host> | mail status | mail forget`  
**What it does:** Save your mail account for mail tasks (mail setup you@gmail.com imap.gmail.com smtp.gmail.com). Uses an app password, asked privately.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `mail setup`, `mail account`, `mail login`, `set up mail`, `mail forget`, `mail status`, `connect my mail`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mailbox_setup.py`

### open gmail

**What it does:** Open Gmail  
**Also found by:** `email`, `mail`, `inbox`, `google mail`, `check mail`  
**Script:** `scripts/open_gmail.py`


## links

### list links

**What it does:** List saved bookmarks  
**Also found by:** `show links`, `my links`, `bookmarks`, `saved links`, `show bookmarks`, `list bookmarks`, `my bookmarks`  
**Script:** `scripts/list_links.py`

### open link

**Usage:** `open link <name>`  
**What it does:** Open a saved bookmark by name (open link code)  
**Also found by:** `open bookmark`, `go to bookmark`, `saved link`, `my link`, `open saved`, `bookmark open`  
**Your words:** passed through untouched  
**Script:** `scripts/open_link.py`

### remove link

**Usage:** `remove link <name>`  
**What it does:** Delete a saved bookmark  
**Also found by:** `delete link`, `delete bookmark`, `remove bookmark`, `forget link`, `unsave link`  
**Your words:** passed through untouched  
**Script:** `scripts/remove_link.py`

### save link

**Usage:** `save link <url> <name>`  
**What it does:** Save a bookmark (save link github.com my code)  
**Also found by:** `bookmark`, `save bookmark`, `save url`, `save website`, `add link`, `add bookmark`, `remember link`  
**Your words:** passed through untouched  
**Script:** `scripts/save_link.py`


## browser

### browser do

**Usage:** `browser click <number> | browser type <number> <text> | browser press <key> | browser select <number> <option> | browser tick <number> | browser hover <number> | browser click text <words>  (add the word preview to only see what it would do)`  
**What it does:** Act on a page in the real browser, by the numbers that  browser look  shows (browser click 4, browser type 2 hello, browser press enter, browser select 3 Red, browser tick 5). Asks first.  
**Behaviour:** asks before running; can use the internet; never saved in history.  
**Also found by:** `browser click`, `browser type`, `browser press`, `browser select`, `browser tick`, `browser submit`, `click in browser`, `type in browser`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/browser_do.py`

### browser look

**Usage:** `browser open <address> | browser look | browser read | browser find <text> | browser tabs | browser tab <number> | browser newtab [address] | browser screenshot | browser back | browser forward | browser scroll down|up | browser wait <seconds> | browser wait for <text> | browser status`  
**What it does:** Look at websites in a real browser (browser open example.com, browser look, browser read, browser find price, browser tabs, browser screenshot, browser back). Nothing on the page is changed.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `browser open`, `browser read`, `browser find`, `browser tabs`, `browser screenshot`, `real browser`, `web browser`, `browse website`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/browser_look.py`

### browser setup

**Usage:** `browser start [hidden] | browser close | browser allow <site> | browser deny <site> | browser forget <site> | browser policy | browser secret <number> | browser upload <number> <file>`  
**What it does:** Set up the real browser (browser start, browser start hidden, browser close, browser allow example.com, browser deny example.com, browser policy, browser secret 3 to type a password yourself). You do this in a terminal.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `browser start`, `browser close`, `browser allow`, `browser deny`, `browser policy`, `browser secret`, `browser password`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/browser_setup.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
