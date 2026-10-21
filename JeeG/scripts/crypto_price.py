# keywords: crypto, bitcoin, btc, ethereum, eth, cryptocurrency, coin price, dogecoin, solana, coin, token price
# desc: Live cryptocurrency price (crypto price bitcoin) (needs internet)
# category: money
# usage: crypto price <coin>
# rawargs: yes
import re
from _lib import args_text, fail
from _money import inr
from _net import get
ALIAS = {"btc": "bitcoin", "eth": "ethereum", "sol": "solana", "xrp": "ripple", "doge": "dogecoin", "bnb": "binancecoin",
         "ada": "cardano", "ltc": "litecoin", "dot": "polkadot", "matic": "matic-network", "usdt": "tether", "ton": "the-open-network"}
words = [x for x in re.findall(r"[a-z0-9\-]+", args_text().lower()) if x not in ("price", "of", "the", "crypto", "coin", "rate", "today", "current")]
coin = ALIAS.get(words[0], words[0]) if words else "bitcoin"
d = get(f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd,inr&include_24hr_change=true", as_json=True)
if d is None:
    fail("Could not reach the price service (offline or rate-limited). Try again in a minute.")
if coin not in d:
    fail(f"Unknown coin '{coin}'. Use its CoinGecko name, e.g. bitcoin, ethereum, solana.")
c = d[coin]
print(f"{coin.title()}: ${c['usd']:,.2f}   INR {inr(c['inr'])}   (24h {c.get('usd_24h_change', 0):+.2f}%)")
