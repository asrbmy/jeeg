# keywords: restaurants near me, restaurant, food near me, places to eat, nearby restaurants, where to eat, hotels near me food, cafes near me, eat nearby
# desc: Find restaurants near you or in a place (restaurants near me, restaurants in pune)
# category: maps
# usage: restaurants near me | restaurants in <place>
# rawargs: yes
import re
from _lib import args_text, open_url, search_url
t = re.sub(r"\b(restaurants?|near|me|nearby|in|around|food|places|to|eat|find|show)\b", " ", args_text(), flags=re.I).strip()
open_url(search_url("https://www.google.com/maps/search/restaurants+" + ("in+{q}" if t else "near+me"), t))
