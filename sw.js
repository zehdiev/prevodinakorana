// Offline support: everything the app needs is cached on first visit.
const VERSION = "quran-bg-c6fb9f4d4c";
const FILES = ["./", "index.html", "manifest.webmanifest", "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png", "data/ar.json", "data/bg-ahmadiyya-flags.json", "data/bg-ahmadiyya.json", "data/bg-dobrev-flags.json", "data/bg-dobrev.json", "data/bg-gendzhev-flags.json", "data/bg-gendzhev.json", "data/bg-hayraddin.json", "data/bg-hope-flags.json", "data/bg-hope.json", "data/bg-shemsuddin-flags.json", "data/bg-shemsuddin.json", "data/bg-tafsir-text.json", "data/bg-theophanov.json", "data/meta.json", "data/tafsir.json"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION && k !== "quran-bg-fonts").map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  if (u.hostname === "fonts.googleapis.com" || u.hostname === "fonts.gstatic.com") {
    e.respondWith(caches.open("quran-bg-fonts").then(c => c.match(e.request).then(hit => {
      const net = fetch(e.request).then(r => { c.put(e.request, r.clone()); return r }).catch(() => hit);
      return hit || net;
    })));
    return;
  }
  if (u.origin !== location.origin) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(r => {
    if (r.ok) { const copy = r.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)) }
    return r;
  }).catch(() => e.request.mode === "navigate" ? caches.match("index.html") : Response.error())));
});
