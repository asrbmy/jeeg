"""Well-known MCP servers you can add by name:  mcp catalog   then   mcp add <name>.  Not a task itself.

Each entry was written from the project's own README. None of them was started from here (this computer has no access to them), so after adding one,
run  mcp tools <name>  to see what it really offers. "read" lists the tools that only look; you can change that with  mcp mark.
cmd: the program and arguments. {arg} is filled from what you type after the name. env: the variable that holds the login (see  mcp login).
"""
CATALOG = {
    "filesystem": {"cmd": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "{arg}"], "arg": "a folder it may use, e.g. ~/Documents", "env": "",
                   "read": ["read_file", "read_text_file", "read_media_file", "read_multiple_files", "list_directory", "list_directory_with_sizes", "directory_tree", "search_files", "get_file_info", "list_allowed_directories"],
                   "note": "read and write files inside one folder"},
    "fetch": {"cmd": ["uvx", "mcp-server-fetch"], "env": "", "read": ["fetch"], "note": "read a web page as text"},
    "memory": {"cmd": ["npx", "-y", "@modelcontextprotocol/server-memory"], "env": "", "read": ["read_graph", "search_nodes", "open_nodes"], "note": "a small notebook the AI keeps"},
    "thinking": {"cmd": ["npx", "-y", "@modelcontextprotocol/server-sequential-thinking"], "env": "", "read": ["sequentialthinking"], "note": "step-by-step thinking helper"},
    "time": {"cmd": ["uvx", "mcp-server-time"], "env": "", "read": ["get_current_time", "convert_time"], "note": "time and time zones"},
    "git": {"cmd": ["uvx", "mcp-server-git", "--repository", "{arg}"], "arg": "a git folder", "env": "",
            "read": ["git_status", "git_diff_unstaged", "git_diff_staged", "git_diff", "git_log", "git_show", "git_branch"], "note": "read a git repository (commits and branches can also be changed: those need your OK)"},
    "sqlite": {"cmd": ["uvx", "mcp-server-sqlite", "--db-path", "{arg}"], "arg": "a .db file", "env": "", "read": ["read_query", "list_tables", "describe_table"], "note": "a SQLite database"},
    "postgres": {"cmd": ["npx", "-y", "@modelcontextprotocol/server-postgres", "{arg}"], "arg": "postgresql://user:pass@host/db (the password is then in the saved command: prefer a read-only user)", "env": "",
                 "read": ["query"], "note": "a PostgreSQL database (read-only queries)"},
    "playwright": {"cmd": ["npx", "-y", "@playwright/mcp@latest"], "env": "", "read": [], "note": "drive a browser (every action needs your OK)"},
    "chrome-devtools": {"cmd": ["npx", "-y", "chrome-devtools-mcp@latest"], "env": "", "read": [], "note": "inspect and debug pages in Chrome"},
    "context7": {"cmd": ["npx", "-y", "@upstash/context7-mcp"], "env": "", "read": ["resolve-library-id", "get-library-docs", "query-docs"], "note": "current documentation for code libraries"},
    "kubernetes": {"cmd": ["npx", "-y", "mcp-server-kubernetes"], "env": "", "read": [], "note": "kubectl-style tools (uses your kubeconfig)"},
    "notion": {"cmd": ["npx", "-y", "@notionhq/notion-mcp-server"], "env": "NOTION_TOKEN", "read": [], "note": "Notion pages and databases; log in with an integration secret"},
    "supabase": {"cmd": ["npx", "-y", "@supabase/mcp-server-supabase@latest", "--read-only"], "env": "SUPABASE_ACCESS_TOKEN", "read": [], "note": "Supabase projects (started read-only)"},
    "figma": {"cmd": ["npx", "-y", "figma-developer-mcp", "--stdio"], "env": "FIGMA_API_KEY", "read": [], "note": "read Figma files"},
    "mongodb": {"cmd": ["npx", "-y", "mongodb-mcp-server", "--readOnly"], "env": "MDB_MCP_CONNECTION_STRING", "read": [], "note": "MongoDB (started read-only); log in with the connection string"},
    # more (2.20, second batch)
    "slack": {"cmd": ["npx", "-y", "@modelcontextprotocol/server-slack"], "env": "SLACK_BOT_TOKEN,SLACK_TEAM_ID", "read": ["slack_list_channels", "slack_get_channel_history", "slack_get_thread_replies", "slack_get_users", "slack_get_user_profile"], "note": "Slack channels and messages (JeeG's own Slack linked app is simpler for sending)"},
    "stripe": {"cmd": ["npx", "-y", "@stripe/mcp", "--tools=all"], "env": "STRIPE_SECRET_KEY", "read": [], "note": "Stripe; use a restricted key"},
    "shopify": {"cmd": ["npx", "-y", "@shopify/dev-mcp@latest"], "env": "", "read": [], "note": "Shopify developer documentation and API schema (not your store: use  app preset add shopify)"},
    "firebase": {"cmd": ["npx", "-y", "firebase-tools@latest", "mcp"], "env": "", "read": [], "note": "Firebase projects (uses your firebase login)"},
    "azure": {"cmd": ["npx", "-y", "@azure/mcp@latest", "server", "start"], "env": "", "read": [], "note": "Azure resources (uses your az login)"},
    "aws-docs": {"cmd": ["uvx", "awslabs.aws-documentation-mcp-server@latest"], "env": "", "read": [], "note": "AWS documentation (other AWS servers: see github.com/awslabs/mcp)"},
    "redis": {"cmd": ["uvx", "--from", "redis-mcp-server@latest", "redis-mcp-server", "--url", "{arg}"], "arg": "redis://localhost:6379/0", "env": "", "read": [], "note": "Redis"},
    "mysql": {"cmd": ["uvx", "--from", "mysql-mcp-server", "mysql_mcp_server"], "env": "MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE", "read": [], "note": "MySQL (use a read-only user)"},
    "neo4j": {"cmd": ["uvx", "mcp-neo4j-cypher@latest", "--transport", "stdio"], "env": "NEO4J_URI,NEO4J_USERNAME,NEO4J_PASSWORD", "read": ["get_neo4j_schema", "read_neo4j_cypher"], "note": "Neo4j graph database"},
    "qdrant": {"cmd": ["uvx", "mcp-server-qdrant"], "env": "QDRANT_URL,COLLECTION_NAME", "read": ["qdrant-find"], "note": "Qdrant vector search"},
    "grafana": {"cmd": ["mcp-grafana"], "env": "GRAFANA_URL,GRAFANA_API_KEY", "read": [], "note": "Grafana (needs the mcp-grafana program installed)"},
    "docker": {"cmd": ["uvx", "mcp-server-docker"], "env": "", "read": [], "note": "Docker (JeeG's own  app preset add docker  is stricter)"},
    "blender": {"cmd": ["uvx", "blender-mcp"], "env": "", "read": [], "note": "Blender (needs the Blender add-on running)"},
    "godot": {"cmd": ["npx", "-y", "@coding-solo/godot-mcp"], "env": "GODOT_PATH", "read": [], "note": "Godot; log in with the path of the Godot program"},
    # web servers (https): the login is sent as a bearer token
    "github": {"url": "https://api.githubcopilot.com/mcp/", "env": "@bearer", "read": [], "note": "GitHub's own MCP server; log in with a personal access token"},
    "context7-web": {"url": "https://mcp.context7.com/mcp", "env": "@bearer", "read": [], "note": "Context7 as a web server (login optional)"},
}
# Services with MCP servers that sign in through the AI app itself (OAuth in a browser). JeeG cannot do that sign-in, so these are not here:
REMOTE_ONLY = ("the hosted (OAuth) versions of Google Drive, Gmail, Google Calendar, Outlook, Asana, Box, Monday.com, Atlassian, Linear, Slack, Stripe, Cloudflare, Vercel, Canva, Spotify, X, "
               "Amplitude, Hex, Clay, Unity, Sentry and similar. Many of their plain APIs ARE here as linked apps: app preset list")
JEEG_HAS = "GitHub, GitLab, Bitbucket, Slack, Telegram, WhatsApp, Discord, Notion, Linear, Todoist, Jira, Confluence, Asana, Box, monday.com, Stripe, Shopify, Cloudflare, Vercel, Spotify, X, Salesforce, Grafana, Gmail, Google Drive, Google Calendar, Outlook, Home Assistant, docker, git, kubectl, adb are also JeeG linked apps (apps / app preset list)"
