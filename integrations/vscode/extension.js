// JeeG for VS Code: a small box to type a task, using the local `jeeg` command. No network, no telemetry.
const vscode = require("vscode");
const { spawn } = require("child_process");

const out = vscode.window.createOutputChannel("JeeG");

function runJeeg(args, stdinText) {
  const cfg = vscode.workspace.getConfiguration("jeeg");
  const parts = String(cfg.get("command") || "jeeg").trim().split(/\s+/);
  const timeout = Math.max(1, Number(cfg.get("timeoutSeconds")) || 60) * 1000;
  return new Promise((resolve) => {
    // No shell: the phrase is passed as separate arguments, so it cannot be used to run other commands.
    const p = spawn(parts[0], [...parts.slice(1), "--json", ...args], { windowsHide: true });
    let so = "", se = "";
    const timer = setTimeout(() => p.kill(), timeout);
    p.stdout.on("data", (d) => { if (so.length < 1e6) so += d; });
    p.stderr.on("data", (d) => { if (se.length < 1e5) se += d; });
    p.on("error", (e) => { clearTimeout(timer); resolve({ ok: false, text: `Could not start JeeG (${e.message}). Install it with: pip install jeeg` }); });
    p.on("close", () => {
      clearTimeout(timer);
      try {
        const j = JSON.parse(so);
        resolve({ ok: j.exit === 0, text: (j.output || "").trim() || `(exit ${j.exit})`, json: j });
      } catch (_) {
        resolve({ ok: false, text: (so + se).trim() || "No answer from JeeG." });
      }
    });
    if (stdinText !== undefined) { p.stdin.write(stdinText); }
    p.stdin.end();
  });
}

async function show(phrase, stdinText) {
  const r = await runJeeg(phrase.split(/\s+/).filter(Boolean), stdinText);
  out.clear();
  out.appendLine(`> ${phrase}`);
  out.appendLine(r.text);
  out.show(true);
  if (!r.ok) vscode.window.showWarningMessage("JeeG: " + r.text.split("\n")[0].slice(0, 120));
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("jeeg.run", async () => {
      const phrase = await vscode.window.showInputBox({ prompt: "What do you want to do?", placeHolder: "gst 2500 18   |   convert 5 km to miles   |   weather" });
      if (phrase) await show(phrase.slice(0, 500));
    }),
    vscode.commands.registerCommand("jeeg.runSelection", async () => {
      const ed = vscode.window.activeTextEditor;
      const t = ed && ed.document.getText(ed.selection).trim();
      if (!t) return vscode.window.showInformationMessage("Select some text first, like: gst 2500 18");
      await show(t.split("\n")[0].slice(0, 500));
    }),
    vscode.commands.registerCommand("jeeg.pipeSelection", async () => {
      const ed = vscode.window.activeTextEditor;
      const t = ed && ed.document.getText(ed.selection);
      if (!t) return vscode.window.showInformationMessage("Select some text first.");
      const phrase = await vscode.window.showInputBox({ prompt: "Which text task? (the selection is piped in)", value: "word count" });
      if (phrase) await show(phrase.slice(0, 200), t.slice(0, 1000000));
    })
  );
}
function deactivate() {}
module.exports = { activate, deactivate };
