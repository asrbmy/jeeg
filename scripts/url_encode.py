# keywords: url encode, percent encode, encode url, urlencode, encode for url, escape url
# desc: Make text safe for use in a web address (url encode hello world & more)
# category: text
# usage: url encode <text>
# rawargs: full
# priority: 1
# stdin: yes
import re, urllib.parse
from _lib import args_or_stdin, fail
t = re.sub(r"^\s*(?:please\s+)?(?:url\s+)?(?:encode|escape)\s+", "", args_or_stdin(), flags=re.I).strip("\"'")
if not t: fail("Usage: url encode <text>")
print(urllib.parse.quote(t, safe=""))
