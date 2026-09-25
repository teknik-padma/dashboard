"""Membangun ikon PWA Padma Group. Pakai: python bangun-ikon.py <folder repo pembungkus>

2026-09-25 (pemilik, menunjuk aplikasi Padma Notes -- WORK\\FIREBASE PAK AAN\\tugas:
"coba pake splash ini aja"): LOGONYA DIAMBIL APA ADANYA DARI PADMA NOTES,
alat/logo-padma-notes.png (= tugas/assets/icon_fg.png, latar depan ikon adaptif
aplikasi itu: teratai + cincin perak, alfa halus, 1024 px). Porsinya pun sama:
logo 61,8% lebar kanvas di ikon maskable, jadi splash Android dashboard sama
besar dengan splash Padma Notes (zona tampak splash Android 12+ = lingkaran
tengah 66,7%, jadi 61,8% masih utuh -- 0,68 dulu terpotong).

Yang DIGANTIKAN: logo jiplakan vektor (jiplak_logo.py) yang dicat dari ikon
launcher APK lama (alat/ikon-lama-512.png) + cincin dicat ulang polar. Riwayat
porsinya (0,68 -> 0,58 -> 0,34 -> 0,46) ada di git log berkas ini.

Latar #101010 = PERSIS Padma Notes (2026-09-25 malam, pemilik: "just use
padmanotes splash and logo", sesudah percobaan putih-polos-di-hitam 2a49e37).
background_color manifest ikut (SPLASH_LATAR di bangun-pembungkus.py); layar
muat laser sesudahnya tetap GELAP_MUAT #16181C -- beda tipis yang diterima."""
import os, sys
import numpy as np, cv2

OUT = sys.argv[1]
ALAT = os.path.dirname(os.path.abspath(__file__))
LOGO = cv2.imread(os.path.join(ALAT, 'logo-padma-notes.png'), cv2.IMREAD_UNCHANGED).astype(np.float32)
LATAR = (0x10, 0x10, 0x10)  # BGR #101010 = latar ikon adaptif Padma Notes = SPLASH_LATAR

# Kotak logo diukur dari alfanya (bukan angka tetap), supaya berkas pengganti
# dengan tepi berbeda tetap diketengahkan dan diskalakan dengan benar.
_ys, _xs = np.where(LOGO[..., 3] > 8)
KOTAK = (_xs.min(), _ys.min(), _xs.max() + 1, _ys.max() + 1)


def ikon(ukuran, porsi):
    """Logo selebar `porsi` x ukuran, di tengah kanvas berlatar LATAR."""
    x0, y0, x1, y1 = KOTAK
    potong = LOGO[y0:y1, x0:x1]
    lebar = max(x1 - x0, y1 - y0)
    sisi = porsi * ukuran / lebar
    w, h = max(1, round((x1 - x0) * sisi)), max(1, round((y1 - y0) * sisi))
    kecil = cv2.resize(potong, (w, h), interpolation=cv2.INTER_AREA)
    kanvas = np.zeros((ukuran, ukuran, 3), np.float32) + np.array(LATAR, np.float32)
    ox, oy = (ukuran - w) // 2, (ukuran - h) // 2
    a = kecil[..., 3:4] / 255.0
    bidang = kanvas[oy:oy + h, ox:ox + w]
    kanvas[oy:oy + h, ox:ox + w] = kecil[..., :3] * a + bidang * (1 - a)
    return np.clip(np.round(kanvas), 0, 255).astype(np.uint8)


for uk in (192, 512):
    # "any" (favicon, launcher tanpa masker): logo 72%, sama dengan sebelumnya.
    cv2.imwrite(os.path.join(OUT, 'icon-%d.png' % uk), ikon(uk, 0.72))
    # maskable = ikon launcher + splash Android 12+: porsi Padma Notes.
    cv2.imwrite(os.path.join(OUT, 'icon-maskable-%d.png' % uk), ikon(uk, 0.618))
print('ok')
