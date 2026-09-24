"""Menyusun alat/logo-customer.json dari keluaran cekLogoPola() (alat/logopola.json)
dan peta logo di Index.html dashboard (2026-09-25).
Pakai: python susun-logo-customer.py "<folder DASHBOARD PADMA>"
Urutan = jumlah SPK terbanyak ("logonya diprioritasin dari spk terbanyak").
Logo tiap customer dicari dengan URUTAN YANG SAMA dengan logoTag() di
Index.html, supaya layar muat memakai logo yang sama dengan dashboard:
  1. unggahan Data Master (sheet LogoCustomer, kunci tanpa awalan PT/CV/UD)
  2. EXACT_LOGO_OVERRIDES[kunci]
  3. CUSTOMER_LOGO_OVERRIDES: merek pertama yang termuat di kunci
  4. favicon Google 128 px dari EXACT_CUSTOMER_DOMAINS / BRAND_DOMAINS
Logo Padma sendiri (data:) dan URL yang sudah dipakai customer lebih laris
dilewati -- satu logo, satu tempat di daftar."""
import json, os, re, sys

DASBOR = sys.argv[1]
ALAT = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(DASBOR, 'Index.html'), encoding='utf-8', errors='replace').read()


def peta(nama):
    """Objek literal JS `const NAMA = { 'k': 'v', ... };` -> dict (urutan dijaga)."""
    i = src.index('const %s = {' % nama)
    j = src.index('\n};', i)
    hasil = {}
    for m in re.finditer(r"^\s*'([^']+)'\s*:\s*'([^']*)'", src[i:j], re.M):
        hasil.setdefault(m.group(1), m.group(2).replace('\\/', '/'))
    assert hasil, nama
    return hasil


EXACT_LOGO = peta('EXACT_LOGO_OVERRIDES')
CUST_LOGO = peta('CUSTOMER_LOGO_OVERRIDES')
EXACT_DOM = peta('EXACT_CUSTOMER_DOMAINS')
BRAND_DOM = peta('BRAND_DOMAINS')


def kunci(nama):
    return re.sub(r'^(pt\.?|cv\.?|ud\.?)\s+', '', nama.lower(), flags=re.I).strip()


data = json.load(open(os.path.join(ALAT, 'logopola.json'), encoding='utf-8'))
UNGGAH = {kunci(k): v for k, v in data['logo'].items()}


def logo_untuk(nama):
    k = kunci(nama)
    if k in UNGGAH:
        return 'https://lh3.googleusercontent.com/d/' + UNGGAH[k], 'unggahan'
    if k in EXACT_LOGO:
        return EXACT_LOGO[k], 'exact'
    for b, url in CUST_LOGO.items():
        if b in k:
            return url, 'override'
    dom = EXACT_DOM.get(k) or next((d for b, d in BRAND_DOM.items() if b in k), None)
    if dom:
        return 'https://www.google.com/s2/favicons?domain=%s&sz=128' % dom, 'favicon'
    return None, None


hasil, dipakai, tanpa = [], set(), []
for nama, jumlah in data['spk']:
    url, asal = logo_untuk(nama)
    if not url:
        tanpa.append(nama)
        continue
    if url.startswith('data:') or url in dipakai:
        continue
    dipakai.add(url)
    hasil.append({'nama': nama, 'spk': jumlah, 'url': url, 'asal': asal})
json.dump(hasil, open(os.path.join(ALAT, 'logo-customer.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(hasil), 'logo;', 'tanpa logo:', len(tanpa))
for x in hasil:
    print('  %4d  %-9s %s' % (x['spk'], x['asal'], x['nama']))
