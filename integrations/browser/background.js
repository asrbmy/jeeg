// JeeG browser extension, background part: right-click menu entries.
// They only hand the selected text or link to the popup; nothing is sent to JeeG until you press Run.
const api = typeof browser !== "undefined" ? browser : chrome;

api.runtime.onInstalled.addListener(() => {
  api.contextMenus.create({ id: "jeeg-selection", title: "Send selection to JeeG", contexts: ["selection"] });
  api.contextMenus.create({ id: "jeeg-link", title: "Send link to JeeG", contexts: ["link"] });
  api.contextMenus.create({ id: "jeeg-page", title: "Send page title and address to JeeG", contexts: ["page"] });
});

api.contextMenus.onClicked.addListener(async (info, tab) => {
  let text = "";
  if (info.menuItemId === "jeeg-selection") text = info.selectionText || "";
  else if (info.menuItemId === "jeeg-link") text = info.linkUrl || "";
  else if (info.menuItemId === "jeeg-page") text = ((tab && tab.title) || "") + "\n" + (info.pageUrl || (tab && tab.url) || "");
  text = String(text).slice(0, 5000);
  if (!text) return;
  await api.storage.local.set({ pending: text });
  try { await api.action.setBadgeText({ text: "1" }); } catch (_) {}
});
