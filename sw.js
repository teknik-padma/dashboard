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
/* v15 (2026-10-01 sore): iframe dashboard dipasang sesudah ukiran selesai (index.html). */
/* v16 (2026-10-01 malam): unduhan selalu disalin ke cache + pesan bukaUnduhan (banner dashboard membuka PDF). */
/* v17 (2026-10-02): ikon aplikasi digambar ulang -- cincin lingkaran sempurna (pemilik: "kanan kirinya tidak lingkaran
   sempurna"); manifest memakai ?v=2 supaya Chrome mengambil ikon baru. */
/* v18 (2026-10-02): padma-demo.pages.dev memuat ./app seperti padmagroup (index.html + DI_PAGES). */
/* v19 (2026-10-15, dashboard v1179, pemilik: "optimization for low internet speed"): NAVIGASI index + app di pages.dev
   bertanya ./versi.json dulu (sidik SHA-256 isi berkas, ditulis bangun-cepat.py, ~150 byte). Sidik sama dengan salinan
   cache -> salinan langsung dipakai, TANPA unduh. Dulu tiap buka mengunduh ulang /app 1,07 MB (Pages tidak memberi
   ETag, jadi tidak pernah 304) dan menunggu 3 dtk dua kali di sinyal jelek; terukur 400 kbps: siap 8,8 dtk, 1,2-1,7 MB
   per buka. versi.json lambat (> VERSI_MAKS_MS) -> salinan dipakai, pembaruan diunduh di latar = terpakai buka
   berikutnya. versi.json tidak ada/gagal (situs demo, rilis lama) -> jalur v6 seperti dulu. lihat dashboard
   docs/ui/boot-dan-runtime.md § Buka ulang tanpa unduh ulang (v1179) */
/* v20 (2026-10-15, dashboard v1181): berkas BERSIDIK di nama (`kamus-<12 hex>.js`, dari bangun-cepat.py) = isinya tidak
   pernah berubah -> cache dulu TANPA unduh ulang di latar (jalur umum mengunduh ulang 266 KB tiap buka). Menyimpan satu
   menghapus saudara lama berawalan sama, jadi cache tidak menumpuk satu kamus per rilis. */
const VERSI = 'padma-pembungkus-v20';
const ABADI = /\/([a-z]+)-[0-9a-f]{12}\.js$/;
const UNDUHAN = 'padma-unduhan';
const CDN = 'padma-cdn-v1';
const DI_PAGES = /(^|\.)(padmagroup|padma-demo)\.pages\.dev$/.test(self.location.hostname);   /* v18: + situs demo */
const BERKAS = ['./', './index.html', './manifest.json', './favicon.svg', './icon-192.png', './icon-512.png', './icon-maskable-192.png', './icon-maskable-512.png']
  .concat(DI_PAGES ? ['./app'] : []);
const NAVIGASI_MAKS_MS = 3000;
const VERSI_MAKS_MS = 1500;
const LINGKUP = new URL(self.registration.scope).pathname;

self.addEventListener('install', (e) => {
  /* v19: ./app disimpan BERSIDIK (bukan addAll), supaya buka pertama sesudah pasang tidak mengunduhnya lagi. */
  e.waitUntil(caches.open(VERSI).then((c) => c.addAll(BERKAS.filter((b) => b !== './app')))
    .then(() => DI_PAGES ? fetch('./app').then((r) => { if (!r.ok) throw new Error('app ' + r.status); return simpanBersidik('./app', r); }) : null)
    .then(() => self.skipWaiting()));
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
/* v19: sidik SHA-256 (hex) isi respons disimpan sebagai header X-Padma-Sidik di salinan cache -- dibandingkan dengan
   versi.json tanpa menghitung ulang 4 MB tiap buka. Content-Encoding/Length dibuang: badan yang disimpan sudah terurai. */
function hex(buf) { return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, '0')).join(''); }
function simpanBersidik(req, r) {
  if (!r || !r.ok || r.redirected) return Promise.resolve();
  return r.clone().arrayBuffer().then((isi) => crypto.subtle.digest('SHA-256', isi).then((h) => {
    const hs = new Headers(r.headers);
    hs.delete('Content-Encoding'); hs.delete('Content-Length');
    hs.set('X-Padma-Sidik', hex(h));
    return caches.open(VERSI).then((c) => c.put(req, new Response(isi, { status: r.status, statusText: r.statusText, headers: hs })));
  }));
}
/* Satu pertanyaan versi.json dipakai bersama index + app (+ layar terbagi) selama 30 dtk. Jawaban: objek sidik,
   null = tidak ada/gagal, undefined = belum datang dalam maksMs (permintaannya tetap berjalan untuk penanya berikut). */
let versiJanji = null, versiSejak = 0;
function versiTerbaru(maksMs) {
  if (!versiJanji || Date.now() - versiSejak > 30000) {
    versiSejak = Date.now();
    versiJanji = fetch('./versi.json', { cache: 'no-store' })
      .then((r) => (r.ok && !r.redirected) ? r.json() : null).catch(() => null);
  }
  return Promise.race([versiJanji, new Promise((j) => setTimeout(() => j(undefined), maksMs))]);
}
function namaNavigasi(url) {
  if (!DI_PAGES) return null;
  if (url.pathname === LINGKUP + 'app') return 'app';
  if (url.pathname === LINGKUP || url.pathname === LINGKUP + 'index.html') return 'index';
  return null;
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
  /* v19: index/app lewat sidik, BUKAN hanya navigasi: index.html juga mengunduh `app` lebih dulu dengan fetch biasa
     (pasang ditunda sesudah ukiran) -- jalur "cache dulu, segarkan di latar" di bawah mengunduh ulang 1 MB tiap buka
     dan menimpa salinan bersidik dengan salinan tanpa sidik (terukur di uji-sw.padmagroup.pages.dev). */
  const nama = namaNavigasi(url);
  if (nama) { navigasiBersidik(e, nama); return; }
  const abadi = ABADI.exec(url.pathname);
  if (abadi) {
    e.respondWith(caches.match(e.request, { ignoreSearch: true }).then((ada) => ada || fetch(e.request).then((r) => {
      if (r && r.ok && !r.redirected) {
        const salin = r.clone();
        e.waitUntil(caches.open(VERSI).then((c) => c.keys().then((ks) => Promise.all(ks
          .filter((k) => { const m = ABADI.exec(new URL(k.url).pathname); return m && m[1] === abadi[1] && k.url !== e.request.url; })
          .map((k) => c.delete(k)))).then(() => c.put(e.request, salin))));
      }
      return r;
    })));
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

/* v19: index/app di pages.dev. Urutan: salinan bersidik + versi.json sama -> salinan (tanpa jaringan lagi);
   versi.json lambat -> salinan, lalu di latar unduh baru bila sidiknya beda; selain itu (beda, tanpa salinan,
   versi.json tidak ada) -> jalur v6 jaringan dulu 3 dtk, hasilnya disimpan bersidik. */
/* Satu unduhan per berkas, dibagi fetch awal index.html + navigasi iframe (+ layar terbagi): versi baru tidak
   pernah diunduh dua kali. Tiap peminta mendapat salinannya sendiri (clone). */
const unduhJalan = {};
function unduhBersama(e, nama, kunci, alamat) {
  if (!unduhJalan[nama]) {
    unduhJalan[nama] = fetch(alamat, { credentials: 'same-origin' }).then((r) => {
      const simpanan = (r && r.ok && !r.redirected) ? simpanBersidik(kunci, r.clone()).catch(() => {}) : Promise.resolve();
      simpanan.then(() => { delete unduhJalan[nama]; });
      return { r, simpanan };
    }, (err) => { delete unduhJalan[nama]; throw err; });
  }
  return unduhJalan[nama].then((h) => { e.waitUntil(h.simpanan); return h.r.clone(); });
}
function navigasiBersidik(e, nama) {
  const req = e.request;
  const kunci = nama === 'app' ? './app' : './';
  const unduh = () => unduhBersama(e, nama, kunci, req.url);
  e.respondWith(caches.match(kunci).then((lama) => {
    lama = (lama && !lama.redirected) ? lama : null;
    const sidikLama = lama && lama.headers.get('X-Padma-Sidik');
    return (lama ? versiTerbaru(VERSI_MAKS_MS) : Promise.resolve(null)).then((v) => {
      if (lama && sidikLama && v && v[nama] === sidikLama) return lama;
      if (lama && v === undefined) {
        e.waitUntil(versiJanji.then((v2) => {
          if (v2 && v2[nama] && v2[nama] !== sidikLama) return unduh().catch(() => {});
        }));
        return lama;
      }
      return new Promise((jawab) => {
        let sudah = false;
        const pakai = (r) => { if (!sudah && r) { sudah = true; jawab(r); } };
        const segar = unduh();
        e.waitUntil(segar.catch(() => {}));
        const jam = setTimeout(() => { if (lama) pakai(lama); }, NAVIGASI_MAKS_MS);
        segar.then((r) => { clearTimeout(jam); pakai(r); }).catch(() => {
          clearTimeout(jam);
          if (lama) { pakai(lama); return; }
          caches.match('./').then((x) => pakai(x || Response.error()));
        });
      });
    });
  }));
}

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
