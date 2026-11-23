# JeeG for Claude Desktop and other MCP apps

JeeG is an MCP server. The quickest way is to let JeeG set it up:

    jeeg
    task> install mcp claude desktop          (shows what would change)
    task> install mcp claude desktop yes      (does it; the old settings file is saved as a backup)

Restart the app. It then has `jeeg_run`, `jeeg_find`, `jeeg_list` and the linked-app tools. By default the app can only
run tasks that cannot change anything important; `install mcp claude desktop read yes` adds look-only tasks and
`full yes` allows every task. See `../../MCP.md` for the list of supported apps.

If you prefer to edit the settings file yourself, `claude_desktop_config.example.json` is the entry to add under
`mcpServers`. If `jeeg` is not found by the app, use the full path from `where jeeg` (Windows) or `which jeeg`.

Claude.ai in the browser cannot start programs on your computer. Use `connect ai ask` (see `../../REMOTE_AI.md`).
