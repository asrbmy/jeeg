# keywords: weather, forecast, temperature, rain, climate
# desc: Weather for a city (e.g. weather mumbai)
# category: info
# usage: check weather <words>
from _lib import web_task
web_task('https://www.google.com/search?q=weather', 'https://www.google.com/search?q=weather+{q}')
