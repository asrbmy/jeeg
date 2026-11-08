// JeeG browser extension: sends "<task> <text>" to the local JeeG API and shows the answer.
const api = typeof browser !== "undefined" ? browser : chrome;
const $ = (id) => document.getElementById(id);

function get(keys) {
  return new Promise((res) => api.storage.local.get(keys, (v) => res(v || {})));
}

async function selectedText() {
  try {
    const [tab] = await api.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.id || /^(chrome|edge|about|moz-extension|chrome-extension):/.test(tab.url || "")) return "";
    const r = await api.scripting.executeScript({ target: { tabId: tab.id }, func: () => String(getSelection() || "").slice(0, 5000) });
    return (r && r[0] && r[0].result) || "";
  } catch (e) {
    return "";
  }
}

async function run() {
  const out = $("out");
  const { port, token, last } = await get(["port", "token", "last"]);
  const task = $("task").value.trim();
  const text = $("text").value.trim();
  out.hidden = false;
  if (!token) { out.textContent = "Open Settings and paste the token from:  jeeg --api-token"; return; }
  if (!task) { out.textContent = "Type a task first."; return; }
  out.textContent = "...";
  api.storage.local.set({ last: task });
  try {
    const r = await fetch("http://127.0.0.1:" + (port || 8766) + "/v1/run", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
      body: JSON.stringify({ query: (task + " " + text).trim() }),
    });
    const j = await r.json();
    out.textContent = j.ok ? (j.result.output || "(no output)") : (j.error || "Failed");
    if (r.status === 403) out.textContent += "\n\nStart JeeG with:  jeeg --serve-api --allow-origin " + location.origin;
  } catch (e) {
    out.textContent = "Could not reach JeeG. Start it with:\n  jeeg --serve-api --allow-origin " + location.origin;
  }
}

(async () => {
  const { last } = await get(["last"]);
  if (last) $("task").value = last;
  $("text").value = await selectedText();
  $("run").addEventListener("click", run);
  $("task").addEventListener("keydown", (e) => { if (e.key === "Enter") run(); });
})();
