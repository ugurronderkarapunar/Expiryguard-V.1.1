import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import streamlit as st
from fpdf import FPDF

try:
    import pywhatkit as pwk
    WHATSAPP_AKTIF = True
except ImportError:
    WHATSAPP_AKTIF = False

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def email_gonder(alici: str, konu: str, mesaj: str) -> bool:
    try:
        smtp_sunucu = "smtp.gmail.com"
        port = 587
        gonderen = st.secrets["email"]["adres"]
        sifre = st.secrets["email"]["sifre"]
        msg = MIMEText(mesaj)
        msg["Subject"] = konu
        msg["From"] = gonderen
        msg["To"] = alici
        baglanti = smtplib.SMTP(smtp_sunucu, port)
        baglanti.starttls(context=ssl.create_default_context())
        baglanti.login(gonderen, sifre)
        baglanti.sendmail(gonderen, alici, msg.as_string())
        baglanti.quit()
        return True
    except Exception as e:
        logging.error(f"E‑posta gönderme hatası: {e}")
        return False

def email_gonder_pdf(alici: str, konu: str, mesaj: str, pdf_icerik: bytes, dosya_adi: str) -> bool:
    try:
        smtp_sunucu = "smtp.gmail.com"
        port = 587
        gonderen = st.secrets["email"]["adres"]
        sifre = st.secrets["email"]["sifre"]
        msg = MIMEMultipart()
        msg["Subject"] = konu
        msg["From"] = gonderen
        msg["To"] = alici
        msg.attach(MIMEText(mesaj))
        part = MIMEBase("application", "octet-stream")
        part.set_payload(pdf_icerik)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={dosya_adi}")
        msg.attach(part)
        baglanti = smtplib.SMTP(smtp_sunucu, port)
        baglanti.starttls(context=ssl.create_default_context())
        baglanti.login(gonderen, sifre)
        baglanti.sendmail(gonderen, alici, msg.as_string())
        baglanti.quit()
        return True
    except Exception as e:
        logging.error(f"PDF e‑posta hatası: {e}")
        return False

def tedarikciye_siparis_gonder(urun: dict, tedarikci_eposta: str) -> bool:
    if not tedarikci_eposta:
        return False
    konu = f"Otomatik Sipariş: {urun['urun_adi']} kritik stokta"
    mesaj = f"""
    Sayın {urun.get('tedarikci', 'Tedarikçi')},
    
    {urun['urun_adi']} ürününün stoğu kritik seviyeye düşmüştür.
    
    Mevcut stok: {urun['miktar']} {urun['birim']}
    Minimum stok: {urun.get('min_miktar', 0)} {urun['birim']}
    Önerilen sipariş miktarı: {urun.get('min_miktar', 10) - urun['miktar'] + 5} {urun['birim']}
    
    Lütfen en kısa sürede tedarik sağlayınız.
    
    Market Yönetim Sistemi
    """
    return email_gonder(tedarikci_eposta, konu, mesaj)

def fis_olustur(urun_adi: str, birim: str, miktar: float, birim_fiyat: float,
                toplam_tutar: float, odeme_tipi: str) -> FPDF:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=10)
    pdf.cell(80, 10, txt="🏪 Market Yönetim Sistemi", ln=True, align='C')
    pdf.cell(80, 10, txt="ALIŞVERİŞ FİŞİ", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("DejaVu", size=8)
    pdf.cell(80, 6, txt=f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("DejaVu", size=10)
    pdf.cell(50, 8, txt="Ürün:", border=0)
    pdf.cell(30, 8, txt=urun_adi[:20], border=0, ln=True)
    pdf.cell(50, 8, txt="Miktar:", border=0)
    pdf.cell(30, 8, txt=f"{miktar} {birim}", border=0, ln=True)
    pdf.cell(50, 8, txt="Birim Fiyat:", border=0)
    pdf.cell(30, 8, txt=f"{birim_fiyat:.2f} ₺", border=0, ln=True)
    pdf.ln(3)
    pdf.set_font("DejaVu", size=12)
    pdf.cell(50, 10, txt="TOPLAM:", border=0)
    pdf.cell(30, 10, txt=f"{toplam_tutar:.2f} ₺", border=0, ln=True)
    pdf.set_font("DejaVu", size=8)
    pdf.cell(50, 6, txt=f"Ödeme: {odeme_tipi}", border=0, ln=True)
    pdf.ln(5)
    pdf.cell(80, 6, txt="İyi günlerde kullanın!", ln=True, align='C')
    return pdf

def whatsapp_gonder(telefon_no: str, mesaj: str) -> bool:
    if not WHATSAPP_AKTIF:
        return False
    try:
        suanki_zaman = datetime.now()
        saat = suanki_zaman.hour
        dakika = suanki_zaman.minute + 2
        if dakika >= 60:
            saat += 1
            dakika -= 60
        pwk.sendwhatmsg(telefon_no, mesaj, saat, dakika, wait_time=15, tab_close=True)
        return True
    except Exception as e:
        logging.error(f"WhatsApp gönderme hatası: {e}")
        return False

def kritik_stok_whatsapp_bildirimi() -> None:
    if "whatsapp_bildirim_gonderildi" not in st.session_state:
        st.session_state.whatsapp_bildirim_gonderildi = False
    if not st.session_state.whatsapp_bildirim_gonderildi:
        patron_tel = st.session_state.get("patron_telefon", "")
        if not patron_tel:
            return
        kritik_urunler = [u for u in st.session_state.stok 
                         if u.get("min_miktar", 0) > 0 and u["miktar"] <= u["min_miktar"]]
        if kritik_urunler:
            mesaj = "🚨 *KRİTİK STOK UYARISI*\n\n"
            for u in kritik_urunler[:5]:
                mesaj += f"📦 {u['urun_adi']}: {u['miktar']} {u['birim']} (min: {u['min_miktar']})\n"
            if len(kritik_urunler) > 5:
                mesaj += f"\n... ve {len(kritik_urunler)-5} ürün daha"
            if whatsapp_gonder(f"+90{patron_tel}", mesaj):
                st.session_state.whatsapp_bildirim_gonderildi = True
                logging.info("WhatsApp bildirimi gönderildi.")