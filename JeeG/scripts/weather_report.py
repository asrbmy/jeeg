# keywords: weather report, forecast, text weather, weather today, temperature, rain chance, humidity
# desc: Weather as text in the terminal (weather report mumbai) (needs internet)
# category: info
# usage: weather report [city]
# rawargs: yes
from _lib import args_text, fail
from _info import weather
city = " ".join(x for x in args_text().split() if x.lower() not in ("report", "in", "for", "of", "the", "today", "now", "weather", "forecast"))
r = weather(city)
if r is None: fail("Could not reach the weather service (offline?). Try again.")
if not r: fail("The weather service answered in an unexpected way. Try 'check weather' to use your browser.")
print(r)
