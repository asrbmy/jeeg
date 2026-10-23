# keywords: undo commit, undo last commit, git reset, uncommit, revert last commit, take back commit, git undo, remove last commit
# desc: Undo the last commit but keep your changes (git undo last commit)
# category: developer
# confirm: yes
import subprocess
from _lib import fail, call
def g(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()
if g("rev-parse", "--is-inside-work-tree")[0]: fail("This folder is not a git repository.")
if g("rev-parse", "HEAD~1")[0]: fail("There is no earlier commit to go back to.")
rc, pushed = g("branch", "-r", "--contains", "HEAD")
if rc == 0 and pushed: fail("That commit is already pushed (" + pushed.splitlines()[0].strip() + "). Undoing it would rewrite shared history; use 'git revert HEAD' yourself instead.")
print("Undoing:", g("log", "-1", "--format=%h %s")[1])
if call(["git", "reset", "--soft", "HEAD~1"]) == 0:
    print("Done. Your changes are still there, staged and ready to commit again.")
