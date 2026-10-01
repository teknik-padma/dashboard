/* Service worker pembungkus Padma Group. Cache sendiri untuk berkas pembungkus;
   dashboard /exec (script.google.com) TIDAK pernah disentuh. Naikkan VERSI tiap isi
   BERKAS atau penangan di bawah berubah. */
/* v6 (2026-09-27, modifikasi bangun-cepat.py dipindah ke sini):
   - NAVIGASI (index, app) = JARINGAN DULU, batas 3 dtk, lalu cache: versi baru terpakai
     di pembukaan yang sama (dulu cache dulu = baru terpakai satu buka kemudian). Rilis
     PERALIHAN pertama tetap butuh buka 2x: navigasinya masih ditangani SW lama.
   - Berkas lain tetap cache dulu, disegarkan di latar (v5, 2026-09-25).
   - cdnjs + Google Fonts di cache sendiri padma-cdn-v1 (luring: d3 dan Inter; v776/v786);
     tidak ikut dibersihkan saat VERSI naik -- URL-nya berversi, isinya tidak berubah.
   - Respons TERALIHKAN tidak pernah disimpan/disajikan (Pages 308 /app.html -> /app).
   - ./app ikut pra-simpan HANYA di *.padmagroup.pages.dev: di github.io tidak ada,
     addAll akan gagal dan SW tidak terpasang sama sekali. */
/* v7 (2026-09-28, notifikasi fase 2): PUSH dari pengirim Cloudflare (repo Dashboard:
   cepat/functions/api/kirim-push.js). Isi { judul, isi, url, tag }; ketukan memfokuskan
   jendela aplikasi yang terbuka, atau membukanya. Tanpa `badge`: ikon berwarna jadi kotak
   putih di bilah status Android -- lonceng bawaan Chrome lebih terbaca. */
/* v9 (2026-09-29, Dashboard v858): index.html layar terbagi (dua iframe dashboard). */
/* v10 (2026-09-30, notifikasi unduh): ./unduhan/<nama> disajikan HANYA dari cache padma-unduhan
   (diisi index.html sesudah relai unduh; Pages tidak punya berkasnya), dan notifikasi `buka:true`
   selalu membuka URL-nya, bukan sekadar memfokuskan jendela yang sudah terbuka. */
/* v11 (2026-10-01): layar muat laser pendek tiap buka, penuh sekali sehari (index.html). */
/* v12 (2026-10-01): logo Padma + FirstJet diam, tanpa ukiran laser (index.html). */
/* v13 (2026-10-01 sore): laser kembali, selaras satu lintasan kilau latar (index.html). */
/* v14 (2026-10-01 sore): jam laser tanpa lompat di awal (index.html). */
const VERSI = 'padma-pembungkus-v14';
const UNDUHAN = 'padma-unduhan';
const CDN = 'padma-cdn-v1';
const DI_PAGES = ('.' + self.location.hostname).endsWith('.padmagroup.pages.dev');
const BERKAS = ['./', './index.html', './manifest.json', './favicon.svg', './icon-192.png', './icon-512.png', './icon-maskable-192.png', './icon-maskable-512.png']
  .concat(DI_PAGES ? ['./app'] : []);
const NAVIGASI_MAKS_MS = 3000;

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSI).then((c) => c.addAll(BERKAS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== VERSI && k !== CDN && k !== UNDUHAN).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function simpan(req, r) {
  if (r && r.ok && !r.redirected) {
    const salin = r.clone();
    caches.open(VERSI).then((c) => c.put(req, salin));
  }
  return r;
}
function dariCache(req) {
  return caches.match(req, { ignoreSearch: true }).then((lama) => (lama && !lama.redirected) ? lama : null);
}

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  if (url.origin === 'https://cdnjs.cloudflare.com' || url.origin === 'https://fonts.googleapis.com' ||
      url.origin === 'https://fonts.gstatic.com') {
    e.respondWith(caches.open(CDN).then((c) => c.match(e.request).then((ada) => ada ||
      fetch(e.request).then((r) => { if (r && (r.ok || r.type === 'opaque')) c.put(e.request, r.clone()); return r; }))));
    return;
  }
  if (url.origin !== self.location.origin) return;
  if (url.pathname.indexOf('/unduhan/') !== -1) {
    e.respondWith(caches.open(UNDUHAN).then((c) => c.match(e.request, { ignoreSearch: true })).then((r) => r ||
      new Response('Berkas ini sudah tidak tersimpan di perangkat. Unduh ulang dari aplikasi.',
        { status: 404, headers: { 'Content-Type': 'text/plain; charset=utf-8' } })));
    return;
  }
  const segar = fetch(e.request).then((r) => simpan(e.request, r));
  if (e.request.mode === 'navigate') {
    /* Jaringan menjawab dalam 3 dtk -> itu yang dipakai; lewat 3 dtk -> cache (kalau
       ada) sementara jaringan tetap mengisi cache; jaringan gagal -> cache -> './'. */
    e.respondWith(new Promise((jawab) => {
      let sudah = false;
      const pakai = (r) => { if (!sudah && r) { sudah = true; jawab(r); } };
      const cadangan = () => dariCache(e.request).then((lama) => { if (lama) pakai(lama); return lama; });
      const jam = setTimeout(cadangan, NAVIGASI_MAKS_MS);
      segar.then((r) => { clearTimeout(jam); pakai(r); }).catch(() => {
        clearTimeout(jam);
        cadangan().then((lama) => { if (!lama) caches.match('./').then((x) => pakai(x || Response.error())); });
      });
    }));
    e.waitUntil(segar.catch(() => {}));
    return;
  }
  e.respondWith(
    dariCache(e.request).then((lama) => {
      if (lama) { e.waitUntil(segar.catch(() => {})); return lama; }
      return segar.catch(() => caches.match('./'));
    })
  );
});

self.addEventListener('push', (e) => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (er) { d = { judul: 'Padma Group', isi: e.data ? e.data.text() : '' }; }
  const opsi = { body: String(d.isi || ''), icon: 'icon-192.png',
                 data: { url: new URL(d.url || './', self.registration.scope).href } };
  if (d.tag) { opsi.tag = String(d.tag); opsi.renotify = true; }
  /* v8 (Dashboard v831): halaman yang sedang terbuka ikut dikabari -> dashboard menyegarkan
     datanya sendiri (lembur disetujui). Hanya tag, isi notifikasi tidak diteruskan. */
  const kabari = self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((daftar) => {
    daftar.forEach((c) => { try { c.postMessage({ padma: 1, jenis: 'push', tag: String(d.tag || '') }); } catch (er) {} });
  });
  e.waitUntil(Promise.all([self.registration.showNotification(String(d.judul || 'Padma Group'), opsi), kabari]));
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  const tujuan = (e.notification.data && e.notification.data.url) || self.registration.scope;
  if (e.notification.data && e.notification.data.buka) { e.waitUntil(self.clients.openWindow(tujuan)); return; }
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((daftar) => {
    for (const c of daftar) {
      if (c.url.indexOf(self.registration.scope) === 0 && 'focus' in c) return c.focus();
    }
    return self.clients.openWindow(tujuan);
  }));
});
