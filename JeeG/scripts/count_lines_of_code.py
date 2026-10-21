# keywords: lines of code, count lines, loc, code size, how many lines of code, count code lines, project size, lines in project, sloc
# desc: Count lines of code by language in a folder (lines of code myproject)
# category: developer
# usage: lines of code [folder]
# rawargs: yes
import os, re
from collections import Counter
from _lib import args_text
from _files import resolve_folder, walk_files
CODE = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".jsx": "JavaScript", ".tsx": "TypeScript", ".java": "Java", ".c": "C", ".h": "C", ".cpp": "C++", ".hpp": "C++",
        ".cs": "C#", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift", ".kt": "Kotlin", ".html": "HTML", ".css": "CSS", ".scss": "CSS",
        ".sh": "Shell", ".bat": "Batch", ".ps1": "PowerShell", ".sql": "SQL", ".json": "JSON", ".md": "Markdown", ".yml": "YAML", ".yaml": "YAML", ".r": "R", ".dart": "Dart", ".vue": "Vue"}
from _files import drop_tokens
folder = resolve_folder(drop_tokens(args_text(), {"in", "of", "for", "the", "folder", "project"}))
lines, blank, files = Counter(), Counter(), Counter()
for p, st in walk_files(folder, seconds=25):
    lang = CODE.get(os.path.splitext(p)[1].lower())
    if not lang or st.st_size > 5 * 1024 * 1024: continue
    try:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for l in f:
                if l.strip(): lines[lang] += 1
                else: blank[lang] += 1
        files[lang] += 1
    except OSError: continue
if not files: print("No code files found."); raise SystemExit(0)
print(f"{'Language':<12}{'Files':>7}{'Code lines':>12}{'Blank':>8}")
for lang, n in lines.most_common(): print(f"{lang:<12}{files[lang]:>7,}{n:>12,}{blank[lang]:>8,}")
print(f"{'Total':<12}{sum(files.values()):>7,}{sum(lines.values()):>12,}{sum(blank.values()):>8,}   (in {folder})")
