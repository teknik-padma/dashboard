"""Huruf garis tunggal untuk tulisan PADMA GROUP yang diukir laser.
Tiap huruf: lebar + daftar goresan; goresan = daftar perintah ('M'|'L'|'C', titik...).
Tinggi huruf 10 satuan (0 = atas, 10 = bawah), lalu diskala & digeser."""

HURUF = {
    'P': (5.8, [[('M', 0, 10), ('L', 0, 0), ('L', 3.4, 0), ('C', 6.4, 0, 6.4, 5, 3.4, 5), ('L', 0, 5)]]),
    'A': (6.6, [[('M', 0, 10), ('L', 3.3, 0), ('L', 6.6, 10)],
                [('M', 1.35, 6.3), ('L', 5.25, 6.3)]]),
    'D': (6.4, [[('M', 0, 10), ('L', 0, 0), ('L', 2.6, 0), ('C', 8.2, 0, 8.2, 10, 2.6, 10), ('L', 0, 10)]]),
    'M': (8.0, [[('M', 0, 10), ('L', 0, 0), ('L', 4, 7), ('L', 8, 0), ('L', 8, 10)]]),
    'G': (7.2, [[('M', 6.9, 2.1), ('C', 6.1, 0.7, 5.0, 0, 3.6, 0), ('C', 1.4, 0, 0, 2.2, 0, 5),
                 ('C', 0, 7.8, 1.4, 10, 3.6, 10), ('C', 5.8, 10, 7.2, 8.4, 7.2, 6.1),
                 ('L', 7.2, 5.3), ('L', 4.2, 5.3)]]),
    'R': (6.4, [[('M', 0, 10), ('L', 0, 0), ('L', 3.4, 0), ('C', 6.4, 0, 6.4, 5, 3.4, 5), ('L', 0, 5)],
                [('M', 3.2, 5), ('L', 6.4, 10)]]),
    'O': (7.4, [[('M', 3.7, 0), ('C', 1.4, 0, 0, 2.2, 0, 5), ('C', 0, 7.8, 1.4, 10, 3.7, 10),
                 ('C', 6.0, 10, 7.4, 7.8, 7.4, 5), ('C', 7.4, 2.2, 6.0, 0, 3.7, 0)]]),
    'U': (6.6, [[('M', 0, 0), ('L', 0, 6.5), ('C', 0, 8.8, 1.4, 10, 3.3, 10),
                 ('C', 5.2, 10, 6.6, 8.8, 6.6, 6.5), ('L', 6.6, 0)]]),
}
JARAK = 3.0      # antar huruf (satuan huruf)
SPASI = 5.0      # lebar spasi


def tulisan(teks, skala, x_tengah, y_atas):
    """-> (daftar string path 'd', lebar total dalam satuan SVG)"""
    lebar = 0
    for i, ch in enumerate(teks):
        lebar += SPASI if ch == ' ' else HURUF[ch][0]
        if i < len(teks) - 1 and ch != ' ' and teks[i + 1] != ' ':
            lebar += JARAK
    total = lebar * skala
    x = x_tengah - total / 2
    paths = []
    for i, ch in enumerate(teks):
        if ch == ' ':
            x += SPASI * skala
            continue
        w, goresan = HURUF[ch]
        for g in goresan:
            bagian = []
            for cmd in g:
                k, angka = cmd[0], cmd[1:]
                titik = []
                for j in range(0, len(angka), 2):
                    titik.append('%.2f %.2f' % (x + angka[j] * skala, y_atas + angka[j + 1] * skala))
                bagian.append(k + ' '.join(titik) if k == 'M' else k + ' ' + ' '.join(titik))
            paths.append(''.join(p if p.startswith('M') else ' ' + p for p in bagian))
        x += w * skala
        if i < len(teks) - 1 and teks[i + 1] != ' ':
            x += JARAK * skala
    return paths, total


if __name__ == '__main__':
    p, w = tulisan('PADMA GROUP', 1.6, 0, 78)
    print(w)
    for d in p:
        print(d)
