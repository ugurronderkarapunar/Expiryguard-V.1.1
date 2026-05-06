import json
import os
import uuid
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from config import *

def dosya_oku(dosya_adi: str, varsayilan=None):
    if os.path.exists(dosya_adi):
        try:
            with open(dosya_adi, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return varsayilan if varsayilan is not None else []

def dosya_yaz(dosya_adi: str, veri) -> bool:
    try:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def veri_gecis_kontrol() -> None:
    degisti = False
    for u in st.session_state.stok:
        for k, v in [("kategori", "Diğer"), ("min_miktar", 0), ("barkod", ""),
                     ("son_kullanma_tarihi", ""), ("alis_fiyat", 0), ("satis_fiyat", 0),
                     ("tedarikci", ""), ("raf_no", ""), ("kdv_oran", 8), ("tahmini_gunluk_satis", 1.0)]:
            if k not in u:
                u[k] = v
                degisti = True
    for s in st.session_state.fire:
        if "adet" in s and "miktar" not in s:
            s["miktar"] = s.pop("adet")
            degisti = True
        for k, v in [("miktar", 0), ("birim", "adet"), ("tedarikci", ""), ("durum", "Bekliyor"),
                     ("eklenme_tarihi", "")]:
            if k not in s:
                s[k] = v
                degisti = True
    if degisti:
        veriyi_kaydet()

def hareket_ekle(kul: str, islem: str, ad: str, detay: str = "") -> None:
    h = {"tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kullanici": kul, "islem": islem,
         "urun_adi": ad, "detay": detay}
    liste = dosya_oku(HAREKET_DOSYASI, [])
    liste.append(h)
    if len(liste) > 1000:
        liste = liste[-1000:]
    dosya_yaz(HAREKET_DOSYASI, liste)

def satis_kaydet(ad: str, birim: str, miktar: float, fiyat: float, tutar: float, kul: str,
                 alis_fiyat: float = 0, odeme_tipi: str = "Nakit") -> None:
    s = {"id": str(uuid.uuid4())[:8], "tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
         "kullanici": kul, "urun_adi": ad, "birim": birim, "miktar": miktar,
         "birim_fiyat": fiyat, "toplam_tutar": tutar,
         "alis_fiyat": alis_fiyat, "maliyet": round(miktar * alis_fiyat, 2),
         "odeme_tipi": odeme_tipi}
    liste = dosya_oku(SATIS_DOSYASI, [])
    liste.append(s)
    dosya_yaz(SATIS_DOSYASI, liste)

def gunluk_ciro(tarih=None) -> float:
    if tarih is None:
        tarih = datetime.now().strftime("%Y-%m-%d")
    liste = dosya_oku(SATIS_DOSYASI, [])
    return sum(s["toplam_tutar"] for s in liste if s["tarih"].startswith(tarih))

def haftalik_ciro(baslangic_tarihi=None) -> float:
    if baslangic_tarihi is None:
        baslangic_tarihi = datetime.now().date() - timedelta(days=datetime.now().weekday())
    bitis = baslangic_tarihi + timedelta(days=6)
    liste = dosya_oku(SATIS_DOSYASI, [])
    toplam = 0
    for s in liste:
        try:
            tarih = datetime.strptime(s["tarih"], "%Y-%m-%d %H:%M:%S").date()
            if baslangic_tarihi <= tarih <= bitis:
                toplam += s["toplam_tutar"]
        except:
            pass
    return toplam

def aylik_ciro(yil=None, ay=None) -> float:
    if yil is None:
        yil = datetime.now().year
    if ay is None:
        ay = datetime.now().month
    liste = dosya_oku(SATIS_DOSYASI, [])
    toplam = 0
    for s in liste:
        try:
            tarih = datetime.strptime(s["tarih"], "%Y-%m-%d %H:%M:%S")
            if tarih.year == yil and tarih.month == ay:
                toplam += s["toplam_tutar"]
        except:
            pass
    return toplam

def gunluk_kar() -> float:
    liste = dosya_oku(SATIS_DOSYASI, [])
    bugun = datetime.now().strftime("%Y-%m-%d")
    toplam_satis = 0
    toplam_maliyet = 0
    for s in liste:
        if s["tarih"].startswith(bugun):
            toplam_satis += s["toplam_tutar"]
            maliyet = s.get("maliyet", s.get("miktar", 0) * s.get("alis_fiyat", 0))
            toplam_maliyet += maliyet
    return round(toplam_satis - toplam_maliyet, 2)

def en_cok_satanlar(n=5, gun=7) -> list:
    satislar = dosya_oku(SATIS_DOSYASI, [])
    if not satislar:
        return []
    df = pd.DataFrame(satislar)
    df["tarih"] = pd.to_datetime(df["tarih"])
    baslangic = datetime.now() - timedelta(days=gun)
    df = df[df["tarih"] >= baslangic]
    if df.empty:
        return []
    populer = df.groupby("urun_adi")["miktar"].sum().sort_values(ascending=False).head(n)
    return populer.index.tolist()

def urun_gunluk_satis_hizi(urun_adi: str, varsayilan: float = 1.0) -> float:
    satislar = dosya_oku(SATIS_DOSYASI, [])
    if not satislar:
        for u in st.session_state.stok:
            if u["urun_adi"] == urun_adi:
                return u.get("tahmini_gunluk_satis", varsayilan)
        return varsayilan
    bugun = datetime.now().date()
    baslangic = bugun - timedelta(days=30)
    miktarlar = []
    for s in satislar:
        try:
            tarih = datetime.strptime(s["tarih"], "%Y-%m-%d %H:%M:%S").date()
            if s["urun_adi"] == urun_adi and baslangic <= tarih <= bugun:
                miktarlar.append(s["miktar"])
        except Exception:
            continue
    if not miktarlar:
        for u in st.session_state.stok:
            if u["urun_adi"] == urun_adi:
                return u.get("tahmini_gunluk_satis", varsayilan)
        return varsayilan
    return sum(miktarlar) / len(miktarlar)

def bilimsel_indirim_hesapla(urun: dict, kalan_gun: int) -> float:
    if kalan_gun <= 0:
        satis_fiyat = urun.get("satis_fiyat", 10)
        alis_fiyat = urun.get("alis_fiyat", 5)
        if satis_fiyat > 0:
            return min(50, int((satis_fiyat - alis_fiyat) / satis_fiyat * 100))
        return 50
    q = urun.get("miktar", 0)
    satis_fiyat = urun.get("satis_fiyat", 0)
    alis_fiyat = urun.get("alis_fiyat", 0)
    if satis_fiyat <= 0 or q <= 0:
        return 0
    m = (satis_fiyat - alis_fiyat) / satis_fiyat
    v = urun_gunluk_satis_hizi(urun["urun_adi"], varsayilan=urun.get("tahmini_gunluk_satis", 1.0))
    beklenen_satis = v * kalan_gun
    stok_fazlasi = q - beklenen_satis
    if stok_fazlasi <= 0:
        return 0
    indirim = (stok_fazlasi / q) * m * 100
    max_indirim = m * 100 * 0.8
    indirim = min(indirim, max_indirim)
    if kalan_gun <= 1:
        indirim = max(indirim, m * 100 * 0.5)
    elif kalan_gun <= 3:
        indirim = max(indirim, m * 100 * 0.2)
    return round(indirim, 1)

def mock_stok_olustur() -> list:
    return [
        {"urun_adi": "Un", "miktar": 150, "birim": "kg", "kategori": "Kuru Gıda",
         "min_miktar": 20, "barkod": "8691234567890", "son_kullanma_tarihi": "2026-12-31",
         "alis_fiyat": 18.50, "satis_fiyat": 25.90, "tedarikci": "ABC Un Fabrikası", "kdv_oran": 1,
         "raf_no": "A1", "tahmini_gunluk_satis": 5.0},
        {"urun_adi": "Şeker", "miktar": 5, "birim": "kg", "kategori": "Kuru Gıda",
         "min_miktar": 10, "barkod": "8691234567891", "son_kullanma_tarihi": "2026-05-15",
         "alis_fiyat": 22.00, "satis_fiyat": 32.50, "tedarikci": "XYZ Şeker", "kdv_oran": 8,
         "raf_no": "A2", "tahmini_gunluk_satis": 2.0},
        {"urun_adi": "Süt", "miktar": 40, "birim": "litre", "kategori": "Süt Ürünleri",
         "min_miktar": 15, "barkod": "8691234567892", "son_kullanma_tarihi": "2026-05-08",
         "alis_fiyat": 12.00, "satis_fiyat": 18.90, "tedarikci": "Sütaş", "kdv_oran": 1,
         "raf_no": "B1", "tahmini_gunluk_satis": 8.0},
        {"urun_adi": "Yumurta", "miktar": 200, "birim": "adet", "kategori": "Diğer",
         "min_miktar": 30, "barkod": "8691234567893", "son_kullanma_tarihi": "2026-05-06",
         "alis_fiyat": 2.50, "satis_fiyat": 4.50, "tedarikci": "Köy Yumurtası", "kdv_oran": 1,
         "raf_no": "C1", "tahmini_gunluk_satis": 30.0},
        {"urun_adi": "Tereyağı", "miktar": 25, "birim": "kg", "kategori": "Süt Ürünleri",
         "min_miktar": 5, "barkod": "8691234567894", "son_kullanma_tarihi": "2026-06-20",
         "alis_fiyat": 120.00, "satis_fiyat": 175.00, "tedarikci": "Sütaş", "kdv_oran": 8,
         "raf_no": "B2", "tahmini_gunluk_satis": 3.0},
    ]

def mock_fire_olustur() -> list:
    return [
        {"urun_adi": "Un", "miktar": 10, "birim": "kg", "aciliyet": "🔥 Yüksek",
         "tedarikci": "ABC Un Fabrikası", "durum": "Bekliyor",
         "eklenme_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M")},
        {"urun_adi": "Şeker", "miktar": 5, "birim": "kg", "aciliyet": "⚡ Orta",
         "tedarikci": "XYZ Şeker", "durum": "Sipariş Verildi",
         "eklenme_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M")},
        {"urun_adi": "Yumurta", "miktar": 50, "birim": "adet", "aciliyet": "✅ Düşük",
         "tedarikci": "Köy Yumurtası", "durum": "Bekliyor",
         "eklenme_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M")},
    ]

def mock_barkod_db_olustur() -> dict:
    return {
        "8691234567890": {"urun_adi": "Un", "birim": "kg", "kategori": "Kuru Gıda", "uretici": "ABC Un Fabrikası"},
        "8691234567891": {"urun_adi": "Şeker", "birim": "kg", "kategori": "Kuru Gıda", "uretici": "XYZ Şeker"},
        "8691234567892": {"urun_adi": "Süt", "birim": "litre", "kategori": "Süt Ürünleri", "uretici": "Sütaş"},
        "8691234567893": {"urun_adi": "Yumurta", "birim": "adet", "kategori": "Diğer", "uretici": "Köy Yumurtası"},
        "8691234567894": {"urun_adi": "Tereyağı", "birim": "kg", "kategori": "Süt Ürünleri", "uretici": "Sütaş"},
    }

def veriyi_kaydet() -> None:
    dosya_yaz(STOK_DOSYASI, st.session_state.stok)
    dosya_yaz(FIRE_DOSYASI, st.session_state.fire)
    dosya_yaz(TEDARIKCI_DOSYASI, st.session_state.tedarikciler)