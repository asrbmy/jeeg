"""Prefect flow that runs a JeeG task. Also works without Prefect installed (it then just runs as plain Python).

    jeeg --serve-api --only text,money,utility,time      (same computer as the worker)
    export JEEG_TOKEN=$(jeeg --api-token)                 (or store it in a Prefect Secret block and read it below)
    python jeeg_flow.py "convert 5 km to miles"

To start a Prefect run from JeeG:  rest add prefect http://127.0.0.1:4200 none
                                   rest post prefect /api/deployments/<deployment id>/create_flow_run {}
"""
import json
import os
import sys
import urllib.request

try:
    from prefect import flow, task
except ImportError:                                   # run as plain Python when Prefect is not installed
    def task(fn=None, **_):
        return fn if fn else (lambda f: f)
    flow = task


@task(retries=2, retry_delay_seconds=5)
def jeeg(query: str, port: int = 8766) -> str:
    token = os.environ.get("JEEG_TOKEN", "")
    if not token:
        raise RuntimeError("Set JEEG_TOKEN (from: jeeg --api-token)")
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/run", json.dumps({"query": query[:2000]}).encode(),
                                 {"Content-Type": "application/json", "Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if not d.get("ok"):
        raise RuntimeError(d.get("error", "JeeG refused"))
    res = d["result"]
    if res.get("needs_confirmation"):
        raise RuntimeError("That task asks for confirmation, so it cannot run in a workflow")
    return res.get("output", "")


@flow(name="jeeg-run-task")
def run_task(query: str = "convert 5 km to miles") -> str:
    answer = jeeg(query)
    print(answer)
    return answer


if __name__ == "__main__":
    run_task(" ".join(sys.argv[1:]) or "convert 5 km to miles")
