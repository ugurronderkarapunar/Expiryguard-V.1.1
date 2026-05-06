import streamlit as st
from ui import guvenli_html
from config import BIRIMLER, KATEGORILER
from data_handler import dosya_yaz, veriyi_kaydet

def goster():
    st.markdown('<div class="main-header">📱 Barkod Okutma</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: barkod_manuel = st.text_input("🔢 Barkod Numarası", placeholder="Okutun veya yazın...", key="manuel_barkod")
    with c2: img_file = st.camera_input("📷 Mobil Kamera")
    barkod = None
    if img_file:
        try:
            import cv2, numpy as np
            img = cv2.imdecode(np.asarray(bytearray(img_file.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(img)
            if data: barkod = data; st.success(f"✅ Okunan: {barkod}")
            else: st.warning("Barkod algılanamadı.")
        except Exception as e: st.error(f"Kamera hatası: {e}")
    aktif = barkod_manuel or barkod
    if aktif:
        bilgi = st.session_state.barkod_db.get(aktif, {})
        urun_adi = bilgi.get("urun_adi", "")
        if urun_adi: st.info(f"📦 **{guvenli_html(urun_adi)}** ({bilgi.get('birim','')}) – {guvenli_html(bilgi.get('uretici',''))}")
        else: st.warning("❓ Yeni barkod.")
        with st.form("barkod_form"):
            c1, c2 = st.columns(2)
            ad = c1.text_input("Ürün Adı *", value=urun_adi)
            miktar = c1.number_input("Miktar", 0.01, format="%.2f", value=1.0)
            birim = c2.selectbox("Birim", BIRIMLER, index=BIRIMLER.index(bilgi.get("birim","adet")) if bilgi.get("birim") in BIRIMLER else 0)
            kategori = c2.selectbox("Kategori", KATEGORILER, index=KATEGORILER.index(bilgi.get("kategori","Diğer")) if bilgi.get("kategori") in KATEGORILER else 0)
            skt_var = c2.checkbox("SKT var mı?", value=True)
            if skt_var: skt = c1.date_input("SKT")
            else: skt = ""
            islem = c2.radio("İşlem", ["📥 Giriş", "📤 Çıkış"], horizontal=True)
            if st.form_submit_button("💾 Kaydet"):
                if not ad.strip(): st.error("Ad zorunlu")
                else:
                    if aktif not in st.session_state.barkod_db:
                        st.session_state.barkod_db[aktif] = {"urun_adi": ad.strip(), "birim": birim, "kategori": kategori}
                        dosya_yaz("barkod_db.json", st.session_state.barkod_db)
                    gercek = miktar if islem == "📥 Giriş" else -miktar
                    skt_str = skt.strftime("%Y-%m-%d") if skt_var else ""
                    for u in st.session_state.stok:
                        if u.get("barkod") == aktif:
                            u["miktar"] += gercek
                            if skt_var: u["son_kullanma_tarihi"] = skt_str
                            veriyi_kaydet(); st.session_state.son_islem_mesaji = f"✅ {ad.strip()} güncellendi"; st.rerun()
                    st.session_state.stok.append({"urun_adi": ad.strip(), "miktar": max(0, gercek), "birim": birim, "kategori": kategori, "son_kullanma_tarihi": skt_str, "barkod": aktif, "min_miktar": 0, "alis_fiyat": 0, "satis_fiyat": 0})
                    veriyi_kaydet(); st.session_state.son_islem_mesaji = f"✅ {ad.strip()} eklendi"; st.rerun()