# keywords: kit share, kit export, kit show, share my routines
# desc: Share your routines, aliases and variables as one file, or look inside someone else's (kit export mykit, kit show file)
# category: routines
# usage: kit export <name> | kit show <file>
# rawargs: full
# patterns: ^\s*kit\s+(export|show)\b
# priority: 4
import _kit
_kit.main({'export', 'show'})
