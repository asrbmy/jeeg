# Reference: Developer tools

Git, projects, packages, data formats, HTTP, ports, containers and testing helpers.

68 tasks. Each entry shows the **usage** (`<x>` you fill in, `[x]` optional), what the task does, how it behaves, other words that also find it, and the script file you can read or edit. Say the task name, or the usage with your words filled in. `explain <words>` shows how any phrase is matched; `<task> preview` or `--dry-run` shows what would happen without doing it.

Categories on this page: [developer](#developer)

## developer

### check versions

**What it does:** Show installed versions of Python, Node, Git, Docker, Java  
**Also found by:** `versions`, `version`, `installed`, `check version`, `python version`, `node version`, `git version`, `java version`, `which version`, `tools installed`  
**Script:** `scripts/check_versions.py`

### color convert

**Usage:** `color <#hex | rgb r g b | hsl h s l>`  
**What it does:** Convert colours between hex, RGB and HSL (color #ff8800; color rgb 255 136 0; color hsl 32 100 50)  
**Also found by:** `color`, `colour`, `hex to rgb`, `rgb to hex`, `hsl`, `color converter`, `color code`, `convert color`, `hex color`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/color_convert.py`

### configure app

**Usage:** `configure git [name N] [email E] [branch B] | configure ssh key | configure vscode extension <id> | configure python project`  
**What it does:** Set up common tools: git name and email, an ssh key, a VS Code extension, a Python virtual environment (configure git name Ravi email r@x.com; add "preview" to see what would run)  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `configure git`, `setup git`, `git identity`, `git name email`, `setup ssh key`, `generate ssh key`, `create ssh key`, `vscode extension`, `python project setup`, `create virtual environment`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/configure_app.py`

### count lines of code

**Usage:** `lines of code [folder]`  
**What it does:** Count lines of code by language in a folder (lines of code myproject)  
**Also found by:** `lines of code`, `count lines`, `loc`, `code size`, `how many lines of code`, `count code lines`, `project size`, `lines in project`, `sloc`  
**Your words:** passed through untouched  
**Script:** `scripts/count_lines_of_code.py`

### create gitignore

**Usage:** `create gitignore [python|node|java]`  
**What it does:** Create or extend a .gitignore for a language (create gitignore python | node | java)  
**Also found by:** `gitignore`, `add gitignore`, `git ignore file`, `ignore files`, `new gitignore`, `make gitignore`  
**Your words:** passed through untouched  
**Script:** `scripts/create_gitignore.py`

### create venv

**What it does:** Create a Python virtual environment (.venv) here  
**Also found by:** `venv`, `virtual environment`, `virtualenv`, `python env`, `new environment`  
**Script:** `scripts/create_venv.py`

### cron explain

**Usage:** `cron <minute hour day month weekday>`  
**What it does:** Explain a cron schedule in words (cron 30 9 * * 1-5)  
**Also found by:** `cron`, `cron expression`, `crontab`, `cron schedule`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/cron_explain.py`

### csv preview

**Usage:** `csv preview <file.csv>`  
**What it does:** Show the first rows of a CSV file as a table (csv preview data.csv)  
**Also found by:** `preview csv`, `show csv`, `view csv`, `look at csv`, `csv head`, `csv columns`, `open csv in terminal`, `peek csv`  
**Your words:** passed through untouched  
**Script:** `scripts/csv_preview.py`

### csv summary

**Usage:** `csv summary <file.csv>`  
**What it does:** Summarise a CSV: rows, columns, number totals and common values (csv summary data.csv)  
**Also found by:** `summarise csv`, `csv stats`, `csv statistics`, `describe csv`, `analyse csv`, `csv totals`, `csv columns summary`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/csv_summary.py`

### docker ps

**What it does:** List running Docker containers  
**Also found by:** `docker`, `containers`, `running containers`, `docker status`  
**Script:** `scripts/docker_ps.py`

### docker stop all

**What it does:** Stop all running Docker containers  
**Behaviour:** asks before running.  
**Also found by:** `stop docker`, `stop containers`, `docker stop`, `stop all containers`, `docker down`  
**Script:** `scripts/docker_stop_all.py`

### env check

**Usage:** `env check [folder]`  
**What it does:** Compare a .env file with .env.example and list missing keys, without showing secrets (env check; env check myapp)  
**Behaviour:** never saved in history.  
**Also found by:** `dotenv`, `env file`, `missing env`, `check env`, `env example`, `environment variables file`, `env keys`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/env_check.py`

### env diff

**Usage:** `env diff <file1> <file2>`  
**What it does:** Compare two .env files and show which keys are missing or different, without printing the values (env diff .env.example .env)  
**Also found by:** `compare env files`, `compare dotenv`, `missing env variables`, `env file differences`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/env_diff.py`

### find todo

**Usage:** `find todo [folder]`  
**What it does:** List TODO, FIXME and HACK comments in a project folder (find todo myproject)  
**Also found by:** `find fixme`, `todo comments`, `list todos in code`, `fixme comments`, `leftover todo`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/find_todo.py`

### git branch

**What it does:** List git branches  
**Also found by:** `branches`, `which branch`, `current branch`, `list branches`  
**Script:** `scripts/git_branch.py`

### git checkout

**Usage:** `git checkout <branch> | git checkout new <branch>`  
**What it does:** Switch to a git branch, or create one (git switch main, git checkout new feature-x)  
**Also found by:** `switch branch`, `change branch`, `git switch`, `go to branch`, `new branch`, `create branch`, `checkout branch`  
**Your words:** passed through untouched  
**Script:** `scripts/git_checkout.py`

### git clone

**Usage:** `git clone <url>`  
**What it does:** Clone a repository (git clone https://github.com/user/repo)  
**Behaviour:** can use the internet.  
**Also found by:** `clone`, `download repo`, `clone repo`, `clone repository`, `copy repo`  
**Script:** `scripts/git_clone.py`

### git commit

**Usage:** `git commit <message>`  
**What it does:** Stage everything and commit (git commit fix login bug)  
**Behaviour:** asks before running.  
**Also found by:** `commit`, `save changes`, `commit all`, `commit message`  
**Your words:** passed through untouched  
**Script:** `scripts/git_commit.py`

### git contributors

**What it does:** Who has committed to this git project, and how much (git contributors)  
**Also found by:** `who committed`, `authors`, `git authors`, `top contributors`, `git shortlog`, `who wrote this`, `commits by author`, `project contributors`  
**Script:** `scripts/git_contributors.py`

### git diff

**What it does:** Summarise uncommitted git changes  
**Also found by:** `diff`, `changes summary`, `what changed`, `uncommitted`  
**Script:** `scripts/git_diff.py`

### git log

**What it does:** Show the last 10 git commits  
**Also found by:** `commits`, `history`, `recent commits`, `commit history`, `last commits`  
**Script:** `scripts/git_log.py`

### git pull

**What it does:** Pull the latest changes (fast-forward only)  
**Behaviour:** can use the internet.  
**Also found by:** `pull`, `update repo`, `sync`, `latest changes`, `fetch latest`  
**Script:** `scripts/git_pull.py`

### git push

**What it does:** Push commits to the remote  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `push`, `publish commits`, `upload commits`, `push code`  
**Script:** `scripts/git_push.py`

### git recent changes

**Usage:** `git recent changes [days]`  
**What it does:** What changed in this git project recently (git recent changes, git recent changes 14 days)  
**Also found by:** `git changes`, `what changed recently`, `recent commits`, `git whats new`, `changes this week`, `git activity`, `git history recent`, `latest changes`  
**Your words:** passed through untouched  
**Script:** `scripts/git_recent_changes.py`

### git stash

**Usage:** `git stash [pop|list|save <note>]`  
**What it does:** Stash or restore uncommitted changes (git stash, git stash pop, git stash list)  
**Also found by:** `stash changes`, `stash pop`, `stash list`, `save changes temporarily`, `shelve changes`, `put changes aside`, `restore stash`  
**Your words:** passed through untouched  
**Script:** `scripts/git_stash.py`

### git status

**What it does:** Show git status of the current folder  
**Also found by:** `git`, `status`, `changes`, `repo status`, `modified`, `what changed`  
**Script:** `scripts/git_status.py`

### git undo commit

**What it does:** Undo the last commit but keep your changes (git undo last commit)  
**Behaviour:** asks before running.  
**Also found by:** `undo commit`, `undo last commit`, `git reset`, `uncommit`, `revert last commit`, `take back commit`, `git undo`, `remove last commit`  
**Script:** `scripts/git_undo_commit.py`

### github inbox

**Usage:** `github login | github inbox | github issues <owner/repo> | github forget`  
**What it does:** See your GitHub notifications or a repo's open issues (github login, github inbox, github issues owner/repo). Token asked privately.  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `github notifications`, `github issues`, `github pull requests`, `my github`, `github login`, `github prs`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/github_inbox.py`

### http get

**Usage:** `http get <url>`  
**What it does:** Fetch a URL and show status, headers and the start of the body (http get https://example.com)  
**Behaviour:** can use the internet.  
**Also found by:** `http request`, `fetch url`, `curl`, `call api`, `test api`, `get request`, `check api response`, `fetch page`, `api test`  
**Your words:** passed through untouched  
**Script:** `scripts/http_get.py`

### json diff

**Usage:** `json diff <old.json> <new.json>`  
**What it does:** Compare two JSON files and list what changed (json diff a.json b.json)  
**Also found by:** `compare json`, `diff json`, `json difference`, `json changes`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/json_diff.py`

### json minify

**Usage:** `json minify <file.json>`  
**What it does:** Shrink a JSON file onto one line (json minify data.json)  
**Also found by:** `minify json`, `compact json`, `shrink json`, `json one line`, `compress json`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/json_minify.py`

### json to csv

**Usage:** `json to csv <file.json>`  
**What it does:** Convert a JSON file (a list of records) to CSV (json to csv data.json)  
**Also found by:** `convert json to csv`, `json csv`, `json file to spreadsheet`, `export json as csv`, `flatten json`  
**Your words:** passed through untouched  
**Script:** `scripts/json_to_csv.py`

### json to yaml

**Usage:** `json to yaml <file.json>`  
**What it does:** Convert a JSON file to YAML (json to yaml config.json)  
**Also found by:** `convert json to yaml`, `json yaml`, `make yaml from json`, `config to yaml`  
**Your words:** passed through untouched  
**Script:** `scripts/json_to_yaml.py`

### jwt decode

**Usage:** `jwt <token>`  
**What it does:** Read what is inside a JWT token, without sending it anywhere (jwt eyJ...)  
**Behaviour:** never saved in history.  
**Also found by:** `jwt`, `decode jwt`, `jwt token`, `json web token`, `read jwt`, `inspect token`  
**Your words:** passed through untouched  
**Script:** `scripts/jwt_decode.py`

### kill port

**Usage:** `kill port <number>`  
**What it does:** Stop whatever is listening on a port (kill port 3000)  
**Behaviour:** asks before running.  
**Also found by:** `free port`, `port in use`, `stop server`, `address already in use`, `close port`, `stop process on port`  
**Script:** `scripts/kill_port.py`

### log analyze

**Usage:** `log analyze <file>`  
**What it does:** Summarise a log file: counts by level, the most common errors, and the busiest minutes (log analyze app.log)  
**Also found by:** `analyze log`, `log summary`, `log errors`, `count errors in log`, `summarize log file`, `log file report`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/log_analyze.py`

### mcp call

**Usage:** `mcp call <name> <tool> [json arguments] [preview]`  
**What it does:** Use any tool of a saved MCP server (mcp call files write_file {"path": "a.txt", "content": "hi"}). Asks first. Add the word preview to see what would be sent.  
**Behaviour:** asks before running; can use the internet; never saved in history.  
**Also found by:** `call mcp tool`, `use mcp tool`, `run mcp tool`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mcp_call.py`

### mcp servers

**Usage:** `mcp catalog | mcp add <catalog name> [argument] | mcp add <name> = <command or https address> | mcp list | mcp tools <name> | mcp login <name> [ENV_VAR ...] | mcp logout <name> | mcp mark <name> <tool,tool> read|write | mcp remove <name>`  
**What it does:** Let JeeG use other MCP servers (mcp catalog, mcp add filesystem ~/Documents, mcp add files = npx some-server, mcp login <name>, mcp tools <name>, mcp mark <name> <tool> read)  
**Behaviour:** can use the internet; never saved in history.  
**Also found by:** `mcp add`, `mcp list`, `mcp catalog`, `mcp tools`, `mcp login`, `mcp mark`, `other ai tools`, `connect to mcp server`, `external tools`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/mcp_servers.py`

### new project

**Usage:** `new project <name> [python|node|html|flask]`  
**What it does:** Create a starter project folder (new project myapp python | node | html | flask)  
**Also found by:** `start project`, `create project`, `project template`, `scaffold`, `starter project`, `init project`, `boilerplate`, `new app`  
**Your words:** passed through untouched  
**Script:** `scripts/new_project.py`

### open codepen

**What it does:** Open CodePen  
**Also found by:** `html`, `css`, `javascript`, `playground`  
**Script:** `scripts/open_codepen.py`

### open dockerhub

**Usage:** `open dockerhub <words>`  
**What it does:** Open Docker Hub  
**Also found by:** `docker`, `container`, `image`  
**Script:** `scripts/open_dockerhub.py`

### open github

**Usage:** `open github <words>`  
**What it does:** Open GitHub or search it  
**Also found by:** `git`, `repo`, `repository`, `code`, `search`  
**Script:** `scripts/open_github.py`

### open gitlab

**What it does:** Open GitLab  
**Also found by:** `git`, `repo`, `repository`  
**Script:** `scripts/open_gitlab.py`

### open huggingface

**Usage:** `open huggingface <words>`  
**What it does:** Open Hugging Face  
**Also found by:** `ai models`, `models`, `datasets`, `ml`  
**Script:** `scripts/open_huggingface.py`

### open kaggle

**Usage:** `open kaggle <words>`  
**What it does:** Open Kaggle  
**Also found by:** `data`, `datasets`, `machine learning`, `ml`, `competition`  
**Script:** `scripts/open_kaggle.py`

### open leetcode

**Usage:** `open leetcode <words>`  
**What it does:** Open LeetCode  
**Also found by:** `coding`, `practice`, `problems`, `dsa`, `interview`  
**Script:** `scripts/open_leetcode.py`

### open localhost

**Usage:** `open localhost [port]`  
**What it does:** Open http://localhost:<port> in the browser  
**Also found by:** `localhost`, `local site`, `local host`, `dev server`, `open port`, `127.0.0.1`  
**Script:** `scripts/open_localhost.py`

### open mdn

**Usage:** `open mdn <words>`  
**What it does:** Open MDN Web Docs or search it  
**Also found by:** `javascript`, `html`, `css`, `web docs`, `documentation`  
**Script:** `scripts/open_mdn.py`

### open npm

**Usage:** `open npm <words>`  
**What it does:** Open npm or search Node packages  
**Also found by:** `node`, `package`, `javascript`, `library`  
**Script:** `scripts/open_npm.py`

### open pypi

**Usage:** `open pypi <words>`  
**What it does:** Open PyPI or search Python packages  
**Also found by:** `python`, `package`, `pip`, `library`  
**Script:** `scripts/open_pypi.py`

### open stackoverflow

**Usage:** `open stackoverflow <words>`  
**What it does:** Open Stack Overflow or search it  
**Also found by:** `programming`, `error`, `question`, `code`, `search`  
**Script:** `scripts/open_stackoverflow.py`

### open vscode here

**What it does:** Open the current folder in VS Code  
**Also found by:** `vscode here`, `code here`, `open project`, `open this folder`, `edit here`, `project in vscode`  
**Script:** `scripts/open_vscode_here.py`

### open w3schools

**What it does:** Open W3Schools  
**Also found by:** `html`, `css`, `tutorial`, `learn web`  
**Script:** `scripts/open_w3schools.py`

### pip install

**Usage:** `pip install <packages>`  
**What it does:** Install Python packages (pip install requests)  
**Behaviour:** asks before running; can use the internet.  
**Also found by:** `pip`, `install`, `python package`, `install package`, `install library`, `install module`  
**Script:** `scripts/pip_install.py`

### pip list

**What it does:** List installed Python packages  
**Also found by:** `installed packages`, `python packages`, `installed libraries`, `which packages`, `pip freeze`  
**Script:** `scripts/pip_list.py`

### pip outdated

**What it does:** List Python packages that have updates  
**Behaviour:** can use the internet.  
**Also found by:** `outdated`, `updates`, `upgradable`, `old packages`, `packages to update`  
**Script:** `scripts/pip_outdated.py`

### regex explain

**Usage:** `regex explain <pattern>`  
**What it does:** Explain a regular expression in plain words (regex explain ^\d{3}-\w+$)  
**Also found by:** `explain regex`, `regular expression explained`, `what does this regex do`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/regex_explain.py`

### regex tester

**Usage:** `regex test "<pattern>" on "<text>"`  
**What it does:** Try a regular expression on some text and see the matches (regex test "\d+" on "abc 123 def 45")  
**Also found by:** `regex test`, `test regex`, `regular expression`, `try regex`, `match pattern`, `regexp`, `check regex`, `find matches regex`, `pattern test`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/regex_tester.py`

### response headers

**Usage:** `http headers <url>`  
**What it does:** Show a website's response headers and which security headers it sets (http headers https://example.com) (needs internet)  
**Behaviour:** can use the internet.  
**Also found by:** `security headers`, `check headers`, `header inspector`, `hsts`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/response_headers.py`

### run tests

**What it does:** Run the tests of the project in this folder (run tests): pytest, unittest, npm, go or cargo is detected  
**Also found by:** `run the tests`, `test project`, `pytest`, `unit tests`, `npm test`, `run unittest`, `test my code`, `execute tests`, `check tests`  
**Script:** `scripts/run_tests.py`

### semver compare

**Usage:** `semver <version> vs <version>`  
**What it does:** Compare two version numbers the way package managers do (semver 1.2.3 vs 1.10.0)  
**Also found by:** `semver`, `compare versions`, `version compare`, `which version is newer`, `version greater than`, `compare semver`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/semver_compare.py`

### serve folder

**Usage:** `serve folder [port]`  
**What it does:** Serve the current folder at http://localhost:8000  
**Behaviour:** can use the internet.  
**Also found by:** `serve`, `http server`, `local server`, `web server`, `host folder`, `localhost server`, `preview site`  
**Script:** `scripts/serve_folder.py`

### show env variables

**Usage:** `env variables [filter]`  
**What it does:** List environment variables (secrets hidden); add a word to filter (env variables java)  
**Also found by:** `environment variables`, `env vars`, `env variable`, `show env`, `printenv`, `list env`, `show environment`, `environment`  
**Your words:** passed through untouched  
**Script:** `scripts/show_env_variables.py`

### show path

**What it does:** Show the folders in your PATH, one per line, marking missing ones  
**Also found by:** `path variable`, `print path`, `what is in path`, `path entries`, `system path`, `check path`, `my path`  
**Script:** `scripts/show_path.py`

### text diff

**Usage:** `text diff <file1> <file2>`  
**What it does:** Show the differences between two text files (text diff a.txt b.txt)  
**Also found by:** `diff files`, `difference between files`, `what changed between files`, `compare text files`, `file diff`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/text_diff.py`

### toml to json

**Usage:** `toml to json <file>`  
**What it does:** Convert a TOML file (such as pyproject.toml) to JSON (toml to json pyproject.toml). Needs Python 3.11 or newer.  
**Also found by:** `convert toml`, `toml json`, `read toml`, `pyproject json`, `toml file to json`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/toml_to_json.py`

### verify checksum

**Usage:** `verify checksum <file> <checksum>`  
**What it does:** Check a file against a checksum you were given (verify checksum setup.exe 9f86d0...)  
**Also found by:** `check hash`, `checksum matches`, `verify download`, `compare checksum`, `sha256 matches`, `is my download safe`  
**Your words:** the whole sentence is passed (quotes kept)  
**Script:** `scripts/verify_checksum.py`

### yaml to json

**Usage:** `yaml to json <file.yaml>`  
**What it does:** Convert a YAML file to JSON (yaml to json config.yaml)  
**Also found by:** `convert yaml to json`, `yml to json`, `yaml json`, `make json from yaml`  
**Your words:** passed through untouched  
**Script:** `scripts/yaml_to_json.py`


Back to [Home](Home) | [Task Catalog](Task-Catalog).
