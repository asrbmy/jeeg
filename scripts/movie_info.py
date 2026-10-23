# keywords: movie info, imdb, movie rating, movie details, film info, cast of, movie reviews, show rating, web series info, find movie
# desc: Look up a movie or show on IMDb (movie info inception)
# category: entertainment
# usage: movie info <title>
# rawargs: yes
from _lib import args_text, open_url, search_url, fail
t = args_text()
if not t: open_url("https://www.imdb.com/")
else: open_url(search_url("https://www.imdb.com/find/?q={q}", t))
