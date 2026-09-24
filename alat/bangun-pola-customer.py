"""Siluet logo customer untuk pola latar layar muat (2026-09-25).
Pakai: python bangun-pola-customer.py
Membaca alat/logo-customer.json (nama + ID Drive, disalin dari CUSTOMER_LOGO_OVERRIDES
di Index.html dashboard), mengunduh tiap logo dari lh3.googleusercontent.com
(berkas Drive "siapa pun yang punya link"), lalu menulis alat/pola-customer/<id>.png:
putih polos, transparansi = seberapa jauh piksel dari warna latar logonya.
Diminta pemilik: "diganti logo2 customer saja yang dibackground ... idle aja
cuma ada cahaya jalan2", "logonya ambil dari customer ya" -- izin unduh: "boleh"."""
import io, json, os, urllib.request
import numpy as np
from PIL import Image

ALAT = os.path.dirname(os.path.abspath(__file__))
KELUAR = os.path.join(ALAT, 'pola-customer')
TINGGI, LEBAR_MAKS = 40, 104   # px di layar; ubin memakai 2x supaya tajam di HP
SKALA = 2
os.makedirs(KELUAR, exist_ok=True)


def latar(a):
    """Warna latar = median piksel pinggir (logo diunggah di atas kotak polos)."""
    tepi = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    return np.median(tepi[:, :3], axis=0), np.median(tepi[:, 3])


def siluet(gambar):
    a = np.asarray(gambar.convert('RGBA')).astype(np.float32)
    warna, alfa_tepi = latar(a)
    if alfa_tepi < 128:
        # Latar transparan = anggap putih: lencana berwarna (Savoria, So Good,
        # Mega Global) dengan alfa saja jadi gumpalan putih. Logo yang memang
        # putih polos (untuk latar gelap) hampir tanpa tinta -> alfa saja.
        L = a[:, :, :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32) / 255.0
        al = a[:, :, 3] / 255.0
        tinta = np.clip((1.0 - L - 0.04) / 0.62, 0, 1) ** 0.8 * al
        if al.sum() and tinta.sum() / al.sum() < 0.15:
            tinta = al
    else:
        # SELISIH KECERAHAN, bukan jarak warna: lencana berwarna penuh
        # (Savoria, Cap Lang, So Good) dengan jarak warna jadi gumpalan putih
        # rata; dengan kecerahan, tulisan terang di dalamnya tetap berlubang.
        # Latar gelap (jarang) dibalik arahnya.
        L = a[:, :, :3] @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32) / 255.0
        Lb = float(warna @ np.array([0.2126, 0.7152, 0.0722])) / 255.0
        beda = (Lb - L) if Lb >= 0.5 else (L - Lb)
        tinta = np.clip((beda - 0.04) / 0.62, 0, 1) ** 0.8 * (a[:, :, 3] / 255.0)
    ys, xs = np.where(tinta > 0.08)
    if not len(xs):
        return None
    tinta = tinta[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = tinta.shape
    k = min(TINGGI * SKALA / h, LEBAR_MAKS * SKALA / w)
    kanal = Image.fromarray((tinta * 255).astype(np.uint8), 'L').resize(
        (max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    # Mode LA (abu + alfa, abunya 255 rata): sepertiga ukuran RGBA.
    putih = Image.new('LA', kanal.size, (255, 0))
    putih.putalpha(kanal)
    return putih


daftar = json.load(open(os.path.join(ALAT, 'logo-customer.json'), encoding='utf-8'))
# Cap Lang (Eagle Indo Pharma): kotak merah polos tanpa isi terang -> siluetnya
# persegi putih; di Index.html pun masih "asumsi, TOLONG DIKONFIRMASI".
LEWATI = {'eagle indo pharma'}
daftar = [d for d in daftar if d['nama'] not in LEWATI]
for f in os.listdir(KELUAR):
    if f.endswith('.png'):
        os.remove(os.path.join(KELUAR, f))
hasil = []
for d in daftar:
    url = 'https://lh3.googleusercontent.com/d/%s=w400' % d['id']
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
        s = siluet(Image.open(io.BytesIO(data)))
    except Exception as e:
        print('GAGAL', d['nama'], e)
        continue
    if s is None:
        print('KOSONG', d['nama'])
        continue
    s.save(os.path.join(KELUAR, d['id'] + '.png'), optimize=True)
    hasil.append({'nama': d['nama'], 'id': d['id'], 'w': s.size[0] // SKALA, 'h': s.size[1] // SKALA})
    print('ok', d['nama'], s.size)
json.dump(hasil, open(os.path.join(KELUAR, 'daftar.json'), 'w', encoding='utf-8'), indent=1)
print(len(hasil), 'dari', len(daftar))
