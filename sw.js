/* Service worker pembungkus Padma Group. Hanya berkas pembungkus (situs ini
   sendiri) yang di-cache; dashboard di script.google.com TIDAK pernah disentuh.
   Cache dulu, disegarkan di latar (v5, 2026-09-25); lihat penangan fetch.
   Naikkan VERSI tiap berkas di BERKAS berubah nama. */
const VERSI = 'padma-pembungkus-v5';
const BERKAS = ['./', './index.html', './manifest.json', './favicon.svg', './icon-192.png', './icon-512.png', './icon-maskable-192.png', './icon-maskable-512.png'];

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
  /* CACHE DULU, SEGARKAN DI LATAR (2026-09-25, "booting pembungkus bisa
     dipercepat?"). Dulu jaringan dulu: tiap buka menunggu satu perjalanan
     ke GitHub/Cloudflare SEBELUM iframe dashboard boleh mulai dimuat. Sekarang
     cangkang langsung dari cache; versi baru dari jaringan disimpan untuk
     pembukaan BERIKUTNYA (harga: pembaruan pembungkus terpakai satu buka kemudian). */
  const segar = fetch(e.request).then((r) => {
    if (r && r.ok) {
      const salin = r.clone();
      caches.open(VERSI).then((c) => c.put(e.request, salin));
    }
    return r;
  });
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((lama) => {
      if (lama) { e.waitUntil(segar.catch(() => {})); return lama; }
      return segar.catch(() => caches.match('./'));
    })
  );
});
