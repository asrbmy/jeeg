# keywords: uninstall app, remove app, uninstall software, remove program, uninstall program, delete app
# desc: Uninstall an app by name with your system's package manager (uninstall vlc; add "preview" to see the command only)
# category: system
# usage: uninstall <app> [preview]
# confirm: yes
# rawargs: full
# patterns: ^\s*(?:please\s+)?(?:uninstall|remove)\s+(?:the\s+)?(?:app|application|software|program)\s+\S ;; ^\s*uninstall\s+(?!history\b)\S
# priority: 3
from _apps import run_action
from _lib import args_text
raise SystemExit(run_action("uninstall", args_text()))
