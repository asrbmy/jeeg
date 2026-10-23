# keywords: discount, sale, off, price after discount, final price, savings, offer price, percent off, markdown, coupon
# desc: Price after discount(s) (discount 2000 30% off, discount 2000 30 10)
# category: money
# usage: discount <price> <percent> [more %]
# rawargs: yes
from _lib import args_text, fail
from _money import inr, numbers
n = numbers(args_text().lower().replace("%", " "))
if len(n) < 2 or any(x < 0 for x in n) or any(x > 100 for x in n[1:]):
    fail("Usage: discount <price> <percent off> [extra percent]   e.g. discount 2000 30% off")
price, price_now = n[0], n[0]
for d in n[1:]:
    price_now *= 1 - d / 100
print(f"Original : {inr(price)}")
print(f"Discount : {' then '.join(f'{d:g}%' for d in n[1:])}")
print(f"You pay  : {inr(price_now)}   (you save {inr(price - price_now)} = {100 * (price - price_now) / price if price else 0:.1f}%)")
