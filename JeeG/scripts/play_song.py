# keywords: play, song, songs, listen, track, music, put on, sing, play song, play music, by artist
# desc: Play a song: searches YouTube Music (or 'on spotify' / 'on youtube'); plain 'play' toggles play/pause
# category: entertainment
# usage: play <song name> [on spotify|youtube]
# rawargs: yes
# priority: 2
import re, urllib.parse
from _lib import args_text, open_url
t = args_text()
site = "ytmusic"
m = re.search(r"\s+(?:on|in|using|with)\s+(spotify|youtube music|youtube|yt music|jiosaavn|saavn)\s*$", t, re.I)
if m:
    s = m.group(1).lower()
    site = "spotify" if s == "spotify" else "youtube" if s == "youtube" else "saavn" if "saavn" in s else "ytmusic"
    t = t[:m.start()]
t = re.sub(r"^(?:the\s+)?(?:song|track|music|songs)\s+", "", t.strip(), flags=re.I).strip()
if not t:                                     # plain "play" -> toggle whatever is playing
    from _sys import media_key
    media_key("play"); print("Play/pause sent.")
elif t.lower() in {"music", "songs", "some music", "something"}:
    open_url("https://music.youtube.com")
else:
    q = urllib.parse.quote_plus(t)
    url = {"ytmusic": f"https://music.youtube.com/search?q={q}",
           "youtube": f"https://www.youtube.com/results?search_query={q}",
           "spotify": f"https://open.spotify.com/search/{urllib.parse.quote(t)}",
           "saavn": f"https://www.jiosaavn.com/search/{urllib.parse.quote(t)}"}[site]
    open_url(url)
    print(f"Searching for '{t}' - click the first result to play it.")
