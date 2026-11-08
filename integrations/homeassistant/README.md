# JeeG and Home Assistant (example, not tested here)

JeeG's local API only listens on 127.0.0.1, so this works when Home Assistant runs on the **same computer**
(for example Home Assistant Core in a venv). It does not work from a separate Home Assistant box or a Docker
container without extra network setup, and exposing the API to your network is not recommended.

1. Start the API with a limited task list and a log:

       jeeg --serve-api 8766 --only reminders,time,lists --log

2. Copy the token it prints into `secrets.yaml` as `jeeg_token: <token>`.
3. Add this to `configuration.yaml`:

       rest_command:
         jeeg_run:
           url: "http://127.0.0.1:8766/v1/run"
           method: POST
           headers:
             Authorization: "Bearer {{ states('input_text.jeeg_token') }}"
             Content-Type: "application/json"
           payload: '{"query": "{{ query }}"}'

   (Use your own way of storing the token; `!secret` cannot be used inside a template, so many people put the
   token directly in this file and keep the file private.)
4. Call it from an automation: `service: rest_command.jeeg_run` with `data: { query: "remind me in 10 minutes to check the oven" }`.

Tasks that ask for confirmation are refused unless you start the API with `--allow-confirm`; do not do that for Home Assistant.
