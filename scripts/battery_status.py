# keywords: battery, charge, charging, power level, plugged, laptop
# desc: Show battery level and charging state
# category: system
from _sys import battery
b = battery()
print("No battery found (desktop PC?)." if not b else f"Battery: {b[0]}% ({b[1]})")
