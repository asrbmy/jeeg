# keywords: subscription, subscriptions, add subscription, renewal, subscription renewal, remove subscription, my subscriptions
# desc: Track subscriptions and renewal dates (add subscription netflix 15 dec 2026, subscriptions)
# category: home
# usage: add subscription <name> <date> | subscriptions | remove subscription <name>
# rawargs: full
# patterns: \bsubscriptions?\b ;; \brenewals?\b
# priority: 2
from _lib import args_text
from _dues import handle
handle("subscriptions.json", "subscription", args_text(), {"subscription", "subscriptions", "show", "list", "my", "all", "renewal", "renewals"}, "netflix 15 dec 2026")
