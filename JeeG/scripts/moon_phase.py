# keywords: moon phase, moon today, full moon, new moon, phase of the moon, is it a full moon, next full moon, purnima, amavasya, lunar phase
# desc: Today's moon phase and the next new and full moon (moon phase)
# category: info
import datetime
from _astro import moon_info, next_phase, SYNODIC
now = datetime.datetime.now(datetime.timezone.utc)
age, illum, name = moon_info(now)
print(f"{name}: about {illum * 100:.0f}% lit, {age:.1f} days into the cycle")
loc = lambda d: d.astimezone().strftime("%a %d %b %Y")
print(f"Next new moon:  about {loc(next_phase(now, 0.0))}")
print(f"Next full moon: about {loc(next_phase(now, SYNODIC / 2))}")
print("(simple calculation, correct to within about a day; official dates can differ slightly)")
