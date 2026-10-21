# keywords: bmi, body mass index, bmi calculator, check bmi, my bmi, am i overweight, weight and height, ideal weight
# desc: Body mass index from weight and height (bmi 70 kg 175 cm, bmi 70 5 ft 9 in)
# category: health
# usage: bmi <weight> kg <height> cm
# rawargs: yes
import re
from _lib import args_text, fail
t = args_text().lower().replace("’", "'")
kg = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilos?|lb|lbs|pounds?)", t)
if not kg:
    nums = re.findall(r"\d+(?:\.\d+)?", t)
    kgv = float(nums[0]) if nums else None
    unit = "kg"
else:
    kgv, unit = float(kg.group(1)), kg.group(2)
if kgv is None: fail("Usage: bmi <weight> kg <height> cm      e.g. bmi 70 kg 175 cm   or   bmi 70 kg 5 ft 9 in")
if unit.startswith(("lb", "pound")): kgv *= 0.45359237
rest = t[:kg.start()] + " " + t[kg.end():] if kg else re.sub(r"\d+(?:\.\d+)?", "", t, count=1)
ft = re.search(r"(\d)\s*(?:ft|feet|foot|')\s*(\d{1,2})?\s*(?:in|inch|inches|\")?", rest)
cm = re.search(r"(\d+(?:\.\d+)?)\s*(cm|m|metres?|meters?)\b", rest)
if ft: h = (int(ft.group(1)) * 12 + int(ft.group(2) or 0)) * 0.0254
elif cm: h = float(cm.group(1)) / (100 if cm.group(2) == "cm" else 1)
else:
    n = re.findall(r"\d+(?:\.\d+)?", rest)
    h = (float(n[0]) / 100) if n else None
    if h is None: fail("I need a height too, e.g. bmi 70 kg 175 cm")
if not (0.5 <= h <= 2.6) or not (2 <= kgv <= 500): fail("Those numbers look wrong. Weight in kg or lb, height in cm, m or ft/in.")
b = kgv / (h * h)
cat = "underweight" if b < 18.5 else "normal range" if b < 25 else "overweight" if b < 30 else "obese range"
print(f"BMI {b:.1f}  ->  {cat} (WHO adult categories)   [{kgv:.1f} kg, {h * 100:.0f} cm]")
print("Healthy weight range for this height (BMI 18.5-24.9): %.1f - %.1f kg" % (18.5 * h * h, 24.9 * h * h))
print("Note: Asian and Indian health guidelines use lower cut-offs (overweight from 23). BMI is a rough screen, not a diagnosis; ask a doctor about your own health.")
