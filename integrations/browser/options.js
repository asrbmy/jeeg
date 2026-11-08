const api = typeof browser !== "undefined" ? browser : chrome;
document.getElementById("cmd").textContent = "jeeg --serve-api --allow-origin " + location.origin + " --only text,money,utility,time";
api.storage.local.get(["port", "token"], (v) => {
  if (v && v.port) document.getElementById("port").value = v.port;
  if (v && v.token) document.getElementById("token").value = v.token;
});
document.getElementById("save").addEventListener("click", () => {
  const port = parseInt(document.getElementById("port").value, 10);
  const token = document.getElementById("token").value.trim();
  if (!(port >= 1024 && port <= 65535)) { document.getElementById("msg").textContent = "Port must be 1024-65535."; return; }
  api.storage.local.set({ port, token }, () => { document.getElementById("msg").textContent = "Saved."; });
});
