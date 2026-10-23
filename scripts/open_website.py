# keywords: website, site, url, link, visit, browse, go to, webpage, web page, address
# desc: Open any website (open website github.com)
# category: web
# usage: open website <address>
import re
from _lib import args_text, fail, open_url
u = (args_text().split() or [""])[0].strip("\"'<>")
if not u:
    fail("Usage: open website <address>   e.g. open website github.com")
if "://" not in u:
    u = "https://" + u
if not re.fullmatch(r"https?://[A-Za-z0-9.\-]+(:\d{1,5})?([/?#][^\s]*)?", u):
    fail("That does not look like a valid web address.")
open_url(u)
