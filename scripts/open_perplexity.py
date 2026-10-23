# keywords: ai, answer, ask, search
# desc: Open Perplexity (or ask it)
# category: ai
# usage: open perplexity <words>
from _lib import web_task
web_task('https://www.perplexity.ai', 'https://www.perplexity.ai/search?q={q}')
