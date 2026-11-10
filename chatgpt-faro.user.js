// ==UserScript==
// @name         Faro · ChatGPT
// @namespace    faro
// @version      1.0
// @description  Avisa a Faro (en tu PC) de cuándo ChatGPT está trabajando y en qué conversación.
// @match        https://chatgpt.com/*
// @grant        GM_xmlhttpRequest
// @connect      192.168.18.108
// @connect      *
// ==/UserScript==
(function () {
  const FARO = "http://192.168.18.108:8787";
  let last = "", beat = 0;
  const busy = () => !!document.querySelector('[data-testid="stop-button"], button[aria-label*="Stop"], button[aria-label*="Detener"], button[aria-label*="detener"]');
  const searching = () => /buscando|searching the web|search/i.test((document.querySelector('[data-testid*="search"], .result-thinking') || {}).textContent || "");
  function send(r) {
    GM_xmlhttpRequest({ method: "POST", url: FARO + "/api/report", headers: { "Content-Type": "application/json" }, data: JSON.stringify(r) });
  }
  setInterval(() => {
    const b = busy(), title = document.title.replace(/\s*[-|·]\s*ChatGPT\s*$/i, "").trim() || "ChatGPT";
    const r = { id: "chatgpt-web", kind: "agent", name: "ChatGPT", brand: "gpt", cloud: true, ttl: 600,
      state: b ? "run" : "ok", action: b ? (searching() ? "web" : "think") : null,
      task: (b ? "responde · " : "") + title.slice(0, 60) };
    const k = JSON.stringify([r.state, r.task]);
    if (k !== last || Date.now() - beat > 60000) { send(r); last = k; beat = Date.now(); }
  }, 3000);
})();
