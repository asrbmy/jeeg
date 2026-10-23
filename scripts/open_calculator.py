# keywords: calc, calculator, math, calculate
# desc: Open the calculator
# category: apps
from _lib import launch
launch(win=[('calc',)], mac=[('open', '-a', 'Calculator')], linux=[('gnome-calculator',), ('kcalc',), ('galculator',), ('mate-calc',), ('xcalc',)], name='a calculator')
