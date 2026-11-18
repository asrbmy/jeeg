# Use JeeG From Code

JeeG can be called by other programs four ways. Everything stays on your computer.

## 1. Python library

    pip install jeeg

    import jeeg
    r = jeeg.run("gst 2500 18")          # say it in words
    print(r.output)
    if r.ok: ...
    jeeg.gst_amount(1000, 18).output     # call a task by name
    jeeg.find("open youtube")            # which task would run (runs nothing)
    jeeg.tasks(category="money")         # jeeg.categories(), jeeg.task_info("gst_amount")
    j = jeeg.JeeG(home="my-data", timeout=30)
    j("add expense 250 food lunch")

- A `Result` has `.ok`, `.exit`, `.output`, `.lines`, `.task`, `.needs_confirmation`, `.ambiguous`, `.candidates`, `.json()`. `check=True` raises `JeeGError` on failure.
- Calls never prompt; confirmation tasks return exit code 3 unless `yes=True`.
- Library calls are not added to history (`history=True` to include).
- `run_task("name", args...)` skips word matching and is the predictable choice inside programs.
- Terminal-only commands (`web`, `setup`, `update`, `plugin` ...) are refused.
- Thread-safe (one call at a time); async helpers exist. Full guide: `PYTHON_GUIDE.md`.

## 2. `--json` (one call, any language)

    jeeg --json gst 2500 18

One JSON object: task, exit code, output. Add `--output result.txt` to save the output.

## 3. `--stdio` (many calls) and `--serve-api` (local HTTP)
- `jeeg --stdio`: JSON lines in, JSON lines out.
- `jeeg --serve-api`: local HTTP on 127.0.0.1 with a token; refuses web pages and other hosts. Browser extensions you name with `--allow-origin chrome-extension://<ID>` are the only origin accepted.
- Limit what a program may do: `--only`, `--except`, `--log`. Confirmation tasks are refused unless `--allow-confirm`.
- OpenAPI description: `integrations/openapi/jeeg-openapi.json`. Examples for Node.js, curl and Python in `examples/other_languages/`.

## 4. MCP (let AI apps use JeeG as a tool)
`jeeg --mcp` is an MCP server over stdio with tools `jeeg_run`, `jeeg_find`, `jeeg_list`, and for linked apps `jeeg_apps`, `jeeg_app_read`, `jeeg_app_do`. See [AI Mode and MCP](AI-Mode-and-MCP).

## Ready-made integrations (folder `integrations/`)
VS Code extension (starter), browser extension (select text, pick a task), Send To / right-click menu, Raycast and Alfred launchers, Home Assistant example, JavaScript client. Several are untested on real machines; each README says so.

Details: `INTEGRATIONS.md`, `PYTHON_GUIDE.md`.
