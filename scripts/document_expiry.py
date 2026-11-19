# keywords: document expiry, passport expiry, licence expiry, license expiry, add document, my documents, remove document, id expiry, document expires
# desc: Remember when passports, licences and IDs expire (add document passport 12 mar 2031, documents, remove document passport)
# category: lists
# usage: add document <name> <expiry date> | documents | remove document <name>
# rawargs: full
# patterns: ^\s*(add|save|renew|record)\s+(my\s+)?(document|passport|licen[cs]e|id\s+card)\b ;; ^\s*(my\s+)?documents?\s*(expiry|expire|expiring)?\s*$ ;; ^\s*remove\s+document\b ;; \b(passport|licen[cs]e|document)s?\s+(expiry|expires|expiring)\b
# priority: 2
from _lib import args_text
from _dues import handle
handle("documents.json", "document", args_text(), {"document", "documents", "show", "list", "my", "all", "expiry", "expires", "expiring", "expire", "date", "on"}, "passport 12 mar 2031")
