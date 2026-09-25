"""Membangun ikon PWA Padma Group. Pakai: python bangun-ikon.py <folder repo pembungkus>

2026-09-25 malam (pemilik, sesudah memakai logo Padma Notes: "kok logonya ga HD
ya kayak burem", "maybe the logo should be plain white and make it black"):
LOGO PUTIH POLOS DARI VEKTOR, LATAR HITAM. Gambar Padma Notes (icon_fg.png)
lembut karena ia sendiri hasil perbesaran gambar kecil -- memperbesarnya lagi
tidak bisa mengembalikan tepi. Tepi di sini dari path jiplakan (jiplak_logo.py),
diisi putih rata, sampel 4x lalu dikecilkan: tajam di ukuran berapa pun.

Porsi tetap milik Padma Notes: maskable 61,8% (ikon launcher = splash Android
12+, lingkaran tampak 66,7% -- cincin utuh), "any" 72%.

Latar #000000, dan background_color manifest ikut hitam (SPLASH_LATAR di
bangun-pembungkus.py) supaya kotak ikon tidak terlihat di splash. Layar muat
laser sesudahnya TETAP gelap #16181C (permintaan lama "bukan hitam tapi gelap").

Riwayat: vektor + cat perak ikon APK lama (0,68 -> 0,58 -> 0,34 -> 0,46), lalu
logo Padma Notes apa adanya 0,618 (pembungkus 51f9c78) -- lihat git log."""
import os, re, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jiplak_logo import jiplak

OUT = sys.argv[1]
ALAT = os.path.dirname(os.path.abspath(__file__))
PADMA = jiplak(os.path.join(ALAT, 'logo-padma.jpg'), 'terang', 100, 0, 'luas')
SUPER = 4  # sampel lebih lalu dikecilkan = tepi halus
LATAR = (0, 0, 0)          # BGR hitam = SPLASH_LATAR di bangun-pembungkus.py
LOGO = (255, 255, 255)     # putih polos


def subpath(d):
    """Path M/C/L/Z absolut -> daftar poligon (Bezier dipecah 16 langkah)."""
    tok = re.findall(r'[MCLZ]|-?\d*\.?\d+', d)
    i, polis, cur, pos = 0, [], [], (0.0, 0.0)
    while i < len(tok):
        c = tok[i]; i += 1
        if c == 'M':
            if cur: polis.append(cur)
            pos = (float(tok[i]), float(tok[i + 1])); i += 2; cur = [pos]
        elif c == 'L':
            pos = (float(tok[i]), float(tok[i + 1])); i += 2; cur.append(pos)
        elif c == 'C':
            p = [float(x) for x in tok[i:i + 6]]; i += 6
            x0, y0 = pos
            for k in range(1, 17):
                t = k / 16; u = 1 - t
                cur.append((u**3 * x0 + 3 * u * u * t * p[0] + 3 * u * t * t * p[2] + t**3 * p[4],
                            u**3 * y0 + 3 * u * u * t * p[1] + 3 * u * t * t * p[3] + t**3 * p[5]))
            pos = (p[4], p[5])
        elif c == 'Z':
            if cur: polis.append(cur)
            cur = []
    if cur: polis.append(cur)
    return polis


def ikon(ukuran, porsi):
    """Logo putih selebar `porsi` x ukuran, di tengah kanvas hitam."""
    n = ukuran * SUPER
    k = PADMA['kotak']; lebar = max(k[2] - k[0], k[3] - k[1])
    skala = n * porsi / lebar
    cx, cy = (k[0] + k[2]) / 2, (k[1] + k[3]) / 2
    masker = np.zeros((n, n), np.uint8)
    for poli in subpath(PADMA['isi']):  # evenodd = XOR tiap subpath
        m = np.zeros_like(masker)
        pts = np.array([[(x - cx) * skala + n / 2, (y - cy) * skala + n / 2] for x, y in poli])
        cv2.fillPoly(m, [np.round(pts * 16).astype(np.int32)], 255, lineType=cv2.LINE_AA, shift=4)
        masker = cv2.bitwise_xor(masker, (m > 127).astype(np.uint8) * 255)
    a = masker[..., None].astype(np.float32) / 255.0
    rgb = np.array(LOGO, np.float32) * a + np.array(LATAR, np.float32) * (1 - a)
    kecil = cv2.resize(rgb, (ukuran, ukuran), interpolation=cv2.INTER_AREA)
    return np.clip(np.round(kecil), 0, 255).astype(np.uint8)


for uk in (192, 512):
    cv2.imwrite(os.path.join(OUT, 'icon-%d.png' % uk), ikon(uk, 0.72))
    cv2.imwrite(os.path.join(OUT, 'icon-maskable-%d.png' % uk), ikon(uk, 0.618))
print('ok')
