# keywords: uppercase, upper case, capital letters, all caps, capitalize all, make uppercase, to uppercase, caps
# desc: UPPERCASE some text (uppercase hello world); with no text it uses the clipboard
# category: text
# usage: uppercase <text>
# rawargs: yes
from _text import get_text, emit
emit(get_text().upper())
