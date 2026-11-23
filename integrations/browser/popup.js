// JeeG browser extension popup: sends "<task> <text>" to the local JeeG API and shows the answer.
const api = typeof browser !== "undefined" ? browser : chrome;
const $ = (id) => document.getElementById(id);
const DEFAULT_CHIPS = ["word count", "readability", "uppercase", "lowercase", "sort lines", "remove duplicate lines"];
const BLOCKED = /^(chrome|edge|about|moz-extension|chrome-extension|view-source):/;

async function activeTab() {
  const [tab] = await api.tabs.query({ active: true, currentWindow: true });
  return tab || null;
}

async function selectedText() {
  try {
    const tab = await activeTab();
    if (!tab || !tab.id || BLOCKED.test(tab.url || "")) return "";
    const r = await api.scripting.executeScript({ target: { tabId: tab.id }, func: () => String(getSelection() || "").slice(0, 5000) });
    return (r && r[0] && r[0].result) || "";
  } catch (e) {
    return "";
  }
}

async function run(task, text) {
  const out = $("out");
  const { port, token } = await api.storage.local.get(["port", "token"]);
  out.hidden = false;
  $("copy").hidden = true;
  if (!token) { out.textContent = "Open Settings and paste the token from:  jeeg --api-token"; return; }
  if (!task) { out.textContent = "Type a task first."; return; }
  out.textContent = "...";
  api.storage.local.set({ last: task });
  try {
    const base = "http://127.0.0.1:" + (port || 8766);
    const headers = { "Content-Type": "application/json", Authorization: "Bearer " + token };
    let path = "/v1/run", body = { query: (task + " " + text).trim().slice(0, 2000) };
    if (text) {
      // Pass the text as one exact argument, so words in it can never be mistaken for part of the task name.
      const f = await (await fetch(base + "/v1/find?q=" + encodeURIComponent(task) + "&limit=1", { headers })).json();
      const m = f.ok && f.result && f.result[0];
      if (m && (!m.args || m.args.length === 0)) { path = "/v1/task"; body = { name: m.name, args: [text.slice(0, 2000)] }; }
    }
    const r = await fetch(base + path, { method: "POST", headers, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.ok) {
      const res = j.result || {};
      out.textContent = res.needs_confirmation ? "This task asks first, so it is not available from the browser." : (res.output || "(no output)");
      $("copy").hidden = !res.output;
    } else {
      out.textContent = j.error || "Failed";
    }
    if (r.status === 403) out.textContent += "\n\nStart JeeG with:  jeeg --serve-api --allow-origin " + location.origin;
  } catch (e) {
    out.textContent = "Could not reach JeeG. Start it with:\n  jeeg --serve-api --allow-origin " + location.origin;
  }
}

async function main() {
  const v = await api.storage.local.get(["last", "pending", "chips"]);
  const chips = Array.isArray(v.chips) && v.chips.length ? v.chips : DEFAULT_CHIPS;
  for (const c of chips.slice(0, 12)) {
    const b = document.createElement("button");
    b.className = "alt"; b.textContent = c;
    b.addEventListener("click", () => { $("task").value = c; run(c, $("text").value.trim()); });
    $("chips").appendChild(b);
  }
  if (v.last) $("task").value = v.last;
  if (v.pending) {                                   // text sent from the right-click menu
    $("text").value = v.pending;
    await api.storage.local.remove("pending");
    try { await api.action.setBadgeText({ text: "" }); } catch (_) {}
  } else {
    $("text").value = await selectedText();
  }
  $("run").addEventListener("click", () => run($("task").value.trim(), $("text").value.trim()));
  $("task").addEventListener("keydown", (e) => { if (e.key === "Enter") $("run").click(); });
  $("page").addEventListener("click", async () => {
    const tab = await activeTab();
    $("text").value = tab ? ((tab.title || "") + "\n" + (tab.url || "")).slice(0, 5000) : "";
  });
  $("copy").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText($("out").textContent); $("copy").textContent = "Copied"; } catch (_) {}
  });
}
main();
