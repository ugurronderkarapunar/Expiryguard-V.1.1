import streamlit as st
import pandas as pd
from ui import enerjik_css, tema_degistir
from auth import oturumu_baslat, oturum_kontrol, giris_ekrani, cikis, izinli_sayfalar

from page_modules.dashboard import goster as ana_sayfa
from page_modules.barkod import goster as barkod_sayfasi
from page_modules.stok import goster as stok_sayfasi
from page_modules.satis import goster as satis_sayfasi
from page_modules.siparis import goster as siparis_sayfasi
from page_modules.diger import (
    tedarikci_sayfasi, stok_analizi, fire_analizi, satis_raporu,
    aktivite_logu, kasa_kapanisi, kullanici_yonetimi, sifre_sifirla,
    geri_bildirim, ayarlar_sayfasi, yedekleme_sayfasi,
)

SAYFALAR = {
    "🏠 Ana Panel": ana_sayfa, "📱 Barkod": barkod_sayfasi,
    "💵 Satış": satis_sayfasi, "📦 Stok": stok_sayfasi,
    "🔥 Sipariş": siparis_sayfasi, "🏭 Tedarikçi": tedarikci_sayfasi,
    "📈 Stok Analizi": stok_analizi, "📉 Fire Analizi": fire_analizi,
    "📊 Satış Raporu": satis_raporu, "📋 Aktivite Logu": aktivite_logu,
    "🧾 Kasa Kapanışı": kasa_kapanisi, "👥 Kullanıcı Yönetimi": kullanici_yonetimi,
    "🔑 Şifre Sıfırlama": sifre_sifirla, "💬 Geri Bildirim": geri_bildirim,
    "⚙️ Ayarlar": ayarlar_sayfasi, "💾 Yedekleme": yedekleme_sayfasi,
}

def main() -> None:
    st.set_page_config(page_title="Market Yönetim", page_icon="🏪", layout="wide", initial_sidebar_state="expanded")
    oturumu_baslat()
    enerjik_css(st.session_state.get("tema", "Koyu"))
    pd.set_option('display.float_format', '{:.2f}'.format)
    oturum_kontrol()
    if not st.session_state.authenticated:
        giris_ekrani()
        return
    if st.session_state.son_islem_mesaji:
        st.success(st.session_state.son_islem_mesaji)
        st.session_state.son_islem_mesaji = ""
    with st.sidebar:
        st.markdown('<h2 style="color:white;">🏪 Market</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color:#F97316;">v3.0 Modüler</p>', unsafe_allow_html=True)
        if st.session_state.current_user:
            st.markdown(f'<div style="background:rgba(249,115,22,0.2);border-radius:12px;padding:12px;"><p style="color:white;">👤 {st.session_state.current_user.get("ad", "Kullanıcı")}</p></div>', unsafe_allow_html=True)
        st.selectbox("Tema", ["Koyu", "Aydınlık"], index=0 if st.session_state.get("tema", "Koyu") == "Koyu" else 1,
                     key="tema_secimi", on_change=tema_degistir)
        aktif_sayfalar = izinli_sayfalar(st.session_state.current_user, SAYFALAR)
        if not aktif_sayfalar:
            st.error("İzinli sayfa yok.")
            st.stop()
        sayfa = st.radio("Menü", list(aktif_sayfalar.keys()), label_visibility="collapsed")
        if st.button("🚪 Çıkış", use_container_width=True):
            cikis()
    aktif_sayfalar[sayfa]()

if __name__ == "__main__":
    main()