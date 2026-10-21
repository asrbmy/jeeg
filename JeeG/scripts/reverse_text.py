# keywords: reverse text, reverse string, flip text, backwards text, mirror text, text backwards, reverse words
# desc: Reverse text (reverse text hello)
# category: text
# usage: reverse text <text>
# rawargs: yes
from _text import get_text, emit
emit(get_text()[::-1])
