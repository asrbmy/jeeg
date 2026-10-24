# keywords: journal prompt, writing prompt, what to write, diary prompt, journal idea, reflect, reflection question
# desc: Give a question to write about in your journal (journal prompt)
# category: journal
# usage: journal prompt
# patterns: \bjournal\s+prompt\b ;; \b(writing|diary)\s+prompt\b ;; \bwhat\s+(should\s+i|to)\s+write\b
# priority: 2
import datetime, random
P = ["What is one thing that went better than you expected today?", "Who helped you recently, and have you thanked them?",
     "What is taking more of your energy than it deserves?", "What would make tomorrow a good day, in one sentence?",
     "What did you learn this week that you want to remember?", "What are you avoiding, and what is the smallest first step?",
     "Describe a small moment today that you would like to keep.", "What are three things you are grateful for right now?",
     "What would you tell yourself a year ago?", "What do you want less of, and what do you want more of?",
     "What made you laugh recently?", "Which of your habits are helping you, and which are not?",
     "What is a worry you could let go of tonight?", "What is one thing you are proud of this month?"]
r = random.Random(datetime.date.today().toordinal())          # one prompt a day, the same all day
print(r.choice(P))
print("\nWrite your answer with:  journal add <your words>")
