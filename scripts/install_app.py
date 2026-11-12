# keywords: install app, install software, install program, install application, setup app, download and install, install chrome, install vlc, install vscode, install git
# desc: Install an app or program by name with your system's package manager (install vlc, install chrome and git; add "preview" to see the command only)
# category: system
# network: yes
# usage: install <app> [and <app> ...] [preview]
# confirm: yes
# rawargs: full
# patterns: ^\s*(?:please\s+)?(?:install|setup|set\s+up)\s+(?!(?:python\s+)?(?:package|packages|library|libraries|module|modules)\b)\S ;; \bdownload\s+and\s+install\b ;; \bget\s+me\s+(?:the\s+)?(?:app|software)\b
# priority: 3
from _apps import run_action
from _lib import args_text
raise SystemExit(run_action("install", args_text()))
