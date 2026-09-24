"""Membangun halaman pembungkus Padma Group (GitHub Pages teknik-padma/dashboard).
Pakai: python bangun-pembungkus.py <folder repo pembungkus>
Menulis index.html, manifest.json, sw.js, favicon.svg (ikon PNG: alat/bangun-ikon.py)."""
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
# Kotak pandang sedikit lebih lebar/tinggi dari logonya (dulu memuat lencana
# biru FirstJet; lencananya dibuang 2026-09-24, ukuran dibiarkan supaya logo
# tidak berubah besar).
# Diketengahkan 2026-09-25 (dulu x -118: logonya -112,4..112,6, jadi margin
# kiri 5,6 dan kanan 17,4 satuan -- terlihat waktu logonya dibesarkan).
VB = (-124, -64, 248, 128)
assert PADMA['kotak'][0] + GESER > VB[0] and FJ['kotak'][2] < VB[0] + VB[2], (PADMA['kotak'], FJ['kotak'])


def logo_svg(kelas, L, isi):
    gores = ''.join('<path class="gores" d="%s"/>' % d for d in L['gores'])
    return ('<g class="%s">'
            '<clipPath id="arsir-%s"><rect class="tirai" x="-200" y="-70" width="400" height="0"/></clipPath>'
            '<path class="isi" fill="%s" fill-rule="evenodd" clip-path="url(#arsir-%s)" d="%s"/>'
            '<g class="tepi" fill="none" stroke="currentColor" stroke-width=".8" stroke-linejoin="round" opacity="0">%s</g>'
            '<circle class="halo" r="3.2" fill="#fff" opacity="0"/><circle class="titik" r="1.1" fill="#fff" opacity="0"/>'
            '</g>') % (kelas, kelas, isi, kelas, L['isi'], gores)


# Diukir putih polos ("putih aja, jangan abu") dan TETAP putih sampai dashboard
# siap. Warna asli sesudah laser selesai (Padma perak, FirstJet kotak biru
# #094B84, commit 770c313) dibuang 2026-09-24: "hapus aja deh ide warna".
# Ikon tab browser (2026-09-24, diminta "logo padma tanpa background"): hanya
# logo Padma, latar transparan -- icon-192.png berlatar hitam tetap untuk
# PWA/apple-touch. Perak asli tenggelam di tab terang, jadi tab terang memakai
# perak gelap; tab gelap perak asli gambarnya (terang ~205 di tengah, ~155 di tepi; media query di dalam SVG, didukung Chrome/Firefox).
K = PADMA['kotak']
ikon_tab = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f">' % (K[0] - 1, K[1] - 1, K[2] - K[0] + 2, K[3] - K[1] + 2)
            + '<style>.t{stop-color:#7A7A7A}.m{stop-color:#5A5A5A}.g{stop-color:#3A3A3A}'
            '@media (prefers-color-scheme:dark){.t{stop-color:#D2D2D2}.m{stop-color:#B2B2B2}.g{stop-color:#8E8E8E}}</style>'
            '<defs><radialGradient id="p" gradientUnits="userSpaceOnUse" cx="0" cy="6" r="58">'
            '<stop offset="0" class="t"/><stop offset=".5" class="m"/><stop offset="1" class="g"/></radialGradient></defs>'
            '<path fill="url(#p)" fill-rule="evenodd" d="%s"/></svg>\n' % PADMA['isi'])
svg = ('<svg id="laser" viewBox="%d %d %d %d" aria-hidden="true">' % VB
       + '<g transform="translate(%s 0)">' % GESER + logo_svg('padma', PADMA, '#FFFFFF') + '</g>'
       + logo_svg('firstjet', FJ, '#FFFFFF')
       + '</svg>')
# UKURAN = SPLASH ANDROID (2026-09-25, "ukuran logo padma di awal loading
# disamain dengan logo pas animasi laser"). Splash Android 12+ menggambar ikon
# maskable di kanvas 240 dp dan cincin Padma di ikon itu 59% (bangun-ikon.py,
# terukur) -> ~142 px. Cincin di sini 100 dari 248 satuan, jadi kotaknya
# 142 x 248 / 100 = 352 px; dulu 320 px (~129 px, 12% lebih kecil). Dibatasi
# 94vw: HP 360 px jadi ~136 px, FirstJet tetap ~16 px dari tepi.
LEBAR_PX, LEBAR_VW = 352, 94

# POLA LOGO CUSTOMER (2026-09-25, diminta "diganti logo2 customer saja yang
# dibackground ... idle aja cuma ada cahaya jalan2"; menggantikan pola
# Padma-FirstJet yang ikut diukir). Siluet putih dari alat/bangun-pola-customer.py
# (alat/pola-customer/*.png), disajikan sebagai berkas pola/<id>.png -- 160 KB
# ditanam di index.html akan menahan layar muat itu sendiri. Diam; yang
# bergerak hanya kilau. Ubin 5 kolom x 14 baris (sempit-tinggi: layar HP ~3
# kolom x 10 baris tanpa pengulangan; 11x6 dulu berulang di tengah layar), baris
# ganjil bergeser setengah sel. Logo di tepi kanan ubin digambar lagi di kiri.
POLA_DIR = os.path.join(ALAT, 'pola-customer')
CUST = json.load(open(os.path.join(POLA_DIR, 'daftar.json'), encoding='utf-8'))
assert len(CUST) >= 12, len(CUST)
SEL_W, SEL_H, KOLOM, BARIS_POLA = 132, 76, 5, 14
W, H = SEL_W * KOLOM, SEL_H * BARIS_POLA
# POLA BERJALAN (2026-09-25, "apa logonya gerak kesamping horizontal atau
# misal ke barat daya/barat laut ya?"): seluruh pola bergeser TEPAT satu ubin
# lalu berulang -- sambungannya tak terlihat. ARAH: 'barat daya' (kiri-bawah),
# 'barat laut' (kiri-atas) atau 'barat' (horizontal). Transform saja.
ARAH, LAJU_PX_DTK = 'barat daya', 25
GESER_X, GESER_Y = {'barat daya': (-W, H), 'barat laut': (-W, -H), 'barat': (-W, 0)}[ARAH]
JALAN_DTK = round((GESER_X ** 2 + GESER_Y ** 2) ** 0.5 / LAJU_PX_DTK)


def gambar_pola():
    isi = []
    for r in range(BARIS_POLA):
        for c in range(KOLOM):
            i = (r * KOLOM + c) % len(CUST)
            L = CUST[i]
            cx = c * SEL_W + SEL_W / 2 + (SEL_W / 2 if r % 2 else 0)
            cy = r * SEL_H + SEL_H / 2
            for geser in ((0, -W) if cx + L['w'] / 2 > W else (0,)):
                isi.append('<image href="pola/%s.png" x="%.1f" y="%.1f" width="%d" height="%d"/>'
                           % (L['id'], cx + geser - L['w'] / 2, cy - L['h'] / 2, L['w'], L['h']))
    return ''.join(isi)


POLA_SVG = ('<svg class="pola-isi pola-dasar"><defs>'
            '<pattern id="ubin" patternUnits="userSpaceOnUse" width="%d" height="%d" x="-40" y="-10">' % (W, H)
            + gambar_pola()
            + '</pattern></defs><rect width="100%" height="100%" fill="url(#ubin)"/></svg>')
DATA_LASER = json.dumps({
                         'baris': [PADMA['baris'], FJ['baris']]}, separators=(',', ':'))

EXEC = 'https://script.google.com/macros/s/AKfycbzBRPeuPWoL3UdErFpn9WngpqQNiqvf9zH0dOhAsNEGlI1s9Uhm0XIGkWwalLctpwwR/exec'
TERANG_BILAH, GELAP_BILAH = '#FFFFFF', '#16181C'
# Iframe TANPA COOKIE (credentialless, Chrome): obat "Maaf, saat ini tidak dapat
# membuka file" di HP dengan beberapa akun Google (terbukti di HP pemilik lewat
# tanpa-cookie.padmagroup.pages.dev, 2026-09-24). NYALA di situs utama sejak
# 2026-09-25 (pemilik: "tanpa cookie situs utama gas", masih kena error Google).
# Token titipan sudah terkumpul sejak v694; antrean/draf menyusul dititipkan.
TANPA_COOKIE = True

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
<link rel="icon" href="favicon.svg" type="image/svg+xml">
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
  /* Sampai DASAR layar (2026-09-24): dulu tingginya 100% - inset bawah, dan di
     iPhone terpasang "100%" tidak sama dengan tinggi layar -- dilaporkan XR
     "dagunya kok panjang" (~67pt kosong, inset-nya 34pt). Sekarang jarak garis
     home diukur di sini (#ukurAman) dan dikirim ke dashboard (pesan "inset"),
     yang menjadikannya ruang DI DALAM bilah bawahnya. */
  /* top+bottom lewat DIV pembungkus: iframe elemen "replaced", top+bottom tidak
     meregangkannya (tingginya jatuh ke bawaan 150px -- terukur sesudah
     deploy pertama perbaikan ini). */
  #bingkai {
    position: fixed; left: 0; right: 0;
    top: env(safe-area-inset-top, 0px); bottom: 0;
  }
  iframe { width: 100%; height: 100%; border: 0; display: block; }
  #ukurAman { position: fixed; left: 0; bottom: 0; width: 0; height: env(safe-area-inset-bottom, 0px); visibility: hidden; pointer-events: none; }
  #muat {
    position: fixed; inset: 0; z-index: 2; background: #000; color: #fff;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    transition: opacity .55s ease;
  }
  #muat.lepas { opacity: 0; pointer-events: none; }
  #laser { width: min(''' + str(LEBAR_PX) + '''px, ''' + str(LEBAR_VW) + '''vw); height: auto; aspect-ratio: ''' + '%d / %d' % (VB[2], VB[3]) + '''; overflow: visible; }
  #laser .halo { filter: blur(1.4px); }
  .putus {
    margin-top: 18px; font: 600 13px/1.4 Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    opacity: .7; display: none;
  }
  #muat.offline .putus { display: block; }
  /* "Tap to continue" DIBUANG (2026-09-25, "gasuka ada tulisan tap to
     continue ... kalo udah selesai login aja tp yg smooth"): dashboard siap
     sebelum laser selesai -> sisa ukiran disusul dalam SUSUL_MS, lalu pudar. */
  /* POLA LOGO CUSTOMER (2026-09-25): siluet putih samar, diam; kilau menyapu
     = salinan pola yang sama, lebih terang, di dalam pita yang lewat. */
  #laser, .putus { position: relative; z-index: 1; }
  .pola { position: absolute; inset: 0; overflow: hidden; pointer-events: none; opacity: .5;
    -webkit-mask-image: radial-gradient(ellipse 62% 40% at 50% 47%, transparent 30%, #000 78%);
            mask-image: radial-gradient(ellipse 62% 40% at 50% 47%, transparent 30%, #000 78%); }
  .pola-putar { position: absolute; inset: 0; }
  /* Lebih besar satu ubin ke arah datangnya pola, supaya layar tetap tertutup
     sepanjang geseran. Salinan terang di pita kilau ikut bergerak bersama
     (animasi sama, mulai bersamaan). */
  .pola-isi { position: absolute; display: block; left: ''' + ('%dpx' % (-GESER_X if GESER_X > 0 else 0)) + ''';
    top: ''' + ('%dpx' % (-GESER_Y if GESER_Y > 0 else 0)) + ''';
    width: calc(100% + ''' + str(abs(GESER_X)) + '''px); height: calc(100% + ''' + str(abs(GESER_Y)) + '''px);
    will-change: transform; animation: polaJalan ''' + str(JALAN_DTK) + '''s linear infinite; }
  @keyframes polaJalan { from { transform: translate(0, 0); }
    to { transform: translate(''' + str(GESER_X) + '''px, ''' + str(GESER_Y) + '''px); } }
  .pola-dasar { opacity: .22; }
  .kilau-pita { position: absolute; top: 0; bottom: 0; left: 0; width: 260px; overflow: hidden;
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 45%, #000 55%, transparent);
            mask-image: linear-gradient(90deg, transparent, #000 45%, #000 55%, transparent);
    transform: translateX(-300px); animation: kilauPita 5s ease-in-out infinite; }
  .kilau-isi { position: absolute; top: 0; bottom: 0; left: 0; width: 100vw; animation: kilauIsi 5s ease-in-out infinite; }
  @keyframes kilauPita { 0% { transform: translateX(-300px); } 45%, 100% { transform: translateX(calc(100vw + 40px)); } }
  @keyframes kilauIsi  { 0% { transform: translateX(300px); }  45%, 100% { transform: translateX(calc(-100vw - 40px)); } }
  /* Kamera Scan QR untuk dashboard (2026-09-24): iframe Apps Script tidak
     diberi izin kamera oleh bingkai Google, halaman ini boleh. */
  #kamera {
    position: fixed; inset: 0; z-index: 3; background: #000; color: #fff;
    display: none; font: 600 14px/1.4 Inter, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  #kamera.buka { display: block; }
  #kamera video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
  #kamera .bingkai {
    position: absolute; left: 50%; top: 50%; width: min(64vw, 280px); aspect-ratio: 1;
    transform: translate(-50%, -50%); border: 2px solid rgba(255, 255, 255, .85); border-radius: 18px;
    box-shadow: 0 0 0 100vmax rgba(0, 0, 0, .45);
  }
  #kamera .petunjuk {
    position: absolute; left: 16px; right: 16px; bottom: calc(28px + env(safe-area-inset-bottom, 0px));
    text-align: center;
  }
  #kamera .tutup {
    position: absolute; top: calc(12px + env(safe-area-inset-top, 0px)); right: 12px;
    width: 44px; height: 44px; border-radius: 999px; border: 0; background: rgba(0, 0, 0, .55);
    color: #fff; font-size: 22px; line-height: 44px; cursor: pointer;
  }
  @media (prefers-reduced-motion: reduce) {
    #muat { transition: none; }
    .kilau-pita, .kilau-isi, .pola-isi { animation: none; }
    .kilau-pita { display: none; }
  }
</style>
</head>
<body>
<div id="muat" role="status" aria-label="Memuat Padma Group">
<div class="pola" aria-hidden="true"><div class="pola-putar">''' + POLA_SVG + '''<div class="kilau-pita"><div class="kilau-isi"><svg class="pola-isi"><rect width="100%" height="100%" fill="url(#ubin)"/></svg></div></div></div></div>
''' + svg + '''
<div class="putus">Tidak ada koneksi internet. Dashboard terbuka otomatis begitu tersambung.</div>
</div>
<div id="kamera" role="dialog" aria-label="Scan QR Mesin">
<video id="kameraVideo" playsinline muted></video>
<div class="bingkai" aria-hidden="true"></div>
<div class="petunjuk" id="kameraPetunjuk">Arahkan kamera ke QR di stiker mesin.</div>
<button type="button" class="tutup" id="kameraTutup" aria-label="Tutup kamera">&times;</button>
</div>
<div id="ukurAman" aria-hidden="true"></div>
<div id="bingkai"><iframe id="dasbor"''' + (' credentialless' if TANPA_COOKIE else '') + ''' src="''' + EXEC + '''"
        title="Padma Group"
        allow="camera; clipboard-read; clipboard-write; fullscreen; geolocation"></iframe></div>
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
  /* Jam laser: normal = ms sejak dibuka; sesudah "siap" dipercepat supaya sisa
     ukiran selesai dalam SUSUL_MS (tidak dipotong, tidak ditunggu). */
  var SUSUL_MS = 1100, susul = null;
  function waktu() {
    var kini = Date.now();
    return susul ? susul.dt0 + (kini - susul.t0) * susul.laju : kini - mulai;
  }
  var TAHAN = /[?&]tahan=1/.test(location.search);

  function simpan(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function titipBaca() {
    try { var t = JSON.parse(localStorage.getItem('padmaTitip') || '{}'); return (t && typeof t === 'object') ? t : {}; } catch (e) { return {}; }
  }
  function titipTulis(t) {
    try { localStorage.setItem('padmaTitip', JSON.stringify(t)); } catch (e) { console.warn('titipan gagal disimpan', e); }
  }
  function lepas() {
    if (!jalan || TAHAN) return;
    jalan = false;
    muat.classList.add('lepas');
    warnaBilah();
    setTimeout(function () { muat.style.display = 'none'; }, 600);
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
    /* Dijawab tiap pesan tema (tiap dashboard dimuat): "ada kamera di sini".
       Dashboard yang mendengarnya memakai kamera halaman ini untuk Scan QR. */
    /* Dijawab tiap pesan tema: "ada pembungkus", kamera tersedia atau tidak,
       dan TOKEN TITIPAN. Iframe tanpa cookie (credentialless) kehilangan
       localStorage tiap aplikasi ditutup, jadi token login disimpan di sini
       dan diserahkan balik; hanya ke bingkai Google (asal sudah disaring). */
    if (d.jenis === 'tema' && e.source) {
      var kamera = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
      var tokenTitip = '';
      try { tokenTitip = localStorage.getItem('padmaToken') || ''; } catch (err) {}
      try { e.source.postMessage({ padma: 1, jenis: 'pembungkus', kamera: kamera, token: tokenTitip, muatUlang: true, titipan: titipBaca() }, asal); } catch (err) {}
    }
    /* TITIPAN SIMPANAN (2026-09-25, dashboard v700): antrean simpan, draf dan
       pengaturan dashboard dicerminkan ke sini, karena localStorage iframe
       tanpa cookie hilang tiap aplikasi ditutup. Hanya kunci padma_*; satu
       objek JSON di kunci padmaTitip. titipSemua = salinan utuh (acuan). */
    if (d.jenis === 'titip' && typeof d.k === 'string' && /^padma_[A-Za-z0-9_:@.+-]{1,200}$/.test(d.k)
        && (d.v === null || (typeof d.v === 'string' && d.v.length <= 1000000))) {
      var t = titipBaca();
      if (d.v === null) delete t[d.k]; else t[d.k] = d.v;
      titipTulis(t);
    }
    if (d.jenis === 'titipSemua' && d.isi && typeof d.isi === 'object') {
      var baru = {};
      Object.keys(d.isi).forEach(function (k) {
        var v = d.isi[k];
        if (/^padma_[A-Za-z0-9_:@.+-]{1,200}$/.test(k) && typeof v === 'string' && v.length <= 1000000) baru[k] = v;
      });
      titipTulis(baru);
    }
    if (d.jenis === 'simpanToken' && typeof d.token === 'string' && d.token.length < 2000) {
      try { if (d.token) localStorage.setItem('padmaToken', d.token); else localStorage.removeItem('padmaToken'); } catch (err) {}
    }
    if (d.jenis === 'tema' && e.source) { sumberDasbor = { w: e.source, asal: asal }; kirimAman(); }
    if (d.jenis === 'pindaiQr' && typeof d.id === 'string' && e.source) kameraBuka(e.source, asal, d.id);
    /* Muat ulang SENYAP atas permintaan dashboard (2026-09-25): sesudah Keluar dan
       sebelum login ulang. Bingkai Google yang me-reload dirinya sendiri berakhir
       layar putih; halaman ini boleh. Diumumkan lewat muatUlang:true di atas. */
    if (d.jenis === 'muatUlang') location.reload();
    /* Tautan tiket Scan QR dibuka langsung (diminta "gausah diklik dulu"):
       halaman puncak boleh pindah tanpa ketukan, iframe tidak. Hanya
       script.google.com -- pesan dari Google pun tidak boleh membawa ke
       situs lain. Tombol Kembali pulang ke dashboard. */
    if (d.jenis === 'buka' && typeof d.url === 'string' && d.url.indexOf('https://script.google.com/') === 0) {
      location.href = d.url;
    }
  });

  /* Jarak aman bawah (garis home iPhone) ke dashboard, tiap dimuat dan tiap
     layar berputar. iframe tidak bisa membaca env() sendiri. */
  var sumberDasbor = null;
  function kirimAman() {
    if (!sumberDasbor) return;
    var px = document.getElementById('ukurAman').getBoundingClientRect().height || 0;
    try { sumberDasbor.w.postMessage({ padma: 1, jenis: 'inset', bawah: px }, sumberDasbor.asal); } catch (err) {}
  }
  window.addEventListener('resize', function () { setTimeout(kirimAman, 150); });

  /* KAMERA SCAN QR (2026-09-24). Dashboard meminta lewat postMessage, halaman
     ini membuka kamera belakang, membaca QR (BarcodeDetector, kalau tidak ada
     jsQR 1.4.0 dari jsDelivr, sama dengan dashboard), lalu mengirim
     TEKS:... / BATAL / IZIN / GAGAL ke id yang diminta. */
  var JSQR = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
  var JSQR_SRI = 'sha384-hStSInNIZ8ljtOVrmrgf7zdHMapaLBWoSnPTtF0nzsybp4+LuhDz6sHuEVpWIX8o';
  var kam = { el: document.getElementById('kamera'), video: document.getElementById('kameraVideo'),
              stream: null, minta: null, jam: 0, detektor: undefined, jsqr: null, kanvas: null };
  function kameraJawab(hasil) {
    var m = kam.minta;
    kam.minta = null;
    kameraMati();
    if (m) { try { m.sumber.postMessage({ padma: 1, jenis: 'hasilPindai', id: m.id, hasil: hasil }, m.asal); } catch (err) {} }
  }
  function kameraMati() {
    if (kam.jam) { clearTimeout(kam.jam); kam.jam = 0; }
    if (kam.stream) { kam.stream.getTracks().forEach(function (t) { try { t.stop(); } catch (err) {} }); kam.stream = null; }
    kam.video.srcObject = null;
    kam.el.classList.remove('buka');
  }
  function kameraDetektor() {
    if (kam.detektor !== undefined) return Promise.resolve(kam.detektor);
    if (!('BarcodeDetector' in window)) { kam.detektor = null; return Promise.resolve(null); }
    var f = BarcodeDetector.getSupportedFormats ? BarcodeDetector.getSupportedFormats() : Promise.resolve(['qr_code']);
    return f.then(function (x) {
      kam.detektor = (x || []).indexOf('qr_code') !== -1 ? new BarcodeDetector({ formats: ['qr_code'] }) : null;
      return kam.detektor;
    }).catch(function () { kam.detektor = null; return null; });
  }
  function kameraJsqr() {
    if (window.jsQR) return Promise.resolve(window.jsQR);
    if (kam.jsqr) return kam.jsqr;
    kam.jsqr = new Promise(function (beres, gagal) {
      var s = document.createElement('script');
      s.src = JSQR; s.integrity = JSQR_SRI; s.crossOrigin = 'anonymous';
      s.onload = function () { window.jsQR ? beres(window.jsQR) : gagal(new Error('jsQR kosong')); };
      s.onerror = function () { kam.jsqr = null; gagal(new Error('Pembaca QR gagal dimuat. Periksa internet.')); };
      document.head.appendChild(s);
    });
    return kam.jsqr;
  }
  function kameraBaca() {
    var v = kam.video;
    return kameraDetektor().then(function (det) {
      if (det) return det.detect(v).then(function (h) { return (h && h[0] && h[0].rawValue) || ''; });
      return kameraJsqr().then(function (jsQR) {
        var sk = Math.min(1, 720 / Math.max(v.videoWidth, v.videoHeight));
        var w = Math.max(1, Math.round(v.videoWidth * sk)), h = Math.max(1, Math.round(v.videoHeight * sk));
        var k = kam.kanvas || (kam.kanvas = document.createElement('canvas'));
        k.width = w; k.height = h;
        var cx = k.getContext('2d', { willReadFrequently: true });
        cx.drawImage(v, 0, 0, w, h);
        var r = jsQR(cx.getImageData(0, 0, w, h).data, w, h, { inversionAttempts: 'dontInvert' });
        return (r && r.data) || '';
      });
    });
  }
  /* setTimeout, bukan rAF: rAF bisa tidak pernah datang (tab tanpa komposit). */
  function kameraPutar() {
    kam.jam = 0;
    if (!kam.stream || !kam.minta) return;
    var v = kam.video;
    if (v.readyState < 2 || !v.videoWidth) { kam.jam = setTimeout(kameraPutar, 200); return; }
    kameraBaca().then(function (teks) {
      if (!kam.stream || !kam.minta) return;
      if (teks) { kameraJawab('TEKS:' + teks); return; }
      kam.jam = setTimeout(kameraPutar, 250);
    }).catch(function (err) {
      document.getElementById('kameraPetunjuk').textContent = (err && err.message) || 'Pembaca QR bermasalah.';
      kam.jam = setTimeout(kameraPutar, 1500);
    });
  }
  function kameraBuka(sumber, asal, id) {
    if (kam.minta) kameraJawab('BATAL');  // permintaan lama digantikan
    kam.minta = { sumber: sumber, asal: asal, id: id };
    document.getElementById('kameraPetunjuk').textContent = 'Arahkan kamera ke QR di stiker mesin.';
    kam.el.classList.add('buka');
    navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false })
      .then(function (stream) {
        if (!kam.minta || kam.minta.id !== id) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
        kam.stream = stream;
        kam.video.srcObject = stream;
        var main = kam.video.play();
        if (main && main.catch) main.catch(function () {});
        kam.jam = setTimeout(kameraPutar, 300);
      })
      .catch(function (err) {
        if (!kam.minta || kam.minta.id !== id) return;
        kameraJawab(err && (err.name === 'NotAllowedError' || err.name === 'SecurityError') ? 'IZIN' : 'GAGAL');
      });
  }
  document.getElementById('kameraTutup').addEventListener('click', function () { kameraJawab('BATAL'); });
  /* Pindah aplikasi / layar mati: kamera dimatikan, dashboard diberi BATAL
     supaya tombol "Pindai lagi" muncul di sana. */
  document.addEventListener('visibilitychange', function () { if (document.hidden && kam.minta) kameraJawab('BATAL'); });
  /* Masuk = laser selesai DAN dashboard siap. Siap lebih dulu -> jam laser
     dipercepat (sisa ukiran dalam SUSUL_MS), lalu pudar sendiri; laser selesai
     lebih dulu -> masuk begitu siap. Jaring 25 dtk tetap. */
  function siapLanjut() {
    if (animSelesai) { lepas(); return; }
    if (susul) return;
    var dt = waktu();
    susul = { t0: Date.now(), dt0: dt, laju: Math.max(1, (AKHIR - dt) / SUSUL_MS) };
  }
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
    /* Tabel titik tiap 0,8 satuan, dihitung SEKALI. Dulu getPointAtLength
       dipanggil tiap frame pada path ribuan huruf -- ikut membuat laser
       "kadang patah" di HP, bersama dashboard yang sedang dimuat di utas yang
       sama (iframe lintas situs di Chrome Android sering satu proses). */
    J.tabel = J.gores.map(function (g, i) {
      var n = Math.max(2, Math.ceil(J.pj[i] / 0.8)), t = new Float32Array(2 * (n + 1));
      for (var k = 0; k <= n; k++) { var q = g.getPointAtLength(J.pj[i] * k / n); t[2 * k] = q.x; t[2 * k + 1] = q.y; }
      return t;
    });
    J.offLama = J.gores.map(function () { return 1; });
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

  function titikDi(t, f) {  // interpolasi linear di tabel titik
    var n = t.length / 2 - 1, x = f * n, k = Math.min(n - 1, Math.floor(x)), r = x - k;
    return { x: t[2 * k] + (t[2 * k + 2] - t[2 * k]) * r, y: t[2 * k + 1] + (t[2 * k + 3] - t[2 * k + 1]) * r };
  }
  function tepi(J, p) {  // -> posisi titik laser, atau null (mati/diam)
    var sisa = J.total * mulus(p), pos = null, aktif = p > 0 && p < 1;
    J.ruas.forEach(function (s) {
      var ambil = Math.max(0, Math.min(s.L, sisa));
      if (!s.luncur) {
        // tulis hanya kalau berubah: goresan yang sudah/belum jalan tidak disentuh
        var off = 1 - ambil / s.L;
        if (off !== J.offLama[s.i]) { J.gores[s.i].style.strokeDashoffset = off; J.offLama[s.i] = off; }
        if (aktif && ambil > 0 && ambil < s.L) pos = titikDi(J.tabel[s.i], ambil / s.L);
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
    var dt = waktu();
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
    if (dt >= AKHIR) {
      animSelesai = true;
      if (siap) lepas();  // belum siap: logo putih diam, masuk begitu "siap" datang
      return;
    }
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
        # ikon maskable terpisah (cincin 80%, zona aman Android), lihat alat/bangun-ikon.py
        {"src": "icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
        {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}

sw = '''/* Service worker pembungkus Padma Group. Hanya berkas pembungkus (situs ini
   sendiri) yang di-cache; dashboard di script.google.com TIDAK pernah disentuh.
   Jaringan dulu supaya pembaruan langsung terpakai; cache kalau offline.
   Naikkan VERSI tiap berkas di BERKAS berubah nama. */
const VERSI = 'padma-pembungkus-v4';
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
import shutil
os.makedirs(os.path.join(OUT, 'pola'), exist_ok=True)
for f in os.listdir(os.path.join(OUT, 'pola')):
    os.remove(os.path.join(OUT, 'pola', f))
for L in CUST:
    shutil.copyfile(os.path.join(POLA_DIR, L['id'] + '.png'), os.path.join(OUT, 'pola', L['id'] + '.png'))
open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8', newline='\n').write(sw)
open(os.path.join(OUT, 'favicon.svg'), 'w', encoding='utf-8', newline='\n').write(ikon_tab)
print('ok', len(html), 'iou padma', PADMA['iou'], 'firstjet', FJ['iou'])
