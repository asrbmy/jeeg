# JeeG for ChatGPT, OpenAI tools and Gemini

There are three different ways to do this. Pick by where the model runs.

## A. Your own program using OpenAI or Gemini function calling
`tools.json` is the OpenAI "tools" list (`jeeg_find`, `jeeg_run`). `gemini-tools.json` is the same for the Gemini API.
Your program sends them with the chat request; when the model asks for a tool you call JeeG (for example
`POST http://127.0.0.1:8766/v1/run`, see `../../INTEGRATIONS.md`) and return the answer.

The ready-made version is `../local/jeeg_chat.py`:

    set OPENAI_API_KEY=...            (macOS/Linux: export OPENAI_API_KEY=...)
    python jeeg_chat.py --openai --model <a model you have access to>
    python jeeg_chat.py --gemini --model <a Gemini model name>   (key in GEMINI_API_KEY)

**Your questions and JeeG's answers are sent to OpenAI or Google** when you do this. The script says so each time.
JeeG still only runs the kinds of task you allow with `--only`.

## B. The ChatGPT website (a custom GPT with Actions)
A custom GPT can only call a public HTTPS address, and JeeG's API listens on this computer only, so something has to
carry the request in. JeeG's own way is `connect ai ask`, which opens a protected link where you approve each change
(see `../../REMOTE_AI.md`). That is the safer choice. Using `../../integrations/openapi/jeeg-openapi.json` with your own
tunnel works too, but anything that can reach the tunnel address and has the token can run tasks on your computer.
If you do it: keep `--only` small, never use `--allow-confirm`, and shut the tunnel when you finish.
Paste `gpt-instructions.md` into the GPT's instructions.

## C. What this has not been tested with
The tool lists were checked for valid shape and against the local script. They were not tried against the live
OpenAI or Gemini services, and the ChatGPT website steps may change as that product changes.
