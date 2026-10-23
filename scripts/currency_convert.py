# keywords: currency, exchange rate, forex, dollar, euro, rupee, usd, inr, convert currency, exchange, money exchange, rate today, dollar rate
# desc: Live currency conversion (currency 100 usd to inr) (needs internet)
# category: money
# usage: currency <amount> <from> to <to>
# rawargs: yes
from _lib import args_text, fail
from _money import currency_cli
if not currency_cli(args_text()):
    fail("Usage: currency <amount> <from> to <to>   e.g. currency 100 usd to inr")
