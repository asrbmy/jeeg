# keywords: color, colour, hex to rgb, rgb to hex, hsl, color converter, color code, convert color, hex color
# desc: Convert colours between hex, RGB and HSL (color #ff8800; color rgb 255 136 0; color hsl 32 100 50)
# category: developer
# usage: color <#hex | rgb r g b | hsl h s l>
# rawargs: full
# patterns: \b(hex|rgb|hsl)\s+(to|code|color)\b ;; ^\s*colou?r\s+(#|rgb|hsl|[0-9a-f]{6}\b) ;; \bcolou?r\s+(code|converter|convert)\b ;; #[0-9a-fA-F]{6}\b
# priority: 2
import colorsys, re
from _lib import args_text, fail
t = re.sub(r"\b(colou?r|convert|code|converter|to|of|the|hex)\b", " ", args_text().strip().lower())
nums = lambda s: [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", s)]
h = re.search(r"#([0-9a-f]{6}|[0-9a-f]{3})\b", t) or re.search(r"\b((?=[a-f]*\d)[0-9a-f]{6})\b", t)
if "rgb" in t and len(nums(t)) >= 3:
    r, g, b = (int(round(x)) for x in nums(t)[:3])
elif "hsl" in t and len(nums(t)) >= 3:
    hh, ss, ll = nums(t)[:3]
    if not (0 <= ss <= 100 and 0 <= ll <= 100):
        fail("Saturation and lightness are 0-100:  color hsl 32 100 50")
    r, g, b = (int(round(x * 255)) for x in colorsys.hls_to_rgb((hh % 360) / 360, ll / 100, ss / 100))
elif h:
    x = h.group(1)
    x = "".join(c * 2 for c in x) if len(x) == 3 else x
    r, g, b = (int(x[i:i + 2], 16) for i in (0, 2, 4))
elif len(nums(t)) == 3 and all(0 <= v <= 255 for v in nums(t)):
    r, g, b = (int(v) for v in nums(t))
else:
    fail("Usage: color #ff8800     color rgb 255 136 0     color hsl 32 100 50")
if not all(0 <= v <= 255 for v in (r, g, b)):
    fail("RGB values are 0 to 255.")
hh, ll, ss = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
def lum(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
L = 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b)
print(f"  Hex  : #{r:02x}{g:02x}{b:02x}")
print(f"  RGB  : rgb({r}, {g}, {b})")
print(f"  HSL  : hsl({hh * 360:.0f}, {ss * 100:.0f}%, {ll * 100:.0f}%)")
print(f"  Text contrast: white {1.05 / (L + 0.05):.1f}:1, black {(L + 0.05) / 0.05:.1f}:1  ({'use dark text' if L > 0.179 else 'use white text'}; 4.5:1 or more is readable)")
