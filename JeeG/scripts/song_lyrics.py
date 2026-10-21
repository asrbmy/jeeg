# keywords: lyrics, song lyrics, find lyrics, words of song, lyrics of, song words
# desc: Find the lyrics of a song (lyrics shape of you)
# category: entertainment
# usage: lyrics <song>
# rawargs: yes
from _lib import args_text, open_url, search_url, fail
t = args_text()
if not t: fail("Usage: lyrics <song name>")
open_url(search_url("https://www.google.com/search?q={q}+lyrics", t))
