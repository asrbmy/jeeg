# keywords: warranty, warranties, add warranty, warranty expiry, warranty ends, show warranties, guarantee expiry
# desc: Keep warranty end dates and see what expires soon (add warranty laptop 12 mar 2027, warranties, remove warranty laptop)
# category: home
# usage: add warranty <item> <date> | warranties | remove warranty <item>
# rawargs: full
# patterns: \bwarrant(y|ies)\b
# priority: 2
from _lib import args_text
from _dues import handle
handle("warranties.json", "warranty", args_text(), {"warranty", "warranties", "show", "list", "my", "all"}, "laptop 12 mar 2027")
