import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import json, logging, hashlib

from ui import guvenli_html
from data_handler import dosya_oku, dosya_yaz, veriyi_kaydet, gunluk_kar, urun_gunluk_satis_hizi
from config import SATIS_DOSYASI, HAREKET_DOSYASI, ROLLER, TEDARIKCI_DOSYASI, KULLANICI_DOSYASI, CONFIG_DOSYASI, config
from utils import email_gonder, email_gonder_pdf, whatsapp_gonder

def tedarikci_sayfasi():
    st.markdown('<div class="main-header">🏭 Tedarikçi Yönetimi</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Liste","➕ Ekle"])
    with tab1:
        if st.session_state.tedarikciler:
            for t in st.session_state.tedarikciler: st.markdown(f"**{guvenli_html(t['ad'])}** – Güven: {t.get('guven_puani',0):.1f}/10 – Tel: {t.get('tel','')} – E‑posta: {t.get('eposta','')}")
        else: st.info("Henüz tedarikçi eklenmemiş.")
    with tab2:
        with st.form("tedarikci_ekle"):
            ad = st.text_input("Firma Adı"); guven = st.slider("Güven", 0.0, 10.0, 5.0); tel = st.text_input("Telefon"); eposta = st.text_input("E‑posta")
            if st.form_submit_button("Ekle"): st.session_state.tedarikciler.append({"ad":ad,"guven_puani":guven,"tel":tel,"eposta":eposta}); dosya_yaz(TEDARIKCI_DOSYASI, st.session_state.tedarikciler); st.session_state.son_islem_mesaji="🏭 Eklendi"; st.rerun()

def stok_analizi():
    st.markdown('<div class="main-header">📈 Stok Analizi</div>', unsafe_allow_html=True)
    if not st.session_state.stok: st.info("Ürün yok."); return
    df = pd.DataFrame(st.session_state.stok)
    st.subheader("💵 Kâr Marjı"); df["kar_marji"] = df.apply(lambda r: ((r['satis_fiyat']-r['alis_fiyat'])/r['satis_fiyat']*100) if r['satis_fiyat']>0 else 0, axis=1)
    st.dataframe(df[["urun_adi","satis_fiyat","alis_fiyat","kar_marji"]].style.format({"kar_marji":"{:.1f}%"}), width='stretch')
    st.subheader("🔄 Stok Devir Hızı")
    for u in st.session_state.stok: st.write(f"{u['urun_adi']}: {urun_gunluk_satis_hizi(u['urun_adi'], u.get('tahmini_gunluk_satis',1.0)):.2f} {u['birim']}/gün")

def fire_analizi():
    st.markdown('<div class="main-header">📉 Fire Analizi</div>', unsafe_allow_html=True)
    if st.session_state.fire:
        kat_fire = {}
        for f in st.session_state.fire:
            kat = next((u.get("kategori","Diğer") for u in st.session_state.stok if u["urun_adi"]==f["urun_adi"]), "Diğer")
            kat_fire[kat] = kat_fire.get(kat,0)+f["miktar"]
        fig = px.pie(names=list(kat_fire.keys()), values=list(kat_fire.values()), title="Kategori Bazlı Fire", hole=0.3)
        st.plotly_chart(fig, width='stretch')
    else: st.info("Fire kaydı yok.")

def satis_raporu():
    st.markdown('<div class="main-header">📊 Satış Raporu</div>', unsafe_allow_html=True)
    satislar = dosya_oku(SATIS_DOSYASI,[])
    if not satislar: st.info("Henüz satış yok."); return
    df = pd.DataFrame(satislar); df["tarih"] = pd.to_datetime(df["tarih"]); df["gun"]=df["tarih"].dt.date; df["ay"]=df["tarih"].dt.strftime("%Y-%m")
    c1, c2, _ = st.columns(3)
    with c1: aralik = st.date_input("Tarih", value=(df["gun"].min(), df["gun"].max()), key="rapor_tarih")
    with c2: tip = st.radio("Kırılım", ["Günlük","Aylık","Ürün Bazlı","Kâr Marjı"], horizontal=True)
    if len(aralik)==2: df = df[(df["gun"]>=aralik[0])&(df["gun"]<=aralik[1])]
    if tip=="Günlük":
        rpr = df.groupby("gun")["toplam_tutar"].sum().reset_index(); rpr.columns=["Tarih","Toplam"]
        st.dataframe(rpr, width='stretch'); fig = px.bar(rpr, x="Tarih", y="Toplam", title="Günlük"); st.plotly_chart(fig, width='stretch')
    elif tip=="Aylık":
        rpr = df.groupby("ay")["toplam_tutar"].sum().reset_index(); rpr.columns=["Ay","Toplam"]
        st.dataframe(rpr, width='stretch'); fig = px.line(rpr, x="Ay", y="Toplam", markers=True, title="Aylık"); st.plotly_chart(fig, width='stretch')
    elif tip=="Ürün Bazlı":
        rpr = df.groupby("urun_adi").agg(Adet=("miktar","sum"), Ciro=("toplam_tutar","sum")).reset_index(); st.dataframe(rpr, width='stretch')
        colA, colB = st.columns(2)
        with colA: fig1 = px.pie(rpr, values="Ciro", names="urun_adi", title="Ciro", hole=0.3); st.plotly_chart(fig1, width='stretch')
        with colB: fig2 = px.bar(rpr, x="urun_adi", y="Adet", title="Adet"); st.plotly_chart(fig2, width='stretch')
    else:
        df_kar = pd.DataFrame(st.session_state.stok); df_kar["kar_marji"] = df_kar.apply(lambda r: ((r['satis_fiyat']-r['alis_fiyat'])/r['satis_fiyat']*100) if r['satis_fiyat']>0 else 0, axis=1)
        st.dataframe(df_kar[["urun_adi","satis_fiyat","alis_fiyat","kar_marji"]].style.format({"kar_marji":"{:.1f}%"}), width='stretch')

def aktivite_logu():
    st.markdown('<div class="main-header">📋 Aktivite Logu</div>', unsafe_allow_html=True)
    hareketler = dosya_oku(HAREKET_DOSYASI,[])
    if not hareketler: st.info("Henüz hareket yok."); return
    df = pd.DataFrame(hareketler); df["tarih"] = pd.to_datetime(df["tarih"])
    c1, c2 = st.columns(2)
    with c1: baslangic = st.date_input("Başlangıç", df["tarih"].min().date())
    with c2: bitis = st.date_input("Bitiş", df["tarih"].max().date())
    mask = (df["tarih"].dt.date>=baslangic)&(df["tarih"].dt.date<=bitis)
    st.dataframe(df[mask].sort_values("tarih", ascending=False), width='stretch')

def kasa_kapanisi():
    st.markdown('<div class="main-header">🧾 Günlük Kasa Kapanışı</div>', unsafe_allow_html=True)
    bugun = datetime.now().strftime("%Y-%m-%d")
    satislar = [s for s in dosya_oku(SATIS_DOSYASI,[]) if s["tarih"].startswith(bugun)]
    if not satislar: st.info("Bugün satış yok."); return
    toplam = sum(s["toplam_tutar"] for s in satislar); df = pd.DataFrame(satislar)
    st.subheader("📋 Satış Detayı"); st.dataframe(df[["urun_adi","miktar","birim_fiyat","toplam_tutar"]], width='stretch')
    st.metric("Toplam Satış", f"{toplam:.2f} ₺"); st.metric("💎 Net Kâr", f"{gunluk_kar():.2f} ₺")
    st.subheader("💳 Ödeme Kanalları")
    if "odeme_tipi" in df.columns:
        odeme_ozet = df.groupby("odeme_tipi")["toplam_tutar"].sum()
        for kanal, tutar in odeme_ozet.items(): st.metric(f"💳 {kanal}", f"{tutar:,.2f} ₺")
    if st.button("📄 PDF İndir"):
        pdf = FPDF(); pdf.add_page(); pdf.add_font("DejaVu","","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",uni=True); pdf.set_font("DejaVu",size=12)
        pdf.cell(200,10,txt=f"Kasa Kapanış - {bugun}",ln=True,align='C'); pdf.ln(10)
        for _, row in df.iterrows():
            pdf.cell(50,10,txt=row["urun_adi"],border=1); pdf.cell(30,10,txt=str(row["miktar"]),border=1)
            pdf.cell(30,10,txt=f"{row['birim_fiyat']} ₺",border=1); pdf.cell(30,10,txt=f"{row['toplam_tutar']} ₺",border=1); pdf.ln()
        pdf.ln(10); pdf.cell(200,10,txt=f"Toplam: {toplam:.2f} ₺",ln=True); pdf.output("kasa.pdf")
        with open("kasa.pdf","rb") as f: st.download_button("📥 PDF İndir", f.read(), "kasa.pdf")
    if st.button("📧 Patrona Gönder"):
        alici = st.session_state.get("patron_email","")
        if not alici: st.error("E‑posta tanımlanmamış.")
        else:
            pdf = FPDF(); pdf.add_page(); pdf.add_font("DejaVu","","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",uni=True); pdf.set_font("DejaVu",size=12)
            pdf.cell(200,10,txt=f"Kasa Kapanış - {bugun}",ln=True,align='C'); pdf.ln(10)
            for _, row in df.iterrows():
                pdf.cell(50,10,txt=row["urun_adi"],border=1); pdf.cell(30,10,txt=str(row["miktar"]),border=1)
                pdf.cell(30,10,txt=f"{row['birim_fiyat']} ₺",border=1); pdf.cell(30,10,txt=f"{row['toplam_tutar']} ₺",border=1); pdf.ln()
            pdf.ln(10); pdf.cell(200,10,txt=f"Toplam: {toplam:.2f} ₺",ln=True); pdf.output("kasa.pdf")
            if email_gonder_pdf(alici, "Kasa Raporu", "Günlük kasa ektedir.", open("kasa.pdf","rb").read(), "kasa.pdf"): st.success("✅ Gönderildi")
            else: st.error("Gönderilemedi.")

def kullanici_yonetimi():
    st.markdown('<div class="main-header">👥 Kullanıcı Yönetimi</div>', unsafe_allow_html=True)
    with st.form("kullanici_ekle"):
        yeni_kul = st.text_input("Kullanıcı Adı"); yeni_sifre = st.text_input("Şifre", type="password")
        rol = st.selectbox("Rol", list(ROLLER.keys())); ad = st.text_input("Ad Soyad")
        if st.form_submit_button("Ekle"):
            if not yeni_kul or not yeni_sifre: st.error("Zorunlu alanlar")
            else: st.session_state.kullanicilar.append({"kullanici_adi":yeni_kul,"sifre":hashlib.sha256(yeni_sifre.encode()).hexdigest(),"rol":rol,"ad":ad}); dosya_yaz(KULLANICI_DOSYASI, st.session_state.kullanicilar); st.session_state.son_islem_mesaji=f"✅ {yeni_kul} eklendi"; st.rerun()

def sifre_sifirla():
    st.markdown('<div class="main-header">🔑 Şifre Sıfırlama</div>', unsafe_allow_html=True)
    with st.form("sifre_sifirla"):
        eski = st.text_input("Eski Şifre", type="password"); yeni = st.text_input("Yeni Şifre", type="password"); yeni2 = st.text_input("Yeni Tekrar", type="password")
        if st.form_submit_button("Sıfırla"):
            admin_pass = config.get("sifre","1234")
            try: admin_pass = st.secrets["admin"]["sifre"]
            except: pass
            if eski != admin_pass: st.error("Eski şifre yanlış.")
            elif yeni != yeni2: st.error("Eşleşmiyor.")
            elif len(yeni)<4: st.error("En az 4 karakter.")
            else: config["sifre"] = yeni; dosya_yaz(CONFIG_DOSYASI, config); st.session_state.son_islem_mesaji="✅ Güncellendi"; st.rerun()

def geri_bildirim():
    st.markdown('<div class="main-header">💬 Geri Bildirim</div>', unsafe_allow_html=True)
    with st.form("geribildirim"):
        konu = st.text_input("Konu"); mesaj = st.text_area("Görüşleriniz")
        if st.form_submit_button("Gönder"): logging.info(f"Geri Bildirim: {konu} - {mesaj}"); st.session_state.son_islem_mesaji="✅ Teşekkürler!"; st.rerun()

def ayarlar_sayfasi():
    st.markdown('<div class="main-header">⚙️ Ayarlar</div>', unsafe_allow_html=True)
    with st.form("ayarlar"):
        eposta = st.text_input("Patron E‑posta", value=st.session_state.get("patron_email",""))
        telefon = st.text_input("Patron Tel (5XXXXXXXXX)", value=st.session_state.get("patron_telefon",""))
        col1, col2, col3 = st.columns(3)
        with col1: kaydet = st.form_submit_button("💾 Kaydet")
        with col2: test_eposta = st.form_submit_button("📧 Test E‑posta")
        with col3: test_wp = st.form_submit_button("📱 Test WhatsApp")
        if kaydet: st.session_state.patron_email=eposta; st.session_state.patron_telefon=telefon; st.session_state.son_islem_mesaji="✅ Kaydedildi"; st.rerun()
        if test_eposta:
            if not eposta: st.error("E‑posta girin")
            elif email_gonder(eposta, "Test", "Market Yönetim test mesajıdır."): st.session_state.son_islem_mesaji="✅ Gönderildi"; st.rerun()
        if test_wp:
            if not telefon: st.error("Tel girin")
            elif whatsapp_gonder(f"+90{telefon}", "Test mesajıdır."): st.session_state.son_islem_mesaji="✅ Gönderildi"; st.rerun()

def yedekleme_sayfasi():
    st.markdown('<div class="main-header">💾 Yedekleme</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        yedek = {"stok":st.session_state.stok,"fire":st.session_state.fire,"barkod_db":st.session_state.barkod_db,"tedarikciler":st.session_state.tedarikciler}
        st.download_button("📥 JSON İndir", json.dumps(yedek, ensure_ascii=False, indent=2), "yedek.json", use_container_width=True)
    with c2:
        dosya = st.file_uploader("Yedek yükle", type="json")
        if dosya:
            icerik = json.load(dosya); st.session_state.stok=icerik.get("stok",[]); st.session_state.fire=icerik.get("fire",[]); st.session_state.barkod_db=icerik.get("barkod_db",{}); st.session_state.tedarikciler=icerik.get("tedarikciler",[])
            veriyi_kaydet(); st.session_state.son_islem_mesaji="✅ Yüklendi"; st.rerun()