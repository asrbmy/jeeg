# keywords: new project, start project, create project, project template, scaffold, starter project, init project, boilerplate, new app
# desc: Create a starter project folder (new project myapp python | node | html | flask)
# category: developer
# usage: new project <name> [python|node|html|flask]
# rawargs: yes
import json, re
from pathlib import Path
from _lib import args_text, fail
t = args_text().split()
kinds = {"python", "node", "html", "flask"}
kind = next((x.lower() for x in t if x.lower() in kinds), "python")
names = [x for x in t if x.lower() not in kinds and x.lower() not in ("a", "an", "called", "named", "project", "app")]
if len(names) != 1 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,60}", names[0]):
    fail("Usage: new project <name> [python|node|html|flask]   (letters, numbers, - _ . only)")
d = Path.cwd() / names[0]
if d.exists(): fail(f"{d} already exists.")
F = {
 "python": {"main.py": 'def main():\n    print("Hello from %s")\n\n\nif __name__ == "__main__":\n    main()\n' % names[0],
            "README.md": f"# {names[0]}\n\nRun: `python main.py`\n", ".gitignore": "__pycache__/\n.venv/\n*.pyc\n"},
 "node": {"package.json": json.dumps({"name": names[0].lower(), "version": "1.0.0", "main": "index.js", "scripts": {"start": "node index.js"}}, indent=2) + "\n",
          "index.js": f'console.log("Hello from {names[0]}");\n', "README.md": f"# {names[0]}\n\nRun: `npm start`\n", ".gitignore": "node_modules/\n"},
 "html": {"index.html": f'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>{names[0]}</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>{names[0]}</h1>\n  <script src="script.js"></script>\n</body>\n</html>\n',
          "style.css": "body { font-family: system-ui, sans-serif; margin: 2rem; }\n", "script.js": 'console.log("ready");\n'},
 "flask": {"app.py": 'from flask import Flask, render_template\n\napp = Flask(__name__)\n\n\n@app.route("/")\ndef home():\n    return render_template("index.html")\n\n\nif __name__ == "__main__":\n    app.run(debug=True)\n',
           "requirements.txt": "flask\n", "templates/index.html": f"<!doctype html>\n<title>{names[0]}</title>\n<h1>{names[0]}</h1>\n",
           "README.md": f"# {names[0]}\n\n    pip install -r requirements.txt\n    python app.py\n", ".gitignore": "__pycache__/\n.venv/\n"},
}[kind]
for rel, text in F.items():
    p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
print(f"Created {kind} project at {d}:")
for rel in F: print("  " + rel)
