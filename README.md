# 🏪 Market Yönetim Sistemi (Akıllı Stok Asistanı)

> **Barkod okut, satış yap, israfı bitir.**  
> Küçük işletmeler için geliştirilmiş, yapay zeka destekli stok ve satış takip platformu.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP%20Demo-orange?style=for-the-badge)]()

<p align="center">
  <img src="demo.gif" alt="Demo" width="600"/>
</p>

---

## 🚀 Neden Bu Uygulama?

Diğer stok programlarında **olmayan** özellikler sunar:

- 📅 **Son Kullanma Tarihi (SKT) Takibi:** Rakiplerde yok. SKT'si yaklaşan ürünleri listelemekle kalmaz, **bilimsel veriyle % kaç indirim yapmanız gerektiğini söyler.**
- 📱 **Mobil Barkod Okutma:** Telefon kamerasıyla anında stok girişi/çıkışı. **USB barkod okuyucuya gerek yok.**
- 🧠 **Fire (İsraf) Analizi:** Hangi kategoride ne kadar kayıp var? Pasta grafiğiyle görün, siparişlerinizi optimize edin.
- 🛒 **POS Satış Ekranı:** Sepet mantığı, ödeme kanalı seçimi ve **anında PDF fiş** indirme.
- 💰 **Günlük / Aylık Kâr Raporu:** Satış ve maliyet verileriyle **net kârınızı** anlık görün.
- 🔐 **Rol Tabanlı Yetkilendirme:** Patron, kasiyer ve depocu aynı anda farklı yetkilerle çalışabilir.

---

## ✨ Özellikler

### 📦 Stok Yönetimi
- Manuel veya barkodla stok girişi/çıkışı
- SKT’li / SKT’siz ürün desteği (kalem, defter gibi)
- Toplu CSV ile stok güncelleme
- Mobil uyumlu stok sayım ekranı (barkod eşleştirmeli)

### 📱 Akıllı Barkod
- USB barkod okuyucu veya **telefon kamerası** ile okutma
- Yeni barkodları otomatik öğrenme ve veritabanına kaydetme
- Stok giriş/çıkış işlemlerini tek adımda tamamlama

### 💵 Satış (POS)
- Manuel ürün seçimi veya **hızlı POS modu** (barkod okutur okutmaz satış)
- En çok satan 5 ürüne tek tıkla satış butonu
- **Ödeme kanalı seçimi:** Nakit, Kredi Kartı, Havale/EFT, Yemek Kartı
- Satış sonrası **PDF fiş** indirme

### ⏰ SKT ve İndirim Önerisi
- Son kullanma tarihi yaklaşan ürünleri otomatik listeleme
- **Bilimsel indirim hesaplama:** Satış hızı, stok fazlası ve kar marjına göre dinamik yüzde önerisi

### 📊 Raporlama ve Analiz
- **Kâr marjı raporu:** Ürün bazında alış/satış/kâr analizi
- **Stok devir hızı:** Hangi ürün ne kadar hızlı tükeniyor?
- **Fire (israf) analizi:** Kategori bazlı kayıp pasta grafiği
- **Satış raporu:** Günlük, aylık, ürün bazlı ciro dökümü
- **Aktivite logu:** Tüm kullanıcı hareketlerinin zaman damgalı kaydı
- **Günlük kasa kapanışı:** Gelir/gider ve ödeme kanallarına göre dağılım, PDF rapor

### 🔔 Bildirimler
- Kritik stokta **e‑posta** ve **WhatsApp** (opsiyonel) uyarısı
- Günlük kasa raporunu patrona otomatik e‑posta ile gönderme
- Tedarikçiye otomatik sipariş e‑postası

### 🔐 Güvenlik
- Rol tabanlı yetkilendirme (patron, kasiyer, depocu)
- Oturum zaman aşımı (30 dk işlem yapılmazsa otomatik çıkış)
- Şifre sıfırlama arayüzü
- Kullanıcı yönetimi (patron yeni kullanıcı ekleyebilir)

### 🎨 Kullanıcı Deneyimi
- **Koyu / Aydınlık tema** desteği
- Mobil uyumlu responsive tasarım
- Modern gradient butonlar ve kart tasarımı

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)

### Adımlar

1. **Depoyu klonlayın:**
   ```bash
   git clone https://github.com/ugurronderkarapunar/deneme_local.git
   cd deneme_local
   🔑 Demo Giriş Bilgileri
Kullanıcı Adı	Şifre	Rol
admin	1234	Patron (tüm yetkiler)
Not: Bu bilgileri canlı ortamda kullanmayın. .streamlit/secrets.toml dosyası ile özelleştirin.

📁 Proje Yapısı (Modüler)
text
deneme_local/
├── app.py                 # Ana giriş, sayfa yönlendirme
├── config.py              # Konfigürasyon ve sabitler
├── data_handler.py        # JSON veri işlemleri, mock veriler
├── utils.py               # Yardımcı fonksiyonlar (e‑posta, PDF, WhatsApp)
├── ui.py                  # CSS tema ve arayüz bileşenleri
├── auth.py                # Oturum yönetimi ve yetkilendirme
├── page_modules/          # Sayfa modülleri
│   ├── dashboard.py       # Ana panel
│   ├── barkod.py          # Barkod okutma
│   ├── stok.py            # Stok yönetimi
│   ├── satis.py           # Satış (POS)
│   ├── siparis.py         # Sipariş panosu
│   └── diger.py           # Tedarikçi, raporlar, ayarlar, yedekleme
├── requirements.txt       # Bağımlılıklar
└── README.md
📦 Bağımlılıklar
streamlit – Web arayüzü

pandas – Veri işleme

plotly – Grafikler ve görselleştirme

openpyxl – Excel dışa aktarım

fpdf2 – PDF fiş ve rapor oluşturma

📄 Lisans
MIT License – bkz. LICENSE dosyası.


