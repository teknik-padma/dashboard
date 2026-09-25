"""Membangun ikon PWA Padma Group dari path logo hasil jiplak (vektor, bukan
memperbesar gambar lama). Pakai: python bangun-ikon.py <folder repo pembungkus>

2026-09-24, dilaporkan "logo di hape pas di install kekecilan": ikon lama dari
ikon launcher APK, cincinnya cuma ~42% lebar ikon. Sekarang:
  icon-*.png           purpose "any"      cincin 80% lebar
  icon-maskable-*.png  purpose "maskable" cincin 68%: zona aman Android lingkaran
                       80%, dan 80% pas di batasnya ternyata terpotong di HP
                       (dilaporkan "kepotong ujung2nya") -- disisakan ruang.
Latar #16181C (sama dengan layar muat + background_color manifest, 2026-09-25:
dulu #000, terlihat sebagai kotak hitam di splash Android yang latarnya #16181C).

WARNANYA DARI IKON LAMA, TEPINYA DARI VEKTOR (2026-09-24, dilaporkan "shadow2nya
hilang, malah plain grey" pada versi perak radial rata): alat/ikon-lama-512.png
(ikon launcher APK, logo 214px) diperbesar Lanczos lalu di-dilate supaya
kilaunya menjangkau tepi, dan masker vektor yang memotong tepinya -- jadi kilau
logam aslinya ikut, tepinya tetap tajam walau diperbesar ~1,9x."""
import os, re, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jiplak_logo import jiplak

OUT = sys.argv[1]
ALAT = os.path.dirname(os.path.abspath(__file__))
PADMA = jiplak(os.path.join(ALAT, 'logo-padma.jpg'), 'terang', 100, 0, 'luas')
SUPER = 4  # sampel lebih lalu dikecilkan = tepi halus
LAMA = cv2.imread(os.path.join(ALAT, 'ikon-lama-512.png'))[..., :3].astype(np.float32)


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


LATAR = (0x1C, 0x18, 0x16)  # BGR dari #16181C = GELAP_MUAT di bangun-pembungkus.py


def ikon(ukuran, porsi):
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
    # cat dari ikon lama: kotak logonya (148..362) dipetakan ke kotak logo vektor
    sisi = int(round(lebar * skala))
    cat = cv2.resize(LAMA[148:363, 148:363], (sisi, sisi), interpolation=cv2.INTER_LANCZOS4)
    cat = cv2.dilate(cat, np.ones((5 * SUPER, 5 * SUPER), np.uint8))
    kanvas = np.zeros((n, n, 3), np.float32)
    o = (n - sisi) // 2
    kanvas[o:o + sisi, o:o + sisi] = cat
    # CINCIN DICAT ULANG LEWAT KOORDINAT POLAR (2026-09-24, dilaporkan di layar
    # splash "logo padma kepotong di ujung2nya"). Cincin ikon lama terpangkas
    # datar di 0/90/180/270 derajat (jari-jari luar 104 lawan 107 di diagonal),
    # jadi di ujung-ujung masker vektor catnya gelap. Tiap piksel cincin vektor
    # kini mengambil warna cincin lama di SUDUT yang sama, dari pita r 100,5-
    # 103,5 yang utuh di semua sudut -- kilau logamnya tetap asli.
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    dx, dy = xx - n / 2 + 0.5, yy - n / 2 + 0.5
    r = np.hypot(dx, dy)
    luar = n * porsi / 2
    dalam = luar * (100.0 / 107.3)
    cincin = r > luar * 0.88  # bunga teratai terjauh ~0,75
    t = np.clip((r - dalam) / (luar - dalam), 0, 1)
    rs = 100.5 + t * 3.0
    sud = np.arctan2(dy, dx)
    peta_x = (255.5 + rs * np.cos(sud)).astype(np.float32)
    peta_y = (254.5 + rs * np.sin(sud)).astype(np.float32)
    polar = cv2.remap(LAMA, peta_x, peta_y, cv2.INTER_LINEAR)
    kanvas = np.where(cincin[..., None], polar, kanvas)
    # latar LATAR, bukan nol: splash Android menggambar ikon ini di atas
    # background_color manifest, jadi keduanya harus sama supaya kotaknya menyatu.
    a = masker[..., None] / 255.0
    rgb = kanvas * a + np.array(LATAR, np.float32) * (1 - a)
    kecil = cv2.resize(rgb.astype(np.float32), (ukuran, ukuran), interpolation=cv2.INTER_AREA)
    return np.clip(np.round(kecil), 0, 255).astype(np.uint8)


for uk in (192, 512):
    # 2026-09-25: dikecilkan lagi (80->72, 68->58), dilaporkan "ikon loading masuk
    # padma logo pinggir2nya masih kayak kepotong ... kecilin aja logonya" --
    # splash Android memotong ke lingkaran tengah, di luar kendali manifest.
    cv2.imwrite(os.path.join(OUT, 'icon-%d.png' % uk), ikon(uk, 0.72))
    # 0.58 -> 0.34 (2026-09-25, "ukuran logo padma diperkecil se ukuran ig", contoh
    # splash Instagram): cincin di splash Android ~58% dari sebelumnya, kira-kira
    # sama dengan logo laser sesudahnya. Harganya: ikon SAMA dipakai launcher, jadi
    # logo di layar utama ikut kecil (pemilik memilihnya).
    # 0.34 -> 0.46 (sama hari, "logo shortcut aplikasinya bisa dibuat gede ga sih?"):
    # ikon launcher = ikon splash Android 12+, jadi dipilih tengah-tengah (pemilik).
    cv2.imwrite(os.path.join(OUT, 'icon-maskable-%d.png' % uk), ikon(uk, 0.46))
print('ok')
