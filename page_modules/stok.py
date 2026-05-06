import streamlit as st
import pandas as pd
from datetime import datetime
from ui import guvenli_html
from config import BIRIMLER, KATEGORILER
from data_handler import dosya_yaz, hareket_ekle, veriyi_kaydet

def goster():
    st.markdown('<div class="main-header">📦 Stok Yönetimi</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Liste", "➕ Ekle", "✏️ Düzenle/Sil", "🔢 Stok Sayım", "📥 Toplu Güncelle"])
    with tab1:
        df = pd.DataFrame(st.session_state.stok)
        if not df.empty:
            def style_row(row): return ['background-color:#ffcccc' if row.get('min_miktar',0)>0 and row['miktar']<=row['min_miktar'] else '' for _ in row]
            st.dataframe(df.style.apply(style_row, axis=1).format(precision=2), width='stretch')
        else: st.info("Ürün yok.")
    with tab2:
        with st.form("manuel_ekle"):
            barkod = st.text_input("Barkod")
            barkod_bilgi = st.session_state.barkod_db.get(barkod, {}) if barkod else {}
            c1, c2, c3 = st.columns(3)
            ad = c1.text_input("Ürün Adı *", value=barkod_bilgi.get("urun_adi",""))
            miktar = c1.number_input("Miktar", 0.0, format="%.2f")
            birim = c2.selectbox("Birim", BIRIMLER, index=BIRIMLER.index(barkod_bilgi.get("birim","adet")) if barkod_bilgi.get("birim") in BIRIMLER else 0)
            kategori = c3.selectbox("Kategori", KATEGORILER, index=KATEGORILER.index(barkod_bilgi.get("kategori","Diğer")) if barkod_bilgi.get("kategori") in KATEGORILER else 0)
            alis = c2.number_input("Alış Fiyatı", 0.0, format="%.2f"); satis = c3.number_input("Satış Fiyatı", 0.0, format="%.2f")
            min_m = c1.number_input("Min Stok", 0.0, format="%.2f", value=5.0)
            tahmini_gunluk = c2.number_input("Tahmini Günlük Satış", 0.1, format="%.1f", value=1.0)
            skt_var = c3.checkbox("SKT var mı?", value=True); skt = c1.date_input("SKT") if skt_var else ""
            raf = c2.text_input("Raf")
            if st.form_submit_button("💾 Kaydet"):
                if not ad.strip(): st.error("Ad zorunlu")
                else:
                    skt_str = skt.strftime("%Y-%m-%d") if skt_var else ""
                    if barkod and barkod not in st.session_state.barkod_db:
                        st.session_state.barkod_db[barkod] = {"urun_adi": ad.strip(), "birim": birim, "kategori": kategori}
                        dosya_yaz("barkod_db.json", st.session_state.barkod_db)
                    st.session_state.stok.append({"urun_adi": ad.strip(), "miktar": miktar, "birim": birim, "kategori": kategori, "min_miktar": min_m, "barkod": barkod.strip(), "son_kullanma_tarihi": skt_str, "alis_fiyat": alis, "satis_fiyat": satis, "raf_no": raf.strip(), "tahmini_gunluk_satis": tahmini_gunluk})
                    veriyi_kaydet(); st.session_state.son_islem_mesaji = f"🎉 {ad.strip()} eklendi!"; st.rerun()
    with tab3:
        if st.session_state.stok:
            urunler = [f"{guvenli_html(u['urun_adi'])} ({u['miktar']:.2f} {u['birim']})" for u in st.session_state.stok]
            secili = st.selectbox("Ürün Seç", urunler, key="duzenle_sec"); idx = urunler.index(secili); urun = st.session_state.stok[idx]
            with st.form("duzenle_form"):
                c1, c2, c3 = st.columns(3)
                yeni_ad = c1.text_input("Ürün Adı", value=urun["urun_adi"])
                yeni_miktar = c1.number_input("Miktar", value=float(urun["miktar"]), min_value=0.0, format="%.2f")
                birim_index = BIRIMLER.index(urun.get("birim","adet")) if urun.get("birim") in BIRIMLER else 0
                yeni_birim = c2.selectbox("Birim", BIRIMLER, index=birim_index)
                kat_index = KATEGORILER.index(urun.get("kategori","Diğer")) if urun.get("kategori") in KATEGORILER else 0
                yeni_kategori = c3.selectbox("Kategori", KATEGORILER, index=kat_index)
                yeni_alis = c2.number_input("Alış Fiyatı", value=float(urun.get("alis_fiyat",0)), format="%.2f")
                yeni_satis = c3.number_input("Satış Fiyatı", value=float(urun.get("satis_fiyat",0)), format="%.2f")
                yeni_min = c1.number_input("Min Stok", value=float(urun.get("min_miktar",0)), format="%.2f")
                yeni_tahmini = c2.number_input("Tahmini Günlük Satış", 0.1, format="%.1f", value=float(urun.get("tahmini_gunluk_satis",1.0)))
                mevcut_skt = urun.get("son_kullanma_tarihi","")
                skt_var = c3.checkbox("SKT var", value=bool(mevcut_skt))
                yeni_skt = ""
                if skt_var:
                    try: skt_date = datetime.strptime(mevcut_skt,"%Y-%m-%d") if mevcut_skt else datetime.now()
                    except: skt_date = datetime.now()
                    yeni_skt = c1.date_input("SKT", value=skt_date)
                yeni_raf = c2.text_input("Raf", value=urun.get("raf_no",""))
                if st.form_submit_button("💾 Güncelle"):
                    if not yeni_ad.strip(): st.error("Ad zorunlu")
                    else:
                        skt_str = yeni_skt.strftime("%Y-%m-%d") if skt_var else ""
                        st.session_state.stok[idx] = {"urun_adi": yeni_ad.strip(), "miktar": yeni_miktar, "birim": yeni_birim, "kategori": yeni_kategori, "min_miktar": yeni_min, "barkod": urun.get("barkod",""), "son_kullanma_tarihi": skt_str, "alis_fiyat": yeni_alis, "satis_fiyat": yeni_satis, "tedarikci": urun.get("tedarikci",""), "raf_no": yeni_raf.strip(), "kdv_oran": urun.get("kdv_oran",8), "tahmini_gunluk_satis": yeni_tahmini}
                        veriyi_kaydet(); st.session_state.son_islem_mesaji = f"✅ {yeni_ad.strip()} güncellendi"; st.rerun()
            with st.popover("🗑️ Sil"):
                st.warning("Geri alınamaz!")
                if st.button("⚠️ Onayla", key=f"pop_sil_{idx}"):
                    silinen = st.session_state.stok.pop(idx); veriyi_kaydet()
                    hareket_ekle(st.session_state.current_user["kullanici_adi"], "Silme", silinen["urun_adi"], "Ürün silindi")
                    st.session_state.son_islem_mesaji = f"🗑️ {silinen['urun_adi']} silindi"; st.rerun()
        else: st.info("Ürün yok.")
    with tab4:
        st.subheader("🔢 Stok Sayım"); st.info("📱 Barkod okutarak veya manuel giriş yapın.")
        kamera_img = st.camera_input("📷 Kameraya göster", key="sayim_kamera")
        sayim_barkod = st.text_input("🔍 veya barkodu yazın", key="sayim_barkod")
        if kamera_img and not sayim_barkod:
            try:
                import cv2, numpy as np
                img = cv2.imdecode(np.asarray(bytearray(kamera_img.read()), dtype=np.uint8), cv2.IMREAD_COLOR)
                data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
                if data: sayim_barkod = data; st.success(f"✅ {sayim_barkod}")
            except: pass
        if sayim_barkod:
            bulunan = next((u for u in st.session_state.stok if u.get("barkod")==sayim_barkod), None)
            if bulunan:
                st.success(f"✅ {bulunan['urun_adi']} (Sistem: {bulunan['miktar']})")
                with st.form("hizli_sayim"):
                    yeni = st.number_input("Gerçek Miktar", value=float(bulunan['miktar']), format="%.2f")
                    if st.form_submit_button("💾 Kaydet"):
                        fark = yeni - bulunan['miktar']; bulunan['miktar'] = yeni; veriyi_kaydet()
                        hareket_ekle(st.session_state.current_user["kullanici_adi"], "Sayım", bulunan['urun_adi'], f"Fark: {fark:+.2f}")
                        st.session_state.son_islem_mesaji = f"✅ {bulunan['urun_adi']} sayıldı"; st.rerun()
            else: st.warning("❌ Bulunamadı.")
        st.markdown("---"); st.write("📋 Manuel Sayım:")
        if st.session_state.stok:
            for i, u in enumerate(st.session_state.stok):
                col1, col2 = st.columns([3,1])
                with col1: st.write(f"{u['urun_adi']} – Sistem: {u['miktar']}")
                with col2:
                    with st.popover("Sayım"):
                        sayim = st.number_input("Gerçek", value=float(u['miktar']), format="%.2f", key=f"man_{i}")
                        if st.button("Kaydet", key=f"kaydet_{i}"):
                            fark = sayim - u['miktar']; u['miktar'] = sayim; veriyi_kaydet()
                            hareket_ekle(st.session_state.current_user["kullanici_adi"], "Sayım", u['urun_adi'], f"Fark: {fark:+.2f}")
                            st.session_state.son_islem_mesaji = f"✅ Sayım kaydedildi"; st.rerun()
        else: st.info("Ürün yok.")
    with tab5:
        st.subheader("📥 Toplu Güncelleme (CSV)"); st.markdown("Format: `barkod,miktar`")
        csv_dosya = st.file_uploader("CSV yükle", type=["csv"], key="toplu_csv")
        if csv_dosya:
            try:
                df_csv = pd.read_csv(csv_dosya, header=None, names=["barkod","miktar"])
                for _, row in df_csv.iterrows():
                    barkod = str(row["barkod"]).strip(); miktar = float(row["miktar"])
                    for u in st.session_state.stok:
                        if u.get("barkod") == barkod:
                            u["miktar"] += miktar
                            hareket_ekle(st.session_state.current_user["kullanici_adi"], "Toplu Güncelleme", u["urun_adi"], f"{miktar:+.2f}")
                            break
                veriyi_kaydet(); st.session_state.son_islem_mesaji = f"✅ {len(df_csv)} ürün güncellendi"; st.rerun()
            except Exception as e: st.error(f"Hata: {e}")