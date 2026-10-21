# keywords: cricket score, live score, cricket, match score, ipl score, ipl, who is winning, test match score, cricket live
# desc: Open live cricket scores (cricket score india, cricket score csk)
# category: search
# usage: cricket score [team]
# rawargs: yes
from _lib import web_task, args_text, open_url, search_url
t = args_text()
open_url(search_url("https://www.google.com/search?q=live+cricket+score+{q}", t) if t else "https://www.google.com/search?q=live+cricket+score")
