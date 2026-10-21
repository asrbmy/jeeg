# keywords: data, datasets, machine learning, ml, competition
# desc: Open Kaggle
# category: developer
# usage: open kaggle <words>
from _lib import web_task
web_task('https://www.kaggle.com', 'https://www.kaggle.com/search?q={q}')
