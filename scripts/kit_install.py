# keywords: kit install, install a kit, add someone else routines
# desc: Install a kit file made by 'kit export' (kit install file). Asks first; keeps anything you already have; check it first with 'kit show'
# category: routines
# usage: kit install <file>
# confirm: yes
# rawargs: full
# patterns: ^\s*kit\s+(install|import)\b
# priority: 4
import _kit
_kit.main({'install', 'import'})
