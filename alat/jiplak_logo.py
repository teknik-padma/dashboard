"""Jiplak logo raster -> kontur SVG untuk layar muat laser (2026-09-24).
Gambar diperbesar 8x (kubik) + dihaluskan, diambang, konturnya diambil
(OpenCV, luar + lubang), disederhanakan RDP lalu dijadikan Bezier
Catmull-Rom dengan sudut tajam dipertahankan. Hasil diukur ulang
terhadap gambar asli (IoU) supaya "mirip" punya angka, bukan kira-kira.
Butuh: pip install opencv-python-headless numpy"""
import re
import cv2
import numpy as np

K = 8  # pembesaran sebelum mengambil kontur


def topeng(f, mode):
    im = cv2.imread(f)[:, :, :3]
    if mode == 'terang':      # padma: perak di atas hitam
        g, ambang = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32), 80
    else:                     # firstjet: putih di atas biru (kanal terendah tinggi = putih)
        g, ambang = im.min(axis=2).astype(np.float32), 128
    big = cv2.resize(g, None, fx=K, fy=K, interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), K * 0.45)
    return (big > ambang).astype(np.uint8) * 255


def _rdp(p, eps):
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]
    ab, v = b - a, p - a
    n = np.hypot(*ab)
    d = np.abs(ab[0] * v[:, 1] - ab[1] * v[:, 0]) / n if n else np.hypot(*v.T)
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([_rdp(p[:i + 1], eps)[:-1], _rdp(p[i:], eps)])
    return np.array([a, b])


def _rdp_tutup(p, eps):
    # dibelah di titik terjauh dari p[0], supaya p[0] tetap titik awal goresan
    j = int(np.argmax(np.hypot(*(p - p[0]).T)))
    a = _rdp(p[:j + 1], eps)
    b = _rdp(np.vstack([p[j:], p[:1]]), eps)
    return np.vstack([a[:-1], b[:-1]])


def _tajam(p, i):
    u, v = p[i] - p[i - 1], p[(i + 1) % len(p)] - p[i]
    return np.dot(u, v) / (np.hypot(*u) * np.hypot(*v) + 1e-9) < np.cos(np.radians(50))


def _lingkaran(p):
    """Lingkaran kuadrat terkecil -> (cx, cy, r, simpangan maks / r)."""
    A = np.c_[2 * p, np.ones(len(p))]
    b = (p ** 2).sum(1)
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    r = np.sqrt(c + cx * cx + cy * cy)
    return cx, cy, r, float(np.abs(np.hypot(p[:, 0] - cx, p[:, 1] - cy) - r).max() / r)


def _bezier_lingkaran(cx, cy, r, mulai, fmt):
    """Lingkaran 8 ruas kubik (galat < 0,0004 r), mulai di sudut `mulai`."""
    n = 8
    k = 4 / 3 * np.tan(np.pi / (2 * n)) * r
    pt = lambda t: np.array([cx + r * np.cos(t), cy + r * np.sin(t)])
    tg = lambda t: np.array([-np.sin(t), np.cos(t)])
    s = 'M' + fmt(pt(mulai))
    for i in range(n):
        t0, t1 = mulai + 2 * np.pi * i / n, mulai + 2 * np.pi * (i + 1) / n
        s += 'C%s %s %s' % (fmt(pt(t0) + k * tg(t0)), fmt(pt(t1) - k * tg(t1)), fmt(pt(t1)))
    return s + 'Z'


def _batasi(t, ruas):
    """Tangen paling panjang 1/3 ruasnya. Tanpa ini sudut yang tidak terdeteksi
    tajam (belokan terbagi dua oleh penghalusan) membuat kurva kebablasan jadi
    taji tipis -- terlihat sebagai garis di ujung bilah F FirstJet."""
    m, L = np.hypot(*t), np.hypot(*ruas) / 3
    return t * (L / m) if m > L else t


def _bezier(p, fmt):
    n = len(p)
    tj = [_tajam(p, i) for i in range(n)]
    s = 'M' + fmt(p[0])
    for i in range(n):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % n], p[(i + 2) % n]
        if tj[i] and tj[(i + 1) % n]:
            s += 'L' + fmt(p2)
            continue
        t1 = np.zeros(2) if tj[i] else _batasi((p2 - p0) / 6, p2 - p1)
        t2 = np.zeros(2) if tj[(i + 1) % n] else _batasi((p3 - p1) / 6, p2 - p1)
        s += 'C%s %s %s' % (fmt(p1 + t1), fmt(p2 - t2), fmt(p2))
    return s + 'Z'


def jiplak(f, mode, tinggi, x_tengah, urut, eps_px=0.35, baris=44):
    """-> dict: gores (list 'd', urutan laser), isi ('d' evenodd), baris
    (arsiran: [y, [[x0,x1],...]] per baris), kotak, iou."""
    m = topeng(f, mode)
    ys, xs = np.nonzero(m)
    cx, cy = (xs.min() + xs.max()) / 2 / K, (ys.min() + ys.max()) / 2 / K
    sk = tinggi / ((ys.max() - ys.min()) / K)
    ke = lambda q: ((q[0] / K - cx) * sk + x_tengah, (q[1] / K - cy) * sk)
    fmt = lambda q: '%.2f %.2f' % ke(q)

    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    kontur = []
    for i, c in enumerate(cs):
        if cv2.contourArea(c) < 4 * K * K:
            continue
        p = c[:, 0, :].astype(np.float64)
        w = 5
        ker = np.ones(w) / w
        p = np.stack([np.convolve(np.r_[p[-w:, j], p[:, j], p[:w, j]], ker, 'same')[w:-w] for j in (0, 1)], 1)
        kontur.append({'p': p, 'luas': cv2.contourArea(c), 'induk': int(hier[0][i][3]), 'id': i})

    # Urutan goresan. 'luas': bentuk luar dari yang terkecil, tiap bentuk
    # langsung disusul lubangnya (padma: teratai dulu, cincin terakhir).
    # 'dekat': mulai dari titik paling kiri-atas, lalu kontur terdekat berikutnya
    # (firstjet: tulisan kiri ke kanan, baru huruf F besar).
    if urut == 'luas':
        luar = sorted([k for k in kontur if k['induk'] < 0], key=lambda k: k['luas'])
        antre = []
        for k in luar:
            antre.append(k)
            antre += [h for h in kontur if h['induk'] == k['id']]
    else:
        sisa = list(kontur)
        ujung = np.array([xs.min(), ys.min()], float)
        antre = []
        while sisa:
            ix = min(range(len(sisa)), key=lambda n: np.hypot(*(sisa[n]['p'] - ujung).T).min())
            k = sisa.pop(ix)
            antre.append(k)
            ujung = k['p'][int(np.argmin(np.hypot(*(k['p'] - ujung).T)))]
    gores, akhir = [], None
    for k in antre:
        p = k['p']
        if akhir is not None:  # titik awal = titik terdekat dari ujung goresan sebelumnya
            j = int(np.argmin(np.hypot(*(p - akhir).T)))
            p = np.vstack([p[j:], p[:j]])
        # Cincin Padma: tepi jiplakan JPEG bergelombang (~1 px) -> lingkaran
        # sejati kalau simpangannya di bawah 3 % jari-jari.
        cx_, cy_, r_, galat = _lingkaran(p)
        if len(p) > 200 and galat < 0.03:
            gores.append(_bezier_lingkaran(cx_, cy_, r_, np.arctan2(p[0, 1] - cy_, p[0, 0] - cx_), fmt))
            akhir = p[0]
            continue
        q = _rdp_tutup(p, eps_px * K)
        gores.append(_bezier(q, fmt))
        akhir = q[0]

    # Arsiran: per baris, rentang x yang terisi (laser menyapu bolak-balik).
    y0, y1 = ys.min(), ys.max()
    brs = []
    for r in np.linspace(y0 + K, y1 - K, baris):
        row = m[int(r)] > 0
        d = np.diff(np.r_[0, row.astype(int), 0])
        a, b = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        rent = [[round(ke((x0, r))[0], 1), round(ke((x1, r))[0], 1)] for x0, x1 in zip(a, b) if x1 - x0 > K * 0.6]
        brs.append([round(ke((0, r))[1], 1), rent])

    kotak = [round(v, 1) for v in (*ke((xs.min(), ys.min())), *ke((xs.max(), ys.max())))]
    return {'gores': gores, 'isi': ''.join(gores), 'baris': brs, 'kotak': kotak,
            'iou': _iou(m, gores, lambda x, y: ((x - x_tengah) / sk + cx, y / sk + cy))}


def _titik(d):
    tok = re.findall(r'[MCLZ]|-?\d+\.?\d*', d)
    i, cur, out = 0, None, []
    while i < len(tok):
        t = tok[i]
        if t in 'ML':
            cur = np.array([float(tok[i + 1]), float(tok[i + 2])])
            out.append(cur)
            i += 3
        elif t == 'C':
            c = [np.array([float(tok[i + 1 + 2 * k]), float(tok[i + 2 + 2 * k])]) for k in range(3)]
            for s in np.linspace(0, 1, 12)[1:]:
                out.append((1 - s) ** 3 * cur + 3 * (1 - s) ** 2 * s * c[0] + 3 * (1 - s) * s * s * c[1] + s ** 3 * c[2])
            cur = c[2]
            i += 7
        else:
            i += 1
    return np.array(out)


def _iou(m, gores, balik):
    R = np.zeros(m.shape, np.uint8)
    polys = []
    for d in gores:
        t = _titik(d)
        x, y = balik(t[:, 0], t[:, 1])
        polys.append(np.round(np.stack([x, y], 1) * K * 16).astype(np.int32))
    cv2.fillPoly(R, polys, 1, shift=4)
    a, b = R > 0, m > 0
    return round(float((a & b).sum() / (a | b).sum()), 4)
