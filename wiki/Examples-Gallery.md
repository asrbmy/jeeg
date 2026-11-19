# Examples Gallery

A gallery of one-liners with their **real output**, captured from JeeG 2.20.0 on 17 November 2026. Each group was run in a fresh temporary home. Anything that depends on the date, the time or chance (coin flips, random numbers, passwords, "days left") will differ when you run it. For the complete list of tasks see the [Task Catalog](Task-Catalog).

## Maths, units and tables

```text
task> 2 plus 2
>> calculate  (2 plus 2)
2 plus 2 = 4

task> sqrt 144
>> calculate  (sqrt 144)
sqrt 144 = 12

task> 15% of 200
>> calculate  (15% of 200)
15% of 200 = 30

task> calculate 2 ** 10
>> calculate  (2 ** 10)
2 ** 10 = 1,024

task> convert 5 kg to lb
>> convert units  (5 kg to lb)
5 kg = 11.0231 lb

task> cooking convert 2 cups flour to grams
>> cooking convert  (2 cups flour to grams)
2 cups flour = 250.8 grams
(approximate: ingredient weights vary with brand and how it is packed; US cup = 236.6 ml)

task> multiplication table 7 up to 10
>> multiplication table  (7 up to 10)
7 x  1 = 7
7 x  2 = 14
7 x  3 = 21
7 x  4 = 28
7 x  5 = 35
7 x  6 = 42
7 x  7 = 49
7 x  8 = 56
7 x  9 = 63
7 x 10 = 70
```

## Money helpers

```text
task> gst 2500 18
>> gst amount  (2500 18)
Add GST at 18%
  Base price : 2,500.00
  GST        : 450.00   (CGST 225.00 + SGST 225.00)
  Total      : 2,950.00

task> gst 1180 18 inclusive
>> gst amount  (1180 18 inclusive)
Price includes GST at 18%
  Base price : 1,000.00
  GST        : 180.00   (CGST 90.00 + SGST 90.00)
  Total      : 1,180.00

task> discount 2999 30
>> discount price  (2999 30)
Original : 2,999.00
Discount : 30%
You pay  : 2,099.30   (you save 899.70 = 30.0%)

task> split bill 2450 among 4 tip 10
>> split bill  (2450 among 4 tip 10)
Bill 2,450.00 + 10% tip = 2,695.00, split 4 ways
  Each person pays: 673.75

task> tip 1200 10% split 3
>> tip calculator  (1200 10% split 3)
Bill 1,200.00 + tip 10% (120.00) = total 1,320.00
Split 3 ways: 440.00 each

task> unit price 500g 45 vs 1kg 80
>> unit price  (500g 45 vs 1kg 80)
  1 kg for Rs 80               -> Rs 80.00 per kg
  500 g for Rs 45              -> Rs 90.00 per kg
Cheapest: 1 kg for Rs 80 (saves 11% per kg vs the dearest)

task> fuel cost 250 km 18 kmpl 105
>> fuel cost  (250 km 18 kmpl 105)
250 km at 18 km/l uses 13.89 litres.
Fuel cost at Rs 105/litre: Rs 1,458.33   (Rs 5.83 per km)
Round trip: Rs 2,916.67

task> profit margin cost 80 price 100
>> profit margin  (profit margin cost 80 price 100)
Cost 80.00, price 100.00
  Profit : 20.00
  Margin : 20.0%   (profit / price)
  Markup : 25.0%   (profit / cost)

task> hra basic 40000 hra 16000 rent 15000 metro
>> hra exemption  (hra basic 40000 hra 16000 rent 15000 metro)
  Actual HRA received            16,000.00
  Rent paid minus 10% of basic   11,000.00
  50% of basic                   20,000.00
Exempt HRA: 11,000.00 a month (1,32,000.00 a year). Taxable HRA: 60,000.00 a year.
(Old regime only. Basic means basic + DA. Rent above 1 lakh a year needs your landlord's PAN.)

task> salary breakup 1200000 a year tax 10 pension 12
>> salary breakup  (1200000 a year tax 10 pension 12)
Per month  (from 1,200,000.00 a year)
  Gross pay                              100,000.00
  Income tax (10%)                       -10,000.00
  Pension / retirement (12%)             -12,000.00
  Take-home                               78,000.00   (78.0% of gross; 936,000.00 a year)
  Rates are the ones you gave. This is an estimate, not payroll advice.
```

## Dates, time zones, sun and moon

Time-zone and astronomy tasks work **offline**: sunrise and moon phase are calculated (about 2 minutes and about a day of accuracy, as the output says).

```text
task> time in london and tokyo
>> world time  (time in london and tokyo)
London        Tue 17 Nov  11:56 AM   (GMT, UTC+0000)
Tokyo         Tue 17 Nov  08:56 PM   (JST, UTC+0900)

task> meeting time 9 am india in london
>> convert time zone  (meeting 9 am india in london)
Tue 17 Nov 09:00 AM in India (IST)
  = Tue 17 Nov 03:30 AM in London (GMT)

task> unix timestamp 1700000000
>> unix timestamp  (unix timestamp 1700000000)
2023-11-14 22:13:20 UTC   |   local: 2023-11-15 03:43:20 IST

task> what day is 25 dec 2026
>> weekday of  (what day is 25 dec 2026)
Friday, 25 December 2026  (day 359 of the year, ISO week 52)

task> days between 1 jan 2027 and 1 jan 2028
>> date difference  (days between 1 jan 2027 and 1 jan 2028)
01 Jan 2027 -> 01 Jan 2028
  365 days  (52 weeks 1 days)  =  1 years 0 months
  261 working days (Mon-Fri, public holidays not excluded)

task> sunrise delhi
>> sunrise sunset  (delhi)
Delhi, Tue 17 Nov 2026
  sunrise 06:46 AM   sunset 05:28 PM   daylight 10h 42m
  (calculated offline, accurate to about 2 minutes; places: Ahmedabad, Bangalore, Bengaluru, Berlin, Bhopal, Chandigarh, Chennai, Colombo... see _astro.py for the full list)

task> moon phase
>> moon phase
First quarter: about 52% lit, 7.6 days into the cycle
Next new moon:  about Wed 09 Dec 2026
Next full moon: about Tue 24 Nov 2026
(simple calculation, correct to within about a day; official dates can differ slightly)
```

## Small utilities

```text
task> flip coin
>> flip coin
Heads

task> roll 2d6
>> roll dice  (2d6)
2d6: [4, 5]  total 9

task> random number 1 100
>> random number  (1 100)
13   (between 1 and 100)

task> random choice pizza, burger, pasta
>> random choice  (pizza, burger, pasta)
-> burger

task> generate password 16
>> generate password  (16)
BrNIt_5Q#)QaPbCc

task> generate uuid
>> generate uuid
1992e3e8-a4fa-4df0-9bd0-ddeffd131099

task> count words the quick brown fox
>> count words  (quick brown fox)
Words: 3   Lines: 1   Characters: 15
```

## Health calculators

These are estimates with plain-language caveats, not medical advice.

```text
task> bmi 70 kg 175 cm
>> bmi calculator  (70 kg 175 cm)
BMI 22.9  ->  normal range (WHO adult categories)   [70.0 kg, 175 cm]
Healthy weight range for this height (BMI 18.5-24.9): 56.7 - 76.3 kg
Note: Asian and Indian health guidelines use lower cut-offs (overweight from 23). BMI is a rough screen, not a diagnosis; ask a doctor about your own health.

task> calorie calculator male 30 years 70 kg 175 cm moderate
>> calorie calculator  (male 30 years 70 kg 175 cm moderate)
Resting energy (BMR, Mifflin-St Jeor): about 1,649 kcal/day
With a 'moderate' activity level (x1.55): about 2,556 kcal/day to maintain weight
These are population estimates; real needs vary by person. For diet or medical decisions, ask a doctor or dietitian.

task> heart rate zones age 30
>> heart rate zones  (age 30)
Age 30: estimated maximum heart rate 190 beats a minute
  Easy / warm-up    95 - 114
  Fat burn         114 - 133
  Cardio           133 - 152
  Hard             152 - 171
  Maximum effort   171 - 190
  A rough estimate (220 minus age). Not medical advice.

task> macros 2200 high protein
>> macro split  (2200 high protein)
2200 kcal a day (high protein)
  Protein :   165 g  (30%)
  Carbs   :   220 g  (40%)
  Fat     :    73 g  (30%)
```

## Study helpers

```text
task> gpa planner current 7.5 credits 60 target 8 next 20 scale 10
>> gpa planner  (current 7.5 credits 60 target 8 next 20 scale 10)
Now 7.5 over 60 credits. To finish on 8 after 20 more credits (scale 10):
  You need an average of 9.50 in those 20 credits (95% of the maximum).

task> study plan 5 subjects 10 days 4 hours
>> study planner  (plan 5 subjects 10 days 4 hours)
5 subjects, 10 days, 4 h a day = 40 hours in all (8.0 h per subject)
  First 8 days: learn new topics, about 6.4 h on each subject
  Last 2 days: revision and past papers only
  Each day: about 1.3 h blocks, 3 subjects at most, with a 10 minute break every hour.

task> attendance 30 of 40 need 75
>> attendance percentage  (30 of 40 need 75)
Attendance: 30 of 40 = 75.0%  (minimum 75%)
  You can miss 0 more classes and stay at or above 75%.

task> cgpa 8.4 out of 10
>> cgpa to percentage  (8.4 out of 10)
CGPA 8.4/10 is about 79.8% (CBSE formula: CGPA x 9.5)
  Many universities use CGPA x 10 = 84.0% - check your own university's rule.

task> marks 412 out of 500
>> marks percentage  (412 out of 500)
412 out of 500 = 82.40%  (Distinction)
```

## Home, vehicles and trips

`warranties` and `vehicle dues` keep a soonest-first list with "in N days" and flag overdue items; `what is due` combines them with birthdays, bills, countdowns and missed medicine.

```text
task> electricity bill 250 units at 6.5 fixed 100
>> electricity bill  (250 units at 6.5 fixed 100)
250 units x 6.50 = 1,625.00
  Fixed charge   : 100.00
  Duty/tax (~5%) : 81.25   (varies by state)
  Estimated bill : 1,806.25
  Tip: a 1.5 ton AC used 8 h a day is roughly 400 units a month.

task> add warranty laptop 12 mar 2027
>> warranty tracker  (add warranty laptop 12 mar 2027)
Saved laptop: 12 Mar 2027 (in 115 day(s)).

task> warranties
>> warranty tracker  (warranties)
Warranty entries, soonest first:
  laptop                    2027-03-12  in 115 day(s)

task> add vehicle due insurance bike 15 dec 2026
>> vehicle dues  (add vehicle due insurance bike 15 dec 2026)
Saved insurance bike: 15 Dec 2026 (in 28 day(s)).

task> vehicle dues
>> vehicle dues  (vehicle dues)
Vehicle due entries, soonest first:
  insurance bike            2026-12-15  in 28 day(s)    soon

task> trip budget 4 days 2 people 3000 a day fare 8000
>> trip budget  (4 days 2 people 3000 a day fare 8000)
Trip: 4 days, 2 people
  On the ground (3,000.00 x 4 days x 2) : 24,000.00
  Fares / tickets                         : 8,000.00
  10% buffer for surprises                : 3,200.00
  Plan to carry                           : 35,200.00  (17,600.00 each)
```


Back to [Home](Home).
