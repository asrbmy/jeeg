# keywords: stock price, share price, stock quote, stocks, nse, bse, nifty, sensex, share market, market price of share, stock
# desc: Look up a share price (stock price tcs, stock price apple)
# category: search
# usage: stock price <company>
# rawargs: yes
from _lib import args_text, open_url, search_url, fail
t = args_text()
open_url(search_url("https://www.google.com/search?q={q}+share+price", t) if t else "https://www.google.com/finance/")
