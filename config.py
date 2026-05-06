import json
import os

CONFIG_DOSYASI = "config.json"
VARSAYILAN_CONFIG = {
    "kullanici_adi": "admin",
    "sifre": "1234",
    "oturum_suresi_dk": 30,
    "skt_uyari_gun": 3,
    "kategoriler": ["Kuru Gıda", "Süt Ürünleri", "İçecek", "Temizlik", "Diğer", "Et & Şarküteri", "Dondurulmuş", "Fırın"],
    "birimler": ["kg", "litre", "adet", "paket", "gram", "koli", "kutu", "şişe", "çuval"],
    "roller": {
        "patron": ["tümü"],
        "kasiyer": ["barkod", "satis"],
        "depocu": ["barkod", "stok", "stok_ekle", "skt_takip"]
    },
    "dosya_yollari": {
        "stok": "stok.json",
        "fire": "fire.json",
        "hareket": "hareket.json",
        "barkod_db": "barkod_db.json",
        "tedarikciler": "tedarikciler.json",
        "kullanicilar": "kullanicilar.json",
        "satislar": "satislar.json"
    }
}

def load_config() -> dict:
    if os.path.exists(CONFIG_DOSYASI):
        try:
            with open(CONFIG_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return VARSAYILAN_CONFIG

config = load_config()
STOK_DOSYASI = config["dosya_yollari"].get("stok", "stok.json")
FIRE_DOSYASI = config["dosya_yollari"].get("fire", "fire.json")
HAREKET_DOSYASI = config["dosya_yollari"].get("hareket", "hareket.json")
BARKOD_DB_DOSYASI = config["dosya_yollari"].get("barkod_db", "barkod_db.json")
TEDARIKCI_DOSYASI = config["dosya_yollari"].get("tedarikciler", "tedarikciler.json")
KULLANICI_DOSYASI = config["dosya_yollari"].get("kullanicilar", "kullanicilar.json")
SATIS_DOSYASI = config["dosya_yollari"].get("satislar", "satislar.json")
KATEGORILER = config.get("kategoriler", ["Kuru Gıda", "Süt Ürünleri", "İçecek", "Temizlik", "Diğer"])
BIRIMLER = config.get("birimler", ["kg", "litre", "adet", "paket", "gram", "koli", "kutu", "şişe", "çuval"])
ROLLER = config.get("roller", {"patron": ["tümü"], "kasiyer": ["barkod", "satis"], "depocu": ["barkod", "stok"]})
OTURUM_SURESI = config.get("oturum_suresi_dk", 30)
SKT_UYARI_GUN = config.get("skt_uyari_gun", 3)