# keywords: credit card due, card due, card payment due, add card, my cards, remove card, card bill date
# desc: Track credit card payment due dates (add card visa 15 nov, cards, remove card visa)
# category: money
# usage: add card <name> <date> | cards | remove card <name>
# rawargs: full
# patterns: \b(add|save)\s+(a\s+)?(credit\s+)?card\b ;; \bcredit\s+card\s+(due|bill|payment|dues)\b ;; ^\s*(my\s+)?cards\s*$ ;; \bremove\s+(credit\s+)?card\b
# priority: 2
from _lib import args_text
from _dues import handle
handle("card_dues.json", "card", args_text(), {"card", "cards", "credit", "show", "list", "my", "all", "due", "dues", "payment", "bill"}, "visa 15 nov")
