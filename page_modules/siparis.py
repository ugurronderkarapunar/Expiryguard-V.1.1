import streamlit as st
import pandas as pd
from datetime import datetime
from ui import guvenli_html
from data_handler import veriyi_kaydet
from utils import tedarikciye_siparis_gonder

def goster():
    st.markdown('<div class="main-header">🔥 Sipariş Panosu</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Liste", "➕ Ekle"])
    with tab1:
        df = pd.DataFrame(st.session_state.fire)
        if not df.empty:
            for i, row in df.iterrows():
                c1, c2, c3 = st.columns([3,1,1])
                with c1:
                    renk = "🟢" if "Düşük" in row['aciliyet'] else "🟡" if "Orta" in row['aciliyet'] else "🔴"
                    st.write(f"{renk} **{guvenli_html(row['urun_adi'])}** – {row['miktar']} {row['birim']} – {row['durum']}")
                with c2:
                    if st.button("🗑️ Sil", key=f"sil_fire_{i}"): st.session_state.fire.pop(i); veriyi_kaydet(); st.session_state.son_islem_mesaji = "Silindi"; st.rerun()
                with c3:
                    if st.button("📧 Tedarikçiye Gönder", key=f"tedarik_{i}"):
                        eposta = next((t["eposta"] for t in st.session_state.tedarikciler if t["ad"]==row.get("tedarikci","")), "")
                        if eposta:
                            urun_dict = row.to_dict()
                            for u in st.session_state.stok:
                                if u["urun_adi"] == row['urun_adi']: urun_dict["miktar"] = u["miktar"]; urun_dict["min_miktar"] = u.get("min_miktar",10); break
                            if tedarikciye_siparis_gonder(urun_dict, eposta): st.session_state.son_islem_mesaji = f"📧 {row['urun_adi']} gönderildi"; st.rerun()
                        else: st.error("E‑posta yok.")
        else: st.info("Sipariş yok.")
    with tab2:
        with st.form("fire_ekle"):
            ad = st.text_input("Ürün"); miktar = st.number_input("Miktar", 0.01, format="%.2f")
            if st.form_submit_button("Ekle"):
                st.session_state.fire.append({"urun_adi":ad,"miktar":miktar,"birim":"adet","aciliyet":"⚡ Orta","durum":"Bekliyor","eklenme_tarihi":datetime.now().strftime("%Y-%m-%d %H:%M")})
                veriyi_kaydet(); st.session_state.son_islem_mesaji = "🔥 Eklendi"; st.rerun()