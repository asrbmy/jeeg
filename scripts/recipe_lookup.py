# keywords: recipe, find recipe, how to cook, cooking, how to make food, dish recipe, ingredients for, cook, recipes
# desc: Find a recipe (recipe paneer butter masala)
# category: entertainment
# usage: recipe <dish>
# rawargs: yes
from _lib import args_text, open_url, search_url, fail
t = args_text()
if not t: fail("Usage: recipe <dish>")
open_url(search_url("https://www.google.com/search?q={q}+recipe", t))
