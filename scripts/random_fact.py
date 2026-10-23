# keywords: fact, facts, trivia, interesting, did you know, fun fact, random fact, tell me something, learn something
# desc: Show an interesting fact
# category: info
import random
ITEMS = ['Octopuses have three hearts.', 'Botanically, bananas are berries, but strawberries are not.', 'A day on Venus is longer than a year on Venus.', 'Sharks have existed for longer than trees have.', 'Wombats produce cube-shaped droppings.', 'The Eiffel Tower can be about 15 cm taller in summer because the iron expands in the heat.', 'A lightning bolt is roughly five times hotter than the surface of the Sun.', 'At the triple point (0.01 C and very low pressure) water can exist as ice, liquid and vapour at once.', 'The Anglo-Zanzibar War of 1896 is the shortest recorded war: under an hour.', 'A group of flamingos is called a flamboyance.', 'Mount Everest is still rising by a few millimetres every year.', 'A solar day on Mercury lasts about 176 Earth days.']
print(random.SystemRandom().choice(ITEMS))
