"""Membangun halaman pembungkus Padma Group (GitHub Pages teknik-padma/dashboard).
Pakai: python bangun-pembungkus.py <folder repo pembungkus>
Menulis index.html, manifest.json, sw.js (ikon dibuat terpisah)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from huruf_laser import tulisan

OUT = sys.argv[1]
IDX = open(r'C:/RAYHANKHALID/WORK/DASHBOARD PADMA/Index.html', 'rb').read().decode('utf-8')
a = IDX.index('<svg class="ag-laser"')
b = IDX.index('</svg>', a) + len('</svg>')
svg = IDX[a:b]
assert svg.count('agl-gores') >= 8, svg.count('agl-gores')

# Tulisan PADMA GROUP garis tunggal di bawah logo, satu SVG dengan logonya
# (satu titik laser berpindah dari logo ke huruf).
paths, lebar = tulisan('PADMA GROUP', 1.6, 0, 78)
VB_X, VB_W = -82, 164
VB_Y, VB_H = -60, 158
assert lebar < VB_W - 4, lebar
huruf = ''.join('<path class="agl-teks" d="%s"/>' % d for d in paths)
svg = svg.replace('class="ag-laser"', 'id="laser"')
svg = svg.replace('viewBox="-60 -60 120 120"', 'viewBox="%d %d %d %d"' % (VB_X, VB_Y, VB_W, VB_H))
svg = svg.replace('stroke="#fff"', 'stroke="currentColor"')
svg = svg.replace('<rect class="agl-titik"',
                  '<g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
                  'stroke-linejoin="round">' + huruf + '</g><rect class="agl-titik" fill="currentColor"')
assert 'viewBox="%d %d' % (VB_X, VB_Y) in svg
LEBAR_PX = round(104 * VB_W / 120)
TINGGI_PX = round(104 * VB_H / 120)

EXEC = 'https://script.google.com/macros/s/AKfycbzBRPeuPWoL3UdErFpn9WngpqQNiqvf9zH0dOhAsNEGlI1s9Uhm0XIGkWwalLctpwwR/exec'
TERANG_LATAR, TERANG_BILAH = '#F5F7FB', '#FFFFFF'
GELAP_LATAR, GELAP_BILAH = '#000000', '#16181C'

html = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="''' + TERANG_BILAH + '''" id="warnaBilah">
<title>Padma Group</title>
<meta name="description" content="Dashboard karyawan PT Padmacahaya Mitra Teknologi dan PT Padmacahaya Mitra Pratama.">
<!-- PWA: bisa diinstal di Chrome HP (manifest + service worker), dan di iPhone
     lewat Bagikan > Tambah ke Layar Utama (tag apple-*). -->
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="icon-192.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Padma Group">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>
/* Tema diputuskan SEBELUM cat pertama: yang terakhir dikirim dashboard
   (localStorage halaman ini), kalau belum pernah -> tema perangkat. Warna bilah
   status (theme-color) ikut diputuskan di sini juga. */
(function () {
  var h = document.documentElement, t = null, b = null;
  try { t = localStorage.getItem('padmaTema'); b = localStorage.getItem('padmaBawah'); } catch (e) {}
  if (t !== 'dark' && t !== 'light') t = (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  h.setAttribute('data-tema', t);
  if (b) h.style.setProperty('--bawah', b);
  var m = document.getElementById('warnaBilah');
  if (m) m.setAttribute('content', b || (t === 'dark' ? \'''' + GELAP_BILAH + '''\' : \'''' + TERANG_BILAH + '''\'));
})();
</script>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@600&display=swap">
<style>
  :root { --latar: ''' + TERANG_LATAR + '''; --garis: #111827; --bawah: ''' + TERANG_BILAH + '''; }
  html[data-tema="dark"] { --latar: ''' + GELAP_LATAR + '''; --garis: #FFFFFF; --bawah: ''' + GELAP_BILAH + '''; }
  html, body { margin: 0; height: 100%; overflow: hidden; background: var(--bawah); }
  /* Ruang atas/bawah seperti aplikasi: area poni/status dan garis navigasi HP
     (safe-area) TIDAK ditimpa iframe -- iframe tidak mengenal inset itu -- tapi
     diisi warna bilah dashboard. Di peramban biasa inset atas = 0. */
  iframe {
    position: fixed; left: 0; width: 100%;
    top: env(safe-area-inset-top, 0px);
    height: calc(100% - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px));
    border: 0; display: block;
  }
  #muat {
    position: fixed; inset: 0; z-index: 2; background: var(--latar); color: var(--garis);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    transition: opacity .26s ease;
  }
  #muat.lepas { opacity: 0; pointer-events: none; }
  #laser { width: ''' + str(LEBAR_PX) + '''px; height: ''' + str(TINGGI_PX) + '''px; overflow: visible; }
  .putus {
    margin-top: 18px; font: 600 13px/1.4 Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    opacity: .7; display: none;
  }
  #muat.offline .putus { display: block; }
  @media (prefers-reduced-motion: reduce) { #muat { transition: none; } }
</style>
</head>
<body>
<div id="muat" role="status" aria-label="Memuat Padma Group">
''' + svg + '''
<div class="putus">Tidak ada koneksi internet. Dashboard terbuka otomatis begitu tersambung.</div>
</div>
<iframe id="dasbor" src="''' + EXEC + '''"
        title="Padma Group"
        allow="camera; clipboard-read; clipboard-write; fullscreen; geolocation"></iframe>
<script>
/* Pembungkus Padma Group (2026-09-24). Layar muat = laser mengukir logo lalu
   tulisan PADMA GROUP, SEKALI (logo 4500 ms, tulisan 2500 ms), dilepas waktu
   dashboard mengirim "siap" (postMessage). Pesan hanya diterima dari domain
   Google. Jaring pengaman 25 dtk; ?tahan=1 menahan layar ini (uji). */
(function () {
  var muat = document.getElementById('muat');
  var dasbor = document.getElementById('dasbor');
  var h = document.documentElement;
  var bilah = document.getElementById('warnaBilah');
  var jalan = true, siap = false, mulai = Date.now();
  var TAHAN = /[?&]tahan=1/.test(location.search);

  function simpan(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function lepas() {
    if (!jalan || TAHAN) return;
    jalan = false;
    muat.classList.add('lepas');
    setTimeout(function () { muat.style.display = 'none'; }, 300);
  }
  function warnaBilah() {
    var c = getComputedStyle(h).getPropertyValue('--bawah').trim();
    if (c) bilah.setAttribute('content', c);
  }

  window.addEventListener('message', function (e) {
    var asal = String(e.origin || '');
    if (!/^https:\\/\\/([a-z0-9-]+\\.)*(googleusercontent\\.com|google\\.com)$/.test(asal)) return;
    var d = e.data;
    if (!d || d.padma !== 1) return;
    if ((d.jenis === 'tema' || d.jenis === 'warna') && (d.tema === 'dark' || d.tema === 'light')) {
      h.setAttribute('data-tema', d.tema);
      simpan('padmaTema', d.tema);
      warnaBilah();
    }
    if (d.jenis === 'warna' && typeof d.bawah === 'string' && /^rgba?\\([\\d.,\\s]+\\)$|^#[0-9a-f]{3,8}$/i.test(d.bawah)) {
      h.style.setProperty('--bawah', d.bawah);
      simpan('padmaBawah', d.bawah);
      warnaBilah();
    }
    if (d.jenis === 'siap') { siap = true; lepas(); }
  });
  setTimeout(lepas, 25000);

  /* Tanpa internet: layar muat berkata begitu; tersambung lagi sebelum dashboard
     sempat siap -> iframe dimuat ulang (yang sudah siap tidak disentuh). */
  function cekOnline() { muat.classList.toggle('offline', navigator.onLine === false); }
  cekOnline();
  window.addEventListener('offline', cekOnline);
  window.addEventListener('online', function () {
    cekOnline();
    if (!siap) dasbor.src = dasbor.src;
  });

  /* Service worker: syarat instal Chrome + cangkang pembungkus tetap terbuka
     tanpa jaringan. Dashboard (script.google.com) tidak pernah di-cache. */
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function (err) { console.warn('service worker gagal', err); });
    });
  }

  /* Laser: gerak yang sama dengan agLaserMulai_ di Index.html (luncur 0,35 x
     jarak dengan titik mati), dua fase: logo lalu huruf. */
  var svg = document.getElementById('laser');
  var semua = Array.prototype.slice.call(svg.querySelectorAll('.agl-gores, .agl-teks'));
  var nLogo = svg.querySelectorAll('.agl-gores').length;
  var titik = svg.querySelector('.agl-titik');
  var pj = semua.map(function (g) { var l = g.getTotalLength(); g.style.strokeDasharray = l; g.style.strokeDashoffset = l; return l; });
  var fase = [{ mulai: 0, ms: 4500, ruas: [], total: 0 }, { mulai: 4500, ms: 2500, ruas: [], total: 0 }];
  semua.forEach(function (g, i) {
    var f = fase[i < nLogo ? 0 : 1];
    if (i > 0) {
      var a = semua[i - 1].getPointAtLength(pj[i - 1]), b = g.getPointAtLength(0);
      var d = Math.hypot(b.x - a.x, b.y - a.y);
      if (d > 0.5) { f.ruas.push({ luncur: true, L: d * 0.35 }); f.total += d * 0.35; }
    }
    f.ruas.push({ luncur: false, i: i, L: pj[i] }); f.total += pj[i];
  });
  var AKHIR = fase[1].mulai + fase[1].ms;
  function mulus(x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; }
  /* Diputar rAF (selaras layar; setTimeout 30 ms dulu patah-patah), setTimeout
     100 ms cadangan kalau rAF tidak datang (tab di latar). */
  function berikut(fn) {
    var sudah = false;
    var jalankan = function () { if (!sudah) { sudah = true; fn(); } };
    if (window.requestAnimationFrame) requestAnimationFrame(jalankan);
    setTimeout(jalankan, 100);
  }
  (function langkah() {
    if (!jalan) return;
    var dt = Date.now() - mulai, pos = null;
    fase.forEach(function (f) {
      var p = Math.max(0, Math.min(1, (dt - f.mulai) / f.ms));
      var aktif = p > 0 && p < 1;
      var sisa = f.total * mulus(p);
      f.ruas.forEach(function (s) {
        var ambil = Math.max(0, Math.min(s.L, sisa));
        if (!s.luncur) {
          semua[s.i].style.strokeDashoffset = pj[s.i] - ambil;
          if (aktif) pos = (ambil > 0 && ambil < s.L) ? semua[s.i].getPointAtLength(ambil) : (ambil > 0 ? null : pos);
        } else if (aktif && ambil > 0) pos = null;
        sisa -= ambil;
      });
    });
    if (pos) { titik.setAttribute('x', pos.x - 2.5); titik.setAttribute('y', pos.y - 2.5); titik.style.opacity = 1; }
    else titik.style.opacity = 0;
    if (dt >= AKHIR) { titik.style.opacity = 0; return; }
    berikut(langkah);
  })();
})();
</script>
</body>
</html>
'''

manifest = {
    "name": "Padma Group",
    "short_name": "Padma Group",
    "description": "Dashboard karyawan PT Padmacahaya Mitra Teknologi dan PT Padmacahaya Mitra Pratama.",
    "id": "./",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "background_color": TERANG_LATAR,
    "theme_color": TERANG_BILAH,
    "lang": "id",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}

sw = '''/* Service worker pembungkus Padma Group. Hanya berkas pembungkus (situs ini
   sendiri) yang di-cache; dashboard di script.google.com TIDAK pernah disentuh.
   Jaringan dulu supaya pembaruan langsung terpakai; cache kalau offline.
   Naikkan VERSI tiap berkas di BERKAS berubah nama. */
const VERSI = 'padma-pembungkus-v1';
const BERKAS = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

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
'''

open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8', newline='\n').write(html)
open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8', newline='\n').write(sw)
print('ok', len(html), 'px', LEBAR_PX, TINGGI_PX, 'huruf', len(paths))
