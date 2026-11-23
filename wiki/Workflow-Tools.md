# JeeG with workflow tools: n8n, Node-RED, Kestra, Prefect, Sim Studio and Python runners

Two directions. Use whichever the tool is better at.

| Direction | What happens | How |
|---|---|---|
| **A. The tool calls JeeG** | a workflow step runs a JeeG task (convert, hash, vault search, `device on lamp`...) and uses the answer | JeeG's local API: `jeeg --serve-api` |
| **B. JeeG calls the tool** | a JeeG task, scene or bridge rule starts a workflow (an n8n webhook, a Kestra flow, a Prefect run...) | `rest add` once, then `rest post` (asks first), or as a step in a scene or bridge rule |

## A. The tool calls JeeG
1. Keep this running on the computer: `jeeg --serve-api --only text,money,utility,time,notes`
   (`--only` is the list of kinds of task the workflow may run; add more only when you need them).
2. Get the token with `jeeg --api-token` and store it in the tool's own secret store (n8n credential, Node-RED
   environment variable, Kestra secret, Prefect Secret block). Never paste it into a workflow you share or export.
3. The request, the same in every tool:

       POST http://127.0.0.1:8766/v1/run
       Authorization: Bearer <token>
       {"query": "gst 2500 18"}          ->  {"ok": true, "result": {"output": "...", ...}}

   Exact name and arguments: `POST /v1/task` with `{"name": "gst_amount", "args": [2500, 18]}`.
Tasks that ask for confirmation are refused here, which is what you want in an unattended workflow.

**Important: the API listens on this computer only (127.0.0.1).** A tool running inside **Docker cannot reach it**
(`host.docker.internal` is not 127.0.0.1, and JeeG refuses other addresses on purpose). Choose one:
- run the tool directly on the computer (`npx n8n`, `npm i -g node-red`, `pip install prefect`, Kestra's standalone jar), or
- use the event route: the tool POSTs to a JeeG **bridge webhook** (`bridge add door when webhook 8790 then ...`, see
  `BRIDGE.md`), which listens on your network and is reachable from Docker. It can only run the short list of
  allowed bridge steps, not any task.

## B. JeeG calls the tool
    rest add n8n http://127.0.0.1:5678 none            (or: bearer / header X-Api-Key, asked privately)
    rest post n8n /webhook/<your-webhook-id> {"event":"backup done"}

The same line works as a scene or bridge step (`rest post ...`). Posting asks first unless a scene or rule you made runs it.
Redirects are never followed, so a key cannot be sent to another site. Address shapes:

| Tool | Address to save | Path to post to |
|---|---|---|
| n8n | `http://127.0.0.1:5678` | `/webhook/<id>` (production) or `/webhook-test/<id>` |
| Node-RED | `http://127.0.0.1:1880` | the URL of your *http in* node, e.g. `/jeeg` |
| Kestra | `http://127.0.0.1:8080` | `/api/v1/executions/webhook/<namespace>/<flow id>/<key>` (flow needs a Webhook trigger) |
| Prefect | `http://127.0.0.1:4200` | `/api/deployments/<deployment id>/create_flow_run` with `{}` |
| Sim Studio / any other | its address | its webhook or API path |

## What is in this folder
- `n8n/jeeg-run-task.json` import into n8n (Workflows > Import from file)
- `node-red/jeeg-flow.json` import into Node-RED (Menu > Import)
- `kestra/jeeg-run-task.yaml` paste into Kestra's flow editor
- `prefect/jeeg_flow.py` a Prefect flow (it also runs without Prefect installed)
- `python/jeeg_runner.py` a plain Python function for any Python job runner or scheduler
- `sim-studio/README.md` how to call JeeG from Sim Studio's API block

## Honest limits
Each file was checked for valid format and, for the Python and JSON parts, run against a live JeeG API. They were **not
imported into the real n8n, Node-RED, Kestra, Prefect or Sim Studio**; those tools change between versions, so a node or
field may need a small adjustment. "Pyunner" was not a name I could match to a tool: `python/jeeg_runner.py` works with
any Python runner. Tell me which one you meant and I will add it.
