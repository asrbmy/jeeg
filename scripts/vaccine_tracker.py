# keywords: vaccine, vaccines, vaccination, add vaccine, vaccine due, vaccination schedule, shots due, booster due
# desc: Keep vaccine due dates for the family (add vaccine asha polio 12 nov 2026, vaccines, remove vaccine asha polio)
# category: health
# usage: add vaccine <person> <name> <date> | vaccines | remove vaccine <person> <name>
# rawargs: full
# private: yes
# patterns: \bvaccin(e|es|ation|ations)\b
# priority: 2
from _lib import args_text
from _dues import handle
handle("vaccines.json", "vaccine", args_text(), {"vaccine", "vaccines", "vaccination", "show", "list", "my", "all", "due"}, "asha polio 12 nov 2026")
