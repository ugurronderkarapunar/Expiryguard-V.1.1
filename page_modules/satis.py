import streamlit as st
from datetime import datetime
from ui import guvenli_html
from data_handler import satis_kaydet, en_cok_satanlar, hareket_ekle, veriyi_kaydet, dosya_oku
from utils import fis_olustur
from config import SATIS_DOSYASI

def pos_modu():
    st.markdown('<div class="main-header">🛒 Hızlı Satış (POS)</div>', unsafe_allow_html=True)
    if "pos_sepet" not in st.session_state: st.session_state.pos_sepet = {}
    tab1, tab2 = st.tabs(["📷 Kamera", "🔢 Manuel"])
    with tab1:
        st.info("Barkodu okutunca sepete eklenir.")
        img_file = st.camera_input("📷 Barkodu gösterin", key="pos_kamera")
        barkod_manuel = st.text_input("veya barkodu yazın", key="pos_manuel_barkod")
        barkod = None
        if img_file:
            try:
                import cv2, numpy as np
                img = cv2.imdecode(np.asarray(bytearray(img_file.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
                data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
                if data: barkod = data; st.success(f"✅ {barkod}")
            except Exception as e: st.error(f"Hata: {e}")
        if barkod_manuel: barkod = barkod_manuel
        if barkod:
            if barkod in st.session_state.pos_sepet: st.session_state.pos_sepet[barkod] += 1
            else: st.session_state.pos_sepet[barkod] = 1
            st.toast(f"Sepete eklendi: {barkod}"); st.rerun()
        if st.session_state.pos_sepet:
            st.subheader("🧺 Sepet"); toplam_tutar = 0
            for barkod_kodu, adet in st.session_state.pos_sepet.items():
                urun = next((u for u in st.session_state.stok if u.get("barkod")==barkod_kodu), None)
                if urun:
                    fiyat = urun.get("satis_fiyat",0); tutar = fiyat * adet; toplam_tutar += tutar
                    col1, col2, col3 = st.columns([3,1,1])
                    with col1: st.write(f"📦 {guvenli_html(urun['urun_adi'])} – {adet} {urun['birim']} x {fiyat:.2f} = {tutar:.2f} ₺")
                    with col2:
                        yeni_adet = st.number_input("Adet", 1, value=adet, key=f"adet_{barkod_kodu}")
                        if yeni_adet != adet: st.session_state.pos_sepet[barkod_kodu] = yeni_adet; st.rerun()
                    with col3:
                        if st.button("🗑️", key=f"sil_{barkod_kodu}"): del st.session_state.pos_sepet[barkod_kodu]; st.rerun()
                else: st.warning(f"❓ {barkod_kodu} bulunamadı.")
            st.markdown(f"### 🧾 Toplam: {toplam_tutar:.2f} ₺")
            odeme_tipi = st.selectbox("💳 Ödeme", ["Nakit","Kredi Kartı","Havale/EFT","Yemek Kartı"], key="odeme_pos")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💳 Satışı Tamamla", type="primary"):
                    for barkod_kodu, adet in st.session_state.pos_sepet.items():
                        urun = next((u for u in st.session_state.stok if u.get("barkod")==barkod_kodu), None)
                        if urun and urun["miktar"] >= adet:
                            fiyat = urun.get("satis_fiyat",0); urun["miktar"] -= adet
                            satis_kaydet(urun["urun_adi"], urun["birim"], adet, fiyat, fiyat*adet, st.session_state.current_user["kullanici_adi"], urun.get("alis_fiyat",0), odeme_tipi)
                            hareket_ekle(st.session_state.current_user["kullanici_adi"], "POS", urun["urun_adi"], f"{adet} {urun['birim']}")
                            if urun["miktar"] <= urun.get("min_miktar",0):
                                if not any(f["urun_adi"]==urun["urun_adi"] and f["durum"]=="Bekliyor" for f in st.session_state.fire):
                                    st.session_state.fire.append({"urun_adi":urun["urun_adi"],"miktar":urun["min_miktar"]-urun["miktar"]+1,"birim":urun["birim"],"aciliyet":"🔥 Yüksek","tedarikci":urun.get("tedarikci",""),"durum":"Bekliyor","eklenme_tarihi":datetime.now().strftime("%Y-%m-%d %H:%M")})
                    veriyi_kaydet()
                    if st.session_state.pos_sepet:
                        ilk_barkod = list(st.session_state.pos_sepet.keys())[0]; ilk_urun = next((u for u in st.session_state.stok if u.get("barkod")==ilk_barkod), None)
                        if ilk_urun:
                            pdf = fis_olustur(ilk_urun["urun_adi"], ilk_urun["birim"], st.session_state.pos_sepet[ilk_barkod], ilk_urun.get("satis_fiyat",0), toplam_tutar, odeme_tipi)
                            pdf.output("fis.pdf")
                            with open("fis.pdf","rb") as f: st.download_button("🧾 Fişi İndir", f.read(), "fis.pdf")
                    st.session_state.pos_sepet = {}; st.success(f"✅ Satış: {toplam_tutar:.2f} ₺"); st.rerun()
            with col_btn2:
                if st.button("🗑️ Sepeti Temizle"): st.session_state.pos_sepet = {}; st.rerun()
    with tab2:
        satilabilir = [u for u in st.session_state.stok if u["miktar"]>0]
        if satilabilir:
            secili_str = st.selectbox("Ürün Seçin", [f"{guvenli_html(u['urun_adi'])} ({u['miktar']:.2f} {u['birim']} - {u.get('satis_fiyat',0):.2f} ₺)" for u in satilabilir])
            idx = [f"{u['urun_adi']} ({u['miktar']:.2f} {u['birim']} - {u.get('satis_fiyat',0):.2f} ₺)" for u in satilabilir].index(secili_str)
            urun = satilabilir[idx]; fiyat = urun.get("satis_fiyat",0); mevcut = urun["miktar"]
            miktar = st.number_input("Miktar", 0.01, float(mevcut), format="%.2f", value=1.0)
            st.metric("Birim Fiyat", f"{fiyat:.2f} ₺"); toplam = miktar * fiyat
            odeme_tipi = st.selectbox("💳 Ödeme", ["Nakit","Kredi Kartı","Havale/EFT","Yemek Kartı"])
            if st.button("💳 Manuel Satış", type="primary"):
                if miktar<=0 or miktar>mevcut: st.error("Geçersiz miktar")
                else:
                    urun["miktar"] -= miktar
                    satis_kaydet(urun["urun_adi"], urun["birim"], miktar, fiyat, toplam, st.session_state.current_user["kullanici_adi"], urun.get("alis_fiyat",0), odeme_tipi)
                    hareket_ekle(st.session_state.current_user["kullanici_adi"], "Manuel", urun["urun_adi"], f"{miktar} {urun['birim']}")
                    veriyi_kaydet()
                    pdf = fis_olustur(urun["urun_adi"], urun["birim"], miktar, fiyat, toplam, odeme_tipi); pdf.output("fis.pdf")
                    with open("fis.pdf","rb") as f: st.download_button("🧾 Fişi İndir", f.read(), "fis.pdf")
                    st.success(f"✅ Satış: {toplam:.2f} ₺"); st.rerun()
        else: st.warning("Satılacak ürün yok")
    if st.button("🚪 POS Modundan Çık"): st.session_state.pos_modu = False; st.rerun()

def goster():
    if st.session_state.get("pos_modu", False): pos_modu(); return
    st.markdown('<div class="main-header">💰 Satış (POS)</div>', unsafe_allow_html=True)
    if st.button("🚀 Hızlı POS Moduna Geç"): st.session_state.pos_modu = True; st.session_state.pos_sepet = {}; st.rerun()
    satilabilir = [u for u in st.session_state.stok if u["miktar"]>0]
    if not satilabilir: st.warning("Satılacak ürün yok"); return
    populer = en_cok_satanlar(5, gun=7)
    if populer:
        st.subheader("⚡ Son 7 Günün En Çok Satanları"); kisa_sutun = st.columns(len(populer))
        for i, urun_adi in enumerate(populer):
            urun = next((u for u in satilabilir if u["urun_adi"]==urun_adi), None)
            if urun:
                with kisa_sutun[i]:
                    if st.button(f"🛒 {urun['urun_adi']}\n1 {urun['birim']}", key=f"hizli_{urun_adi}"):
                        urun["miktar"]-=1; satis_kaydet(urun["urun_adi"],urun["birim"],1,urun.get("satis_fiyat",0),urun.get("satis_fiyat",0),st.session_state.current_user["kullanici_adi"]); veriyi_kaydet(); st.session_state.son_islem_mesaji=f"✅ Hızlı: {urun['urun_adi']}"; st.rerun()
    secili_str = st.selectbox("Ürün Seçin", [f"{guvenli_html(u['urun_adi'])} ({u['miktar']:.2f} {u['birim']} - {u.get('satis_fiyat',0):.2f} ₺)" for u in satilabilir])
    idx = [f"{u['urun_adi']} ({u['miktar']:.2f} {u['birim']} - {u.get('satis_fiyat',0):.2f} ₺)" for u in satilabilir].index(secili_str)
    urun = satilabilir[idx]; fiyat = urun.get("satis_fiyat",0); mevcut = urun["miktar"]
    c1, c2 = st.columns(2)
    with c1: miktar = st.number_input("Miktar", 0.01, float(mevcut), format="%.2f", value=1.0)
    with c2: st.metric("Birim Fiyat", f"{fiyat:.2f} ₺")
    kalan = mevcut - miktar; st.metric("📦 Kalan Stok", f"{kalan:.2f} {urun['birim']}")
    toplam = miktar * fiyat; odeme_tipi = st.selectbox("💳 Ödeme", ["Nakit","Kredi Kartı","Havale/EFT","Yemek Kartı"])
    if st.button("💳 Satış Yap", type="primary"):
        if miktar<=0 or miktar>mevcut: st.error("Geçersiz miktar")
        else:
            for u in st.session_state.stok:
                if u["urun_adi"]==urun["urun_adi"] and u.get("barkod")==urun.get("barkod"):
                    u["miktar"] = round(u["miktar"]-miktar,2)
                    if u["miktar"] <= u.get("min_miktar",0):
                        if not any(f["urun_adi"]==u["urun_adi"] and f["durum"]=="Bekliyor" for f in st.session_state.fire):
                            st.session_state.fire.append({"urun_adi":u["urun_adi"],"miktar":u["min_miktar"]-u["miktar"]+2,"birim":u["birim"],"aciliyet":"🔥 Yüksek","tedarikci":u.get("tedarikci",""),"durum":"Bekliyor","eklenme_tarihi":datetime.now().strftime("%Y-%m-%d %H:%M")}); break
            satis_kaydet(urun["urun_adi"], urun["birim"], miktar, fiyat, toplam, st.session_state.current_user["kullanici_adi"], urun.get("alis_fiyat",0), odeme_tipi)
            hareket_ekle(st.session_state.current_user["kullanici_adi"], "Satış", urun["urun_adi"], f"{miktar} {urun['birim']}")
            veriyi_kaydet(); pdf = fis_olustur(urun["urun_adi"], urun["birim"], miktar, fiyat, toplam, odeme_tipi); pdf.output("fis.pdf")
            with open("fis.pdf","rb") as f: st.download_button("🧾 Fişi İndir", f.read(), "fis.pdf")
            st.session_state.son_islem_mesaji = f"✅ Satış: {toplam:.2f} ₺"; st.rerun()