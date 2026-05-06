import streamlit as st
from datetime import datetime, timedelta
from ui import guvenli_html
from data_handler import gunluk_ciro, haftalik_ciro, aylik_ciro, gunluk_kar, bilimsel_indirim_hesapla, veriyi_kaydet
from utils import kritik_stok_whatsapp_bildirimi, tedarikciye_siparis_gonder
from config import SKT_UYARI_GUN

def goster():
    st.markdown('<div class="main-header">📊 Yönetim Paneli</div>', unsafe_allow_html=True)
    kritik_stok_whatsapp_bildirimi()
    kritik = [u for u in st.session_state.stok if u.get("min_miktar", 0) > 0 and u["miktar"] <= u["min_miktar"]]
    bugun = datetime.now().date()
    bugunku = gunluk_ciro(bugun.strftime("%Y-%m-%d"))
    dun = gunluk_ciro((bugun - timedelta(days=1)).strftime("%Y-%m-%d"))
    delta_gun = bugunku - dun
    bugunku_kar = gunluk_kar()
    bu_hafta_baslangic = bugun - timedelta(days=bugun.weekday())
    gecen_hafta_baslangic = bu_hafta_baslangic - timedelta(days=7)
    bu_hafta = haftalik_ciro(bu_hafta_baslangic)
    gecen_hafta = haftalik_ciro(gecen_hafta_baslangic)
    delta_hafta = bu_hafta - gecen_hafta
    bu_ay = aylik_ciro(bugun.year, bugun.month)
    gecen_ay_tarih = bugun.replace(day=1) - timedelta(days=1)
    gecen_ay = aylik_ciro(gecen_ay_tarih.year, gecen_ay_tarih.month)
    delta_ay = bu_ay - gecen_ay

    st.subheader("📈 Hızlı İstatistikler")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Bugünkü Ciro", f"{bugunku:,.0f} ₺", delta=f"{delta_gun:+,.0f} ₺")
    c2.metric("Bugünkü Kâr", f"{bugunku_kar:,.0f} ₺")
    c3.metric("Dünkü Ciro", f"{dun:,.0f} ₺")
    c4.metric("Bu Hafta", f"{bu_hafta:,.0f} ₺", delta=f"{delta_hafta:+,.0f} ₺")
    c5.metric("Bu Ay", f"{bu_ay:,.0f} ₺", delta=f"{delta_ay:+,.0f} ₺")
    c6.metric("Haftalık Büyüme", f"%{0 if gecen_hafta == 0 else (delta_hafta/gecen_hafta*100):.1f}")

    st.markdown("---")
    with st.expander("🪄 Stok Yenileme Sihirbazı", expanded=bool(kritik)):
        if kritik:
            st.warning(f"🚨 {len(kritik)} ürün kritik stok seviyesinde!")
            for u in kritik:
                st.write(f"📦 {u['urun_adi']} – Mevcut: {u['miktar']} {u['birim']} (Min: {u['min_miktar']} {u['birim']})")
            if st.button("⚡ Tüm Kritik Ürünleri Siparişe Ekle ve Tedarikçilere Bildir", type="primary"):
                eklenen = 0; gonderilen = 0
                for u in kritik:
                    if not any(f["urun_adi"] == u["urun_adi"] and f["durum"] == "Bekliyor" for f in st.session_state.fire):
                        st.session_state.fire.append({
                            "urun_adi": u["urun_adi"], "miktar": u["min_miktar"] - u["miktar"] + 5,
                            "birim": u["birim"], "aciliyet": "🔥 Yüksek", "tedarikci": u.get("tedarikci", ""),
                            "durum": "Bekliyor", "eklenme_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }); eklenen += 1
                    tedarikci_eposta = next((t.get("eposta", "") for t in st.session_state.tedarikciler if t["ad"] == u.get("tedarikci", "")), "")
                    if tedarikci_eposta:
                        urun_dict = u.copy(); urun_dict["miktar"] = u["miktar"]; urun_dict["min_miktar"] = u.get("min_miktar", 10)
                        if tedarikciye_siparis_gonder(urun_dict, tedarikci_eposta): gonderilen += 1
                veriyi_kaydet()
                st.session_state.son_islem_mesaji = f"✅ {eklenen} ürün eklendi, {gonderilen} e‑posta gönderildi"
                st.rerun()
        else:
            st.success("✅ Tüm ürünler minimum stok seviyesinin üzerinde.")

    if kritik:
        st.markdown('<div class="sticky-alert">⚠️ KRİTİK STOK UYARISI</div>', unsafe_allow_html=True)
    skt = []
    for u in st.session_state.stok:
        s = u.get("son_kullanma_tarihi", "")
        if s:
            try:
                k = (datetime.strptime(s, "%Y-%m-%d").date() - bugun).days
                if 0 <= k <= SKT_UYARI_GUN: skt.append({**u, "kalan": k})
            except: pass
    if kritik:
        st.subheader("🚨 Kritik Stoklar")
        for u in kritik[:5]: st.error(f"{guvenli_html(u['urun_adi'])}: {u['miktar']:.2f} {u['birim']}")
        st.balloons()
    if skt:
        st.subheader("⏰ Yaklaşan SKT (Bilimsel İndirim)")
        for u in skt[:5]:
            oneri = bilimsel_indirim_hesapla(u, u['kalan'])
            st.warning(f"{guvenli_html(u['urun_adi'])}: {u['kalan']} gün → Önerilen İndirim: %{oneri}")