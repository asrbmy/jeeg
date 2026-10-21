# keywords: quote, quotes, motivation, inspire, inspiration, motivate me, wisdom, quote of the day, thought of the day
# desc: Show an inspiring quote
# category: info
import random
ITEMS = ['The only thing we have to fear is fear itself. - Franklin D. Roosevelt', 'Well done is better than well said. - Benjamin Franklin', 'The journey of a thousand miles begins with a single step. - Lao Tzu', 'Imagination is more important than knowledge. - Albert Einstein', 'We are what we repeatedly do. Excellence, then, is not an act, but a habit. - Will Durant', 'Not all those who wander are lost. - J.R.R. Tolkien', 'Arise, awake, and stop not till the goal is reached. - Swami Vivekananda', "You miss 100% of the shots you don't take. - Wayne Gretzky", 'The best way to predict the future is to invent it. - Alan Kay', 'Dream is not that which you see while sleeping, it is that which does not let you sleep. - A. P. J. Abdul Kalam', 'Success is the sum of small efforts, repeated day in and day out. - Robert Collier', 'Stay hungry, stay foolish. - Stewart Brand (quoted by Steve Jobs)']
print(random.SystemRandom().choice(ITEMS))
