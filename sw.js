/* Service worker pembungkus Padma Group. Hanya berkas pembungkus (situs ini
   sendiri) yang di-cache; dashboard di script.google.com TIDAK pernah disentuh.
   Jaringan dulu supaya pembaruan langsung terpakai; cache kalau offline.
   Naikkan VERSI tiap berkas di BERKAS berubah nama. */
const VERSI = 'padma-pembungkus-v3';
const BERKAS = ['./', './index.html', './manifest.json', './favicon.svg', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSI).then((c) => c.addAll(BERKAS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== VERSI).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  e.respondWith(
    fetch(e.request)
      .then((r) => {
        if (r && r.ok) {
          const salin = r.clone();
          caches.open(VERSI).then((c) => c.put(e.request, salin));
        }
        return r;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true })
        .then((r) => r || caches.match('./')))
  );
});
