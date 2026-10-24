# keywords: vehicle dues, vehicle due, insurance due, puc due, pollution certificate, service due, car papers, bike insurance, vehicle log
# desc: Track insurance, pollution certificate and service dates (add vehicle due insurance bike 15 dec 2026, vehicle dues)
# category: home
# usage: add vehicle due <what> <date> | vehicle dues | remove vehicle due <what>
# rawargs: full
# patterns: \bvehicle\s+dues?\b ;; \b(bike|car|scooter)\s+(insurance|service|puc)\b ;; \b(insurance|puc|pollution\s+certificate)\s+due\b
# priority: 2
from _lib import args_text
from _dues import handle
handle("vehicle_dues.json", "vehicle due", args_text(), {"vehicle", "vehicles", "due", "dues", "show", "list", "my", "all"}, "insurance bike 15 dec 2026")
