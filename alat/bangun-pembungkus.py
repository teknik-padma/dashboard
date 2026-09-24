"""Membangun halaman pembungkus Padma Group (GitHub Pages teknik-padma/dashboard).
Pakai: python bangun-pembungkus.py <folder repo pembungkus>
Menulis index.html, manifest.json, sw.js (ikon dibuat terpisah)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jiplak_logo import jiplak

OUT = sys.argv[1]
ALAT = os.path.dirname(os.path.abspath(__file__))

# Dua logo dijiplak dari gambar aslinya (alat/logo-*.{jpg,png}, dikirim pemilik
# 2026-09-24), tinggi sama 100 satuan, berdampingan (Padma digeser GESER ke
# kiri). Keduanya diukir BERSAMAAN sejak awal, dua titik laser -- dulu Padma
# dulu lalu geser, tapi boot cepat memotong FirstJet ("login ya login aja").
# Laser = garis tepi (kontur), lalu isi diarsir baris demi baris.
PADMA = jiplak(os.path.join(ALAT, 'logo-padma.jpg'), 'terang', 100, 0, 'luas')
FJ = jiplak(os.path.join(ALAT, 'logo-firstjet.png'), 'putih', 100, 65, 'dekat')
# IoU Padma ~0,92, bukan ~0,98: gambar aslinya memotong cincin ~2,7 px di
# keempat sisi, dan cincin di sini lingkaran sejati (tidak ikut terpotong).
for nama, L, batas in (('padma', PADMA, 0.9), ('firstjet', FJ, 0.97)):
    assert L['iou'] > batas, (nama, L['iou'])
GESER = -62.5
VB = (-118, -56, 236, 112)
assert PADMA['kotak'][0] + GESER > VB[0] and FJ['kotak'][2] < VB[0] + VB[2], (PADMA['kotak'], FJ['kotak'])


def logo_svg(kelas, L, isi):
    gores = ''.join('<path class="gores" d="%s"/>' % d for d in L['gores'])
    return ('<g class="%s">'
            '<clipPath id="arsir-%s"><rect class="tirai" x="-200" y="-60" width="400" height="0"/></clipPath>'
            '<path class="isi" fill="%s" fill-rule="evenodd" clip-path="url(#arsir-%s)" d="%s"/>'
            '<g class="tepi" fill="none" stroke="currentColor" stroke-width=".8" stroke-linejoin="round" opacity="0">%s</g>'
            '<circle class="halo" r="3.2" fill="#fff" opacity="0"/><circle class="titik" r="1.1" fill="#fff" opacity="0"/>'
            '</g>') % (kelas, kelas, isi, kelas, L['isi'], gores)


# Padma putih polos seperti FirstJet (pemilik: "putih aja, jangan abu"; warna
# perak gambar aslinya tidak dipakai).
svg = ('<svg id="laser" viewBox="%d %d %d %d" aria-hidden="true">' % VB
       + '<g transform="translate(%s 0)">' % GESER + logo_svg('padma', PADMA, '#FFFFFF') + '</g>'
       + logo_svg('firstjet', FJ, '#FFFFFF')
       + '</svg>')
LEBAR_PX = 320
DATA_LASER = json.dumps({
                         'baris': [PADMA['baris'], FJ['baris']]}, separators=(',', ':'))

EXEC = 'https://script.google.com/macros/s/AKfycbzBRPeuPWoL3UdErFpn9WngpqQNiqvf9zH0dOhAsNEGlI1s9Uhm0XIGkWwalLctpwwR/exec'
TERANG_BILAH, GELAP_BILAH = '#FFFFFF', '#16181C'

html = '''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#000000" id="warnaBilah">
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
   (localStorage halaman ini), kalau belum pernah -> tema perangkat. Layar muat
   selalu hitam (diminta pemilik), jadi bilah status (theme-color) hitam dulu;
   warna bilah dashboard baru dipasang sesudah layar muat dilepas. */
(function () {
  var h = document.documentElement, t = null, b = null;
  try { t = localStorage.getItem('padmaTema'); b = localStorage.getItem('padmaBawah'); } catch (e) {}
  if (t !== 'dark' && t !== 'light') t = (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
  h.setAttribute('data-tema', t);
  if (b) h.style.setProperty('--bawah', b);
})();
</script>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@600&display=swap">
<style>
  :root { --bawah: ''' + TERANG_BILAH + '''; }
  html[data-tema="dark"] { --bawah: ''' + GELAP_BILAH + '''; }
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
    position: fixed; inset: 0; z-index: 2; background: #000; color: #fff;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    transition: opacity .26s ease;
  }
  #muat.lepas { opacity: 0; pointer-events: none; }
  #laser { width: min(''' + str(LEBAR_PX) + '''px, 86vw); height: auto; aspect-ratio: ''' + '%d / %d' % (VB[2], VB[3]) + '''; overflow: visible; }
  #laser .halo { filter: blur(1.4px); }
  .putus {
    margin-top: 18px; font: 600 13px/1.4 Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    opacity: .7; display: none;
  }
  #muat.offline .putus { display: block; }
  /* Dashboard sudah siap sebelum laser selesai: tombol lanjut muncul di bawah
     logo (diminta: "ditunggu selesai baru masuk, tapi kalau sudah selesai
     loading ada opsi klik untuk melanjutkan"). Seluruh layar ikut bisa diketuk. */
  .lanjut {
    margin-top: 32px; min-height: 44px; padding: 10px 22px; border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, .38); background: transparent; color: #fff;
    font: 600 14px/1.2 Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    opacity: 0; visibility: hidden; transition: opacity .3s ease; cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }
  #muat.siap .lanjut { opacity: .9; visibility: visible; }
  #muat.siap { cursor: pointer; }
  @media (prefers-reduced-motion: reduce) { #muat { transition: none; } }
</style>
</head>
<body>
<div id="muat" role="status" aria-label="Memuat Padma Group">
''' + svg + '''
<button type="button" class="lanjut" id="lanjut">Ketuk untuk melanjutkan</button>
<div class="putus">Tidak ada koneksi internet. Dashboard terbuka otomatis begitu tersambung.</div>
</div>
<iframe id="dasbor" src="''' + EXEC + '''"
        title="Padma Group"
        allow="camera; clipboard-read; clipboard-write; fullscreen; geolocation"></iframe>
<script>
/* Pembungkus Padma Group (2026-09-24). Layar muat hitam = laser mengukir logo
   Padma dan FirstJet bersamaan, SEKALI (~14,4 dtk), dilepas waktu
   dashboard mengirim "siap" (postMessage). Pesan hanya diterima dari domain
   Google. Jaring pengaman 25 dtk; ?tahan=1 menahan layar ini (uji). */
(function () {
  var muat = document.getElementById('muat');
  var dasbor = document.getElementById('dasbor');
  var h = document.documentElement;
  var bilah = document.getElementById('warnaBilah');
  var jalan = true, siap = false, animSelesai = false, mulai = Date.now();
  var TAHAN = /[?&]tahan=1/.test(location.search);

  function simpan(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function lepas() {
    if (!jalan || TAHAN) return;
    jalan = false;
    muat.classList.add('lepas');
    warnaBilah();
    setTimeout(function () { muat.style.display = 'none'; }, 300);
  }
  function warnaBilah() {
    if (jalan) return;  // layar muat masih tampil: bilah tetap hitam
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
    if (d.jenis === 'siap') { siap = true; siapLanjut(); }
  });
  /* Masuk = laser selesai DAN dashboard siap. Siap lebih dulu -> tombol lanjut
     (atau ketuk di mana saja); laser selesai lebih dulu -> masuk begitu siap.
     Jaring 25 dtk tetap: "siap" bisa tidak pernah datang. */
  function siapLanjut() {
    if (animSelesai) lepas();
    else muat.classList.add('siap');
  }
  muat.addEventListener('click', function () { if (siap) lepas(); });
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

  /* Laser, SEKALI (2026-09-24): Padma dan FirstJet diukir bersamaan, satu
     titik laser per logo (garis tepi 9 dtk, lalu isi diarsir 5 dtk -- dulu 2,6 +
     1,3 lalu 5 + 3 dtk, pemilik dua kali: "kecepetan"); sesudah itu diam sampai
     "siap". Luncur antar-goresan 0,35 x
     jarak dengan titik mati, seperti agLaserMulai_ di Index.html. */
  var D = ''' + DATA_LASER + ''';
  var svg = document.getElementById('laser');
  var JADWAL = [  // ms sejak halaman dibuka
    { tepi: [0, 9000], arsir: [9000, 14000], logo: svg.querySelector('.padma') },
    { tepi: [0, 9000], arsir: [9000, 14000], logo: svg.querySelector('.firstjet') }
  ];
  var PUDAR_MS = 400, AKHIR = 14000 + PUDAR_MS;
  JADWAL.forEach(function (J, n) {
    J.gores = Array.prototype.slice.call(J.logo.querySelectorAll('.gores'));
    J.tirai = J.logo.querySelector('.tirai');
    J.baris = D.baris[n];
    /* pathLength=1: dash dinormalkan peramban sendiri. getTotalLength dan panjang
       yang digambar tidak persis sama -> tanpa ini potongan garis FirstJet sudah
       tampil sebelum gilirannya (terlihat di pratinjau). */
    J.tepiG = J.logo.querySelector('.tepi');
    J.titik = [J.logo.querySelector('.titik'), J.logo.querySelector('.halo')];
    J.pj = J.gores.map(function (g) {
      g.setAttribute('pathLength', 1); g.style.strokeDasharray = '1 2'; g.style.strokeDashoffset = 1;
      return g.getTotalLength();
    });
    J.ruas = []; J.total = 0;
    J.gores.forEach(function (g, i) {
      if (i > 0) {
        // kontur tertutup: ujung goresan sebelumnya = titik awalnya
        var a = J.gores[i - 1].getPointAtLength(0), b = g.getPointAtLength(0);
        var d = Math.hypot(b.x - a.x, b.y - a.y);
        if (d > 0.5) { J.ruas.push({ luncur: true, L: d * 0.35 }); J.total += d * 0.35; }
      }
      J.ruas.push({ luncur: false, i: i, L: J.pj[i] }); J.total += J.pj[i];
    });
    /* Arsiran: panjang sapuan tiap baris = jumlah rentang terisi; baris genap
       kiri->kanan, ganjil kanan->kiri, loncat antar-rentang dengan laser mati. */
    J.sapu = J.baris.map(function (b) { return b[1].reduce(function (t, r) { return t + (r[1] - r[0]); }, 0); });
    J.sapuTotal = J.sapu.reduce(function (t, x) { return t + x; }, 0);
    J.atas = J.baris[0][0] - 3;
    J.tirai.setAttribute('y', J.atas);
  });
  function mulus(x) { return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2; }
  function jalur(dt, r) { return Math.max(0, Math.min(1, (dt - r[0]) / (r[1] - r[0]))); }

  function tepi(J, p) {  // -> posisi titik laser, atau null (mati/diam)
    var sisa = J.total * mulus(p), pos = null, aktif = p > 0 && p < 1;
    J.ruas.forEach(function (s) {
      var ambil = Math.max(0, Math.min(s.L, sisa));
      if (!s.luncur) {
        J.gores[s.i].style.strokeDashoffset = 1 - ambil / s.L;
        if (aktif && ambil > 0 && ambil < s.L) pos = J.gores[s.i].getPointAtLength(ambil);
      }
      sisa -= ambil;
    });
    return pos;
  }
  function arsir(J, p) {
    var sisa = J.sapuTotal * p, n = J.baris.length;
    for (var i = 0; i < n; i++) {
      if (sisa > J.sapu[i] && i < n - 1) { sisa -= J.sapu[i]; continue; }
      var y = J.baris[i][0], rent = J.baris[i][1], pos = null;
      if (i % 2) rent = rent.map(function (r) { return [r[1], r[0]]; }).reverse();
      var maju = Math.min(sisa, J.sapu[i]);
      for (var k = 0; k < rent.length; k++) {
        var L = Math.abs(rent[k][1] - rent[k][0]);
        if (maju <= L) { pos = { x: rent[k][0] + (rent[k][1] > rent[k][0] ? maju : -maju), y: y }; break; }
        maju -= L;
      }
      // isi terbuka sampai baris yang sedang disapu; selesai = terbuka semua
      // (p = 0: tertutup total -- tanpa ini 3 satuan teratas isi sudah tampil
      // sejak awal, terlihat sebagai garis putus-putus di atas FIRSTJET)
      J.tirai.setAttribute('height', p <= 0 ? 0 : Math.max(0, (p >= 1 ? y + 60 : y) - J.atas));
      return p > 0 && p < 1 ? pos : null;
    }
    return null;
  }
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
    var dt = Date.now() - mulai;
    JADWAL.forEach(function (J) {
      var pt = jalur(dt, J.tepi);
      var pt2 = tepi(J, pt), pos = arsir(J, jalur(dt, J.arsir)) || pt2;  // dua-duanya selalu dijalankan (tirai)
      // garis tepi: tak tampil sebelum gilirannya, pudar 400 ms sesudah isi penuh
      J.tepiG.style.opacity = pt > 0 ? 1 - jalur(dt, [J.arsir[1], J.arsir[1] + PUDAR_MS]) : 0;
      J.titik.forEach(function (c, i) {
        if (pos) { c.setAttribute('cx', pos.x); c.setAttribute('cy', pos.y); c.setAttribute('opacity', i ? 0.45 : 1); }
        else c.setAttribute('opacity', 0);
      });
    });
    if (dt >= AKHIR) { animSelesai = true; if (siap) lepas(); return; }
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
    "background_color": "#000000",
    "theme_color": "#000000",
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
const VERSI = 'padma-pembungkus-v2';
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
print('ok', len(html), 'iou padma', PADMA['iou'], 'firstjet', FJ['iou'])
