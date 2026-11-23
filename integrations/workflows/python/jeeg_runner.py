"""Call JeeG from any Python job runner, scheduler or script. Standard library only.

    from jeeg_runner import jeeg
    print(jeeg("gst 2500 18"))
    print(jeeg("vault search beta launch"))

Needs:  jeeg --serve-api --only text,money,utility,time,notes   and the token in the JEEG_TOKEN environment variable
(from: jeeg --api-token). Tasks that ask for confirmation are refused.
"""
import json
import os
import urllib.request


def jeeg(query: str, port: int = 8766, timeout: int = 60) -> str:
    token = os.environ.get("JEEG_TOKEN", "")
    if not token:
        raise RuntimeError("Set JEEG_TOKEN (from: jeeg --api-token)")
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/run", json.dumps({"query": query[:2000]}).encode(),
                                 {"Content-Type": "application/json", "Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    if not d.get("ok"):
        raise RuntimeError(d.get("error", "JeeG refused"))
    res = d["result"]
    if res.get("needs_confirmation"):
        raise RuntimeError("That task asks for confirmation, so it cannot run unattended")
    return res.get("output", "")
