import streamlit as st
import hashlib
from datetime import datetime, timedelta
from config import config, OTURUM_SURESI, KULLANICI_DOSYASI, ROLLER
from data_handler import dosya_oku, dosya_yaz, mock_stok_olustur, mock_fire_olustur, mock_barkod_db_olustur, veri_gecis_kontrol

def oturumu_baslat() -> None:
    if "stok" not in st.session_state:
        st.session_state.stok = dosya_oku("stok.json", mock_stok_olustur())
    if "fire" not in st.session_state:
        st.session_state.fire = dosya_oku("fire.json", mock_fire_olustur())
    if "barkod_db" not in st.session_state:
        st.session_state.barkod_db = dosya_oku("barkod_db.json", mock_barkod_db_olustur())
    if "tedarikciler" not in st.session_state:
        st.session_state.tedarikciler = dosya_oku("tedarikciler.json", [])
    if "kullanicilar" not in st.session_state:
        st.session_state.kullanicilar = dosya_oku(KULLANICI_DOSYASI, [
            {"kullanici_adi": "admin", "sifre": hashlib.sha256("1234".encode()).hexdigest(), "rol": "patron", "ad": "Ahmet"}
        ])
    if "pos_sepet" not in st.session_state:
        st.session_state.pos_sepet = {}
    if "son_islem_mesaji" not in st.session_state:
        st.session_state.son_islem_mesaji = ""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()
    if "tema" not in st.session_state:
        st.session_state.tema = "Koyu"
    if "patron_email" not in st.session_state:
        st.session_state.patron_email = ""
    if "patron_telefon" not in st.session_state:
        st.session_state.patron_telefon = ""
    veri_gecis_kontrol()

def oturum_kontrol() -> None:
    if st.session_state.authenticated:
        if datetime.now() - st.session_state.last_activity > timedelta(minutes=OTURUM_SURESI):
            st.session_state.authenticated = False
            st.warning("⏳ Oturum doldu")
            st.rerun()
        else:
            st.session_state.last_activity = datetime.now()

def giris_ekrani() -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            '<h1 style="text-align:center; background:linear-gradient(135deg,#F97316,#8B5CF6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">🏪 Market Yönetim</h1>',
            unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#E2E8F0;">Akıllı Stok Takibi</p>', unsafe_allow_html=True)
        with st.form("giris", clear_on_submit=False):
            kullanici = st.text_input("👤 Kullanıcı Adı", placeholder="admin")
            sifre = st.text_input("🔒 Şifre", type="password", placeholder="••••")
            if st.form_submit_button("🚀 Giriş Yap", use_container_width=True):
                try:
                    admin_user = st.secrets["admin"]["kullanici_adi"]
                    admin_pass = st.secrets["admin"]["sifre"]
                except Exception:
                    admin_user = config.get("kullanici_adi", "admin")
                    admin_pass = config.get("sifre", "1234")
                if kullanici == admin_user and sifre == admin_pass:
                    st.session_state.authenticated = True
                    st.session_state.current_user = {"kullanici_adi": admin_user, "rol": "patron", "ad": "Admin"}
                    st.session_state.last_activity = datetime.now()
                    st.rerun()
                else:
                    st.error("❌ Hatalı giriş!")

def cikis() -> None:
    st.session_state.authenticated = False
    st.rerun()

def izinli_sayfalar(kullanici: dict, SAYFALAR: dict) -> dict:
    if not kullanici:
        return {}
    rol = kullanici.get("rol", "")
    izinler = ROLLER.get(rol, [])
    if "tümü" in izinler:
        return SAYFALAR
    yetki_sayfa = {
        "barkod": ["📱 Barkod"],
        "satis": ["💵 Satış"],
        "stok": ["📦 Stok", "📈 Stok Analizi", "📉 Fire Analizi"],
        "stok_ekle": ["📦 Stok", "🔥 Sipariş"],
        "skt_takip": ["🏠 Ana Panel"],
    }
    izinli = {}
    for anahtar, fonksiyon in SAYFALAR.items():
        for yetki in izinler:
            if anahtar in yetki_sayfa.get(yetki, []):
                izinli[anahtar] = fonksiyon
                break
    return izinli