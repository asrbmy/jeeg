# keywords: packing list, pack for trip, trip checklist, travel checklist, what to pack
# desc: A packing checklist for a trip (packing list beach 4 days, packing list trek 3 days)
# category: personal
# usage: packing list <beach|trek|city|work> [days]
# rawargs: yes
import re
import sys

t = " ".join(sys.argv[1:]).lower()
d = re.search(r"(\d+)\s*(?:days?|nights?)?", t)
days = min(int(d.group(1)), 30) if d else 3
kind = next((k for k in ("beach", "trek", "hike", "city", "work", "business") if k in t), "city")
kind = {"hike": "trek", "business": "work"}.get(kind, kind)
base = ["Phone and charger", "Power bank", "Wallet, ID, cards", "Tickets and bookings", "Medicines", "Toothbrush and toiletries", "Water bottle"]
extra = {"beach": ["Swimwear", "Sunscreen", "Sunglasses and cap", "Light towel", "Slippers", "Waterproof pouch"],
         "trek": ["Trekking shoes", "Rain jacket", "Torch", "First-aid kit", "Energy snacks", "Extra socks", "Warm layer"],
         "city": ["Comfortable shoes", "Umbrella", "Earphones", "Small backpack"],
         "work": ["Laptop and charger", "Notebook and pens", "Formal clothes", "Visiting cards", "Adapter plug"]}[kind]
print(f"Packing list: {kind}, {days} day(s)")
for i in base + extra:
    print("  [ ] " + i)
print(f"  [ ] {days} sets of clothes" + (f" (+1 spare)" if days > 1 else ""))
print(f"  [ ] {days} sets of underwear and socks")
