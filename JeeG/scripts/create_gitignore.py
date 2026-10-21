# keywords: gitignore, create gitignore, add gitignore, git ignore file, ignore files, new gitignore, make gitignore
# desc: Create or extend a .gitignore for a language (create gitignore python | node | java)
# category: developer
# usage: create gitignore [python|node|java]
# rawargs: yes
from pathlib import Path
from _lib import args_text, fail
t = args_text().lower()
T = {
 "python": ["__pycache__/", "*.py[cod]", ".venv/", "venv/", "env/", "*.egg-info/", "dist/", "build/", ".pytest_cache/", ".mypy_cache/", ".ipynb_checkpoints/"],
 "node": ["node_modules/", "npm-debug.log*", "dist/", "build/", ".next/", "coverage/"],
 "java": ["*.class", "target/", "build/", ".gradle/", "*.jar"],
 "general": [".DS_Store", "Thumbs.db", ".idea/", ".vscode/", "*.log", ".env", ".env.*", "*.tmp"],
}
kinds = [k for k in T if k in t] or ["python" if Path("requirements.txt").exists() or any(Path.cwd().glob("*.py")) else "node" if Path("package.json").exists() else "general"]
want = [l for k in kinds + (["general"] if "general" not in kinds else []) for l in T[k]]
p = Path.cwd() / ".gitignore"
have = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
add = [l for l in dict.fromkeys(want) if l not in have]
if not add: print(".gitignore already has everything."); raise SystemExit(0)
with open(p, "a", encoding="utf-8") as f:
    if have and have[-1].strip(): f.write("\n")
    f.write("\n".join(add) + "\n")
print(f"{'Updated' if have else 'Created'} {p}: added {len(add)} line(s) for {', '.join(kinds)}.")
