const api = typeof browser !== "undefined" ? browser : chrome;
const $ = (id) => document.getElementById(id);
$("cmd").textContent = "jeeg --serve-api --allow-origin " + location.origin + " --only text,money,utility,time";
api.storage.local.get(["port", "token", "chips"]).then((v) => {
  if (v.port) $("port").value = v.port;
  if (v.token) $("token").value = v.token;
  if (Array.isArray(v.chips)) $("chips").value = v.chips.join("\n");
});
$("save").addEventListener("click", async () => {
  const port = parseInt($("port").value, 10);
  const token = $("token").value.trim();
  if (!(port >= 1024 && port <= 65535)) { $("msg").textContent = "Port must be 1024-65535."; return; }
  const chips = $("chips") ? $("chips").value.split("\n").map((s) => s.trim()).filter(Boolean).slice(0, 12) : [];
  await api.storage.local.set({ port, token, chips });
  $("msg").textContent = "Saved.";
});
