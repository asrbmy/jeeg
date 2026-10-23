# keywords: calorie calculator, calories, bmr, daily calories, calories needed, maintenance calories, tdee, how many calories do i burn, metabolic rate
# desc: Estimate daily calories you burn (calorie calculator male 30 years 70 kg 175 cm moderate)
# category: health
# usage: calorie calculator <male|female> <age> years <kg> kg <cm> cm [activity]
# rawargs: yes
import re
from _lib import args_text, fail
t = args_text().lower()
sex = "m" if re.search(r"\b(male|man|boy|m)\b", t) else "f" if re.search(r"\b(female|woman|girl|f)\b", t) else None
age = re.search(r"(\d{1,3})\s*(?:years?|yrs?|y|yo)\b", t)
kg = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilos?)\b", t)
cm = re.search(r"(\d+(?:\.\d+)?)\s*cm\b", t)
if not (sex and age and kg and cm):
    fail("Usage: calorie calculator <male|female> <age> years <weight> kg <height> cm [sedentary|light|moderate|active|very active]")
a, wkg, hcm = int(age.group(1)), float(kg.group(1)), float(cm.group(1))
if not (10 <= a <= 100 and 20 <= wkg <= 300 and 100 <= hcm <= 250): fail("Those numbers look out of range.")
bmr = 10 * wkg + 6.25 * hcm - 5 * a + (5 if sex == "m" else -161)
lv = [("very active", 1.9), ("sedentary", 1.2), ("light", 1.375), ("moderate", 1.55), ("active", 1.725)]
name, mult = next(((n, m) for n, m in lv if n in t), ("light", 1.375))
print(f"Resting energy (BMR, Mifflin-St Jeor): about {bmr:,.0f} kcal/day")
print(f"With a '{name}' activity level (x{mult}): about {bmr * mult:,.0f} kcal/day to maintain weight")
print("These are population estimates; real needs vary by person. For diet or medical decisions, ask a doctor or dietitian.")
