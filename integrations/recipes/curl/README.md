# Calling the local API

Start it (keep it open) and get the token:

    jeeg --serve-api --only text,money,utility,time
    jeeg --api-token

**curl** (macOS, Linux, Windows 10+)

    curl -s -H "Authorization: Bearer $TOKEN" -d '{"query":"gst 2500 18"}' http://127.0.0.1:8766/v1/run

**PowerShell**

    $t = jeeg --api-token
    Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8766/v1/run `
      -Headers @{ Authorization = "Bearer $t" } -ContentType "application/json" `
      -Body (@{ query = "gst 2500 18" } | ConvertTo-Json)

**Node.js** (18+)

    const r = await fetch("http://127.0.0.1:8766/v1/run", {
      method: "POST",
      headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" },
      body: JSON.stringify({ query: "gst 2500 18" }) });
    console.log((await r.json()).result.output);

Exact task name and arguments (no word matching): `POST /v1/task` with `{"name": "gst_amount", "args": [2500, 18]}`.
Every request and the full list of limits are in `../../../INTEGRATIONS.md` and `../../openapi/jeeg-openapi.json`.
