# Sim Studio + JeeG

Sim Studio is a visual builder for AI-agent workflows. I could not test against it, so this is the generic recipe; field
names in its editor may differ slightly.

**Sim Studio calls JeeG** (Sim running on the same computer, not in Docker): add an **API / HTTP request** block:
- Method `POST`, URL `http://127.0.0.1:8766/v1/run`
- Headers: `Authorization: Bearer <token>` (use Sim's secret/environment variable store, not plain text) and `Content-Type: application/json`
- Body: `{"query": "<what to do>"}`; the answer is in `result.output` of the response.
- Start JeeG with `jeeg --serve-api --only text,money,utility,time` (add `notes` for Obsidian reading).

If an agent block decides what to ask, treat its text as untrusted: keep `--only` small and never use `--allow-confirm`.

**JeeG calls Sim Studio:** give the workflow a webhook/API trigger, then
`rest add sim http://127.0.0.1:3000 header X-API-Key` (asked privately) and `rest post sim <its trigger path> {"event":"..."}`.
