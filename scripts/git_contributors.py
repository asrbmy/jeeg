# keywords: git contributors, who committed, authors, git authors, top contributors, git shortlog, who wrote this, commits by author, project contributors
# desc: Who has committed to this git project, and how much (git contributors)
# category: developer
from _lib import call
raise SystemExit(call(["git", "shortlog", "-sne", "HEAD"]))
