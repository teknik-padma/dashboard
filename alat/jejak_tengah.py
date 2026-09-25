"""Garis tengah logo untuk laser "membuka logo" (opsi A, 2026-09-25 malam, pemilik:
"A go go go"). Dari path isi hasil jiplak_logo: raster -> penipisan Zhang-Suen ->
graf goresan (simpang = zona di sekitar piksel bercabang >= 3) -> goresan terurut
untuk satu titik laser. Tiap goresan membawa LEBAR = tebal pita terlebar yang
dilaluinya (distance transform), jadi goresan ber-mask selebar itu membuka isi
logo yang ASLI di belakang titik laser -- tajam sejak bingkai pertama, dan bingkai
terakhirnya logo itu sendiri (dulu: garis tepi dua sisi per pita = kabur di awal).

Pakai: jejak_tengah(L, mulai=(x, y), cincin_akhir=False) -> {'jejak': [{'d','w'}],
'tutup': porsi isi yang terjangkau jejak, 'panjang': total panjang (satuan)}."""
import re
import numpy as np, cv2

D8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


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


def masker(L, S, pad=4):
    k = L['kotak']; x0, y0 = k[0] - pad, k[1] - pad
    w = int(np.ceil((k[2] - k[0] + 2 * pad) * S)); h = int(np.ceil((k[3] - k[1] + 2 * pad) * S))
    m = np.zeros((h, w), np.uint8)
    for poli in subpath(L['isi']):  # evenodd = XOR tiap subpath
        t = np.zeros_like(m)
        pts = np.array([[(x - x0) * S, (y - y0) * S] for x, y in poli])
        cv2.fillPoly(t, [np.round(pts * 16).astype(np.int32)], 255, lineType=cv2.LINE_8, shift=4)
        m ^= t
    return m > 0, x0, y0


def tipiskan(b):
    """Penipisan Zhang-Suen (numpy): bentuk -> kerangka selebar 1 piksel."""
    I = b.astype(np.uint8)
    berubah = True
    while berubah:
        berubah = False
        for langkah in (0, 1):
            P = np.pad(I, 1)
            p2, p3, p4 = P[:-2, 1:-1], P[:-2, 2:], P[1:-1, 2:]
            p5, p6, p7 = P[2:, 2:], P[2:, 1:-1], P[2:, :-2]
            p8, p9 = P[1:-1, :-2], P[:-2, :-2]
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            urut = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            A = sum(((urut[k] == 0) & (urut[k + 1] == 1)).astype(np.uint8) for k in range(8))
            if langkah == 0:
                c1 = (p2 * p4 * p6) == 0; c2 = (p4 * p6 * p8) == 0
            else:
                c1 = (p2 * p4 * p8) == 0; c2 = (p2 * p6 * p8) == 0
            m = (I == 1) & (B >= 2) & (B <= 6) & (A == 1) & c1 & c2
            if m.any():
                I[m] = 0; berubah = True
    return I.astype(bool)


def urutkan(pix):
    """Piksel satu komponen tanpa simpang -> jalur berurut (+ apakah siklus)."""
    tetangga = lambda p: [(p[0] + dy, p[1] + dx) for dy, dx in D8 if (p[0] + dy, p[1] + dx) in pix]
    ujung = [p for p in pix if len(tetangga(p)) == 1]
    siklus = not ujung
    awal = ujung[0] if ujung else min(pix)
    jalur, lihat, cur = [awal], {awal}, awal
    while True:
        calon = [q for q in tetangga(cur) if q not in lihat]
        if not calon: break
        calon.sort(key=lambda q: abs(q[0] - cur[0]) + abs(q[1] - cur[1]))  # tegak lurus dulu
        cur = calon[0]; jalur.append(cur); lihat.add(cur)
    return jalur, siklus


def haluskan(pts, siklus, jendela=5):
    if len(pts) < jendela + 2: return pts
    h = jendela // 2
    if siklus:
        ext = np.vstack([pts[-h:], pts, pts[:h]])
        return np.array([ext[i:i + jendela].mean(0) for i in range(len(pts))])
    out = pts.copy()
    for i in range(h, len(pts) - h):
        out[i] = pts[i - h:i + h + 1].mean(0)
    return out


def jejak_tengah(L, mulai=(0.0, -1e9), cincin_akhir=False, S=8, sisa=0.6):
    M, x0, y0 = masker(L, S)
    dt = cv2.distanceTransform(M.astype(np.uint8), cv2.DIST_L2, 5) / S          # satuan viewBox
    sk = tipiskan(M)
    K = np.ones((3, 3), np.float32)
    skU = sk.astype(np.uint8)
    deg = (cv2.filter2D(skU.astype(np.float32), -1, K, borderType=cv2.BORDER_CONSTANT) - skU).astype(np.int32)
    simpang = sk & (deg >= 3)
    zona = cv2.dilate(simpang.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    nz, labz = cv2.connectedComponents(zona.astype(np.uint8), connectivity=8)
    pusat = {}
    for z in range(1, nz):
        ys, xs = np.where((labz == z) & simpang)
        if not len(ys): ys, xs = np.where(labz == z)
        pusat[z] = (xs.mean(), ys.mean(), float(dt[int(round(ys.mean())), int(round(xs.mean()))]))
    tepi = sk & ~zona
    n, lab = cv2.connectedComponents(tepi.astype(np.uint8), connectivity=8)
    ke_satuan = lambda x, y: ((x + 0.5) / S + x0, (y + 0.5) / S + y0)
    # 1) ruas mentah: jalur piksel + zona simpang di kedua ujungnya (0 = ujung bebas)
    ruas = []
    for c in range(1, n):
        ys, xs = np.where(lab == c)
        jalur, siklus = urutkan(set(zip(ys.tolist(), xs.tolist())))
        pts = [(float(x), float(y)) for y, x in jalur]
        lebar = [float(dt[y, x]) for y, x in jalur]
        za = zb = 0
        if not siklus:
            ends = []
            for idx in (0, -1):
                y, x = jalur[idx]
                zs = {int(labz[y + dy, x + dx]) for dy, dx in D8
                      if 0 <= y + dy < labz.shape[0] and 0 <= x + dx < labz.shape[1] and labz[y + dy, x + dx] > 0}
                ends.append(min(zs) if zs else 0)
            za, zb = ends
            # ujung yang menyentuh simpang diperpanjang ke pusat simpangnya: goresan bertemu, tanpa celah
            if za: px, py, r = pusat[za]; pts.insert(0, (px, py)); lebar.append(r)
            if zb: px, py, r = pusat[zb]; pts.append((px, py)); lebar.append(r)
        ruas.append({'pts': pts, 'lebar': lebar, 'za': za, 'zb': zb, 'siklus': siklus})
    panjang_px = lambda e: float(np.sum(np.hypot(*np.diff(np.array(e['pts']), axis=0).T))) if len(e['pts']) > 1 else 0.0
    # 2) bersihkan berulang: buang taji, lalu sambung ruas yang bertemu di simpang berderajat 2
    #    (penipisan Zhang-Suen meninggalkan "simpang palsu" di tiap anak tangga diagonal)
    def derajat():
        dg = {}
        for e in ruas:
            if e['siklus']: continue
            for z in (e['za'], e['zb']):
                if z: dg[z] = dg.get(z, 0) + 1
        return dg
    berubah = True
    while berubah:
        berubah = False
        dg = derajat()
        tetap = []
        for e in ruas:
            L_su = panjang_px(e) / S
            if not e['siklus']:
                bebas = [e['za'], e['zb']].count(0)
                z = e['za'] or e['zb']
                rz = pusat[z][2] if z else 0.0
                if bebas == 1 and dg.get(z, 0) >= 3 and L_su < max(1.5, 1.2 * rz):
                    berubah = True; continue            # taji
                if e['za'] and e['za'] == e['zb'] and L_su < max(2.0, 2.5 * rz):
                    berubah = True; continue            # simpul kecil di dalam satu simpang
                if bebas == 2 and L_su < 0.5:
                    berubah = True; continue            # noda
            tetap.append(e)
        ruas = tetap
        dg = derajat()
        for z, k in dg.items():
            if k != 2: continue
            dua = [e for e in ruas if not e['siklus'] and z in (e['za'], e['zb'])]
            if len(dua) == 1:                            # satu ruas masuk-keluar di z -> siklus
                e = dua[0]; e['siklus'] = True; e['za'] = e['zb'] = 0; e['pts'] = e['pts'][:-1]
                berubah = True; break
            if len(dua) != 2: continue
            e1, e2 = dua
            if e1['zb'] != z: e1 = dict(e1, pts=e1['pts'][::-1], lebar=e1['lebar'][::-1], za=e1['zb'], zb=e1['za'])
            if e2['za'] != z: e2 = dict(e2, pts=e2['pts'][::-1], lebar=e2['lebar'][::-1], za=e2['zb'], zb=e2['za'])
            baru_e = {'pts': e1['pts'] + e2['pts'][1:], 'lebar': e1['lebar'] + e2['lebar'],
                      'za': e1['za'], 'zb': e2['zb'], 'siklus': False}
            ruas = [e for e in ruas if e is not dua[0] and e is not dua[1]] + [baru_e]
            berubah = True; break
    goresan = []
    for e in ruas:
        P = np.array([ke_satuan(x, y) for x, y in e['pts']])
        P = haluskan(P, e['siklus'])
        P = cv2.approxPolyDP(P.astype(np.float32).reshape(-1, 1, 2), 0.12, e['siklus']).reshape(-1, 2)
        if len(P) < 2: continue
        goresan.append({'P': P, 'siklus': e['siklus'], 'w': 2 * max(e['lebar']) + sisa})
    # urutan satu titik laser: terdekat dulu; siklus diputar ke titik terdekat
    cincin = None
    if cincin_akhir:
        sik = [g for g in goresan if g['siklus']]
        if sik:
            cincin = max(sik, key=lambda g: np.ptp(g['P'][:, 0]) * np.ptp(g['P'][:, 1]))
            goresan = [g for g in goresan if g is not cincin]
    urut, cur = [], np.array(mulai, float)
    def pasang(g, cur):
        P = g['P']
        if g['siklus']:
            k = int(np.argmin(np.hypot(*(P - cur).T))); P = np.vstack([P[k:], P[:k]])
            return P, float(np.hypot(*(P[0] - cur)))
        da, db = np.hypot(*(P[0] - cur)), np.hypot(*(P[-1] - cur))
        return (P, float(da)) if da <= db else (P[::-1], float(db))
    sisa_g = list(goresan)
    while sisa_g:
        terbaik = min(sisa_g, key=lambda g: pasang(g, cur)[1])
        P, _ = pasang(terbaik, cur)
        urut.append(dict(terbaik, P=P)); sisa_g = [g for g in sisa_g if g is not terbaik]
        cur = P[-1] if not terbaik['siklus'] else P[0]
    if cincin is not None:
        P, _ = pasang(cincin, cur); urut.append(dict(cincin, P=P))
    # jangkauan: goresan ber-lebar (ujung bulat) iris isi
    tutup = np.zeros(M.shape, np.uint8)
    for g in urut:
        q = np.round(np.array([((x - x0) * S - 0.5, (y - y0) * S - 0.5) for x, y in g['P']])).astype(np.int32)
        t = max(1, int(round(g['w'] * S)))
        cv2.polylines(tutup, [q.reshape(-1, 1, 2)], g['siklus'], 1, t, cv2.LINE_8)
        for x, y in q[[0, -1]]: cv2.circle(tutup, (int(x), int(y)), t // 2, 1, -1)
    porsi = float((tutup.astype(bool) & M).sum() / max(1, M.sum()))
    jejak, total = [], 0.0
    for g in urut:
        P = g['P']
        d = 'M' + 'L'.join('%.2f %.2f' % (x, y) for x, y in P) + ('Z' if g['siklus'] else '')
        seg = np.hypot(*np.diff(np.vstack([P, P[:1]]) if g['siklus'] else P, axis=0).T)
        total += float(seg.sum())
        # Pita lebar (batang F FirstJet, segitiga) berujung SIKU: sapuannya lurus dan
        # sudut batangnya ikut terbuka; pita tipis (Padma, huruf) tetap bulat.
        jejak.append({'d': d, 'w': round(g['w'], 2), 'siku': g['w'] > 8})
    return {'jejak': jejak, 'tutup': porsi, 'panjang': total}
