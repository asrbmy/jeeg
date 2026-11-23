# n8n + JeeG

**n8n calls JeeG:** Workflows > Import from file > `jeeg-run-task.json`. In the *Run on JeeG* node create a **Header Auth**
credential: Name `Authorization`, Value `Bearer <token>` (token from `jeeg --api-token`). Run `jeeg --serve-api --only text,money,utility,time`
first. Change the text in *What to ask JeeG*, or feed `query` from an earlier node (a webhook, a schedule, an email).
n8n must run directly on this computer, not in Docker (see `../README.md`).

**JeeG calls n8n:** make a workflow that starts with a **Webhook** node (POST), activate it, then in JeeG:

    rest add n8n http://127.0.0.1:5678 none
    rest post n8n /webhook/<the path shown on the Webhook node> {"event":"backup done"}
