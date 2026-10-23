# keywords: url decode, percent decode, decode url, urldecode, decode percent, unescape url
# desc: Turn a percent-encoded web address back into readable text (url decode hello%20world)
# category: text
# usage: url decode <text>
# rawargs: full
# priority: 1
import re, urllib.parse
from _lib import args_text, fail
t = re.sub(r"^\s*(?:please\s+)?(?:url\s+)?(?:decode|unescape)\s+", "", args_text(), flags=re.I).strip("\"'")
if not t: fail("Usage: url decode <text>")
print(urllib.parse.unquote(t))
