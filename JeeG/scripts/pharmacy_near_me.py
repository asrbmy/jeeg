# keywords: pharmacy near me, medical store, chemist, medicine shop, pharmacy, drugstore, chemist near me, medical shop nearby, medicine near me
# desc: Find a medical store or pharmacy near you or in a place (pharmacy near me)
# category: maps
# usage: pharmacy near me | pharmacy in <place>
# rawargs: yes
import re
from _lib import args_text, open_url, search_url
t = re.sub(r"\b(pharmacy|pharmacies|medical|store|shop|chemist|near|me|nearby|in|around|medicine|find|show|drugstore)\b", " ", args_text(), flags=re.I).strip()
open_url(search_url("https://www.google.com/maps/search/pharmacy+" + ("in+{q}" if t else "near+me"), t))
