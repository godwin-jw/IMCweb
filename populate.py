import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('tr_TR') # Türkçe isimler üret

# Eskişehir Merkez Koordinatları (Bağlar/Adalar civarı)
MERKEZ_LAT = 39.7767
MERKEZ_LNG = 30.5206

def baglanti_kur():
    return sqlite3.connect('imc_database.db')

def koordinat_uret():
    # Merkezin etrafında 1-2 km dağıt
    lat = MERKEZ_LAT + random.uniform(-0.015, 0.015)
    lng = MERKEZ_LNG + random.uniform(-0.015, 0.015)
    return lat, lng

def temizle():
    conn = baglanti_kur()
    print("🧹 Eski veriler temizleniyor...")
    # Sadece sahte verileri silmek zor olduğu için her şeyi sıfırlayıp baştan kuruyoruz
    # (Admin ve senin hesabın kalacaksa burayı düzenleyebilirsin ama temiz kurulum iyidir)
    tables = ['siparisler', 'yorumlar', 'favoriler', 'urunler', 'kullanicilar']
    for table in tables:
        conn.execute(f"DELETE FROM {table}")
        conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'") # ID'leri sıfırla
    conn.commit()
    conn.close()

def veri_bas():
    conn = baglanti_kur()
    print("🤖 Yapay Zeka verileri üretiyor...")

    # 1. SENİN HESABIN (Admin & Esnaf) - Sunumda kullanman için
    conn.execute('''INSERT INTO kullanicilar (ad_soyad, email, sifre, rol, enlem, boylam, profil_resmi) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                    ("Patron", "admin@imc.com", "123", "esnaf", MERKEZ_LAT, MERKEZ_LNG, "default.png"))
    
    # 2. ESNAFLAR OLUŞTUR (20 Adet)
    esnaf_ids = []
    restoran_turleri = ["Dönerci", "Burger", "Pizza", "Ev Yemekleri", "Pastane", "Çiğköfte", "Kafe"]
    
    for _ in range(20):
        ad = fake.name()
        dukkan = f"{fake.last_name()} {random.choice(restoran_turleri)}"
        lat, lng = koordinat_uret()
        
        cursor = conn.execute('''INSERT INTO kullanicilar (ad_soyad, email, sifre, rol, enlem, boylam) 
                        VALUES (?, ?, ?, ?, ?, ?)''', 
                        (dukkan, fake.email(), "123", "esnaf", lat, lng))
        esnaf_ids.append(cursor.lastrowid)
    
    print(f"✅ 20 Esnaf Eskişehir haritasına yerleştirildi.")

    # 3. ÖĞRENCİLER OLUŞTUR (30 Adet)
    ogrenci_ids = []
    for _ in range(30):
        lat, lng = koordinat_uret()
        cursor = conn.execute('''INSERT INTO kullanicilar (ad_soyad, email, sifre, rol, enlem, boylam) 
                        VALUES (?, ?, ?, ?, ?, ?)''', 
                        (fake.name(), fake.email(), "123", "ogrenci", lat, lng))
        ogrenci_ids.append(cursor.lastrowid)
        
    print(f"✅ 30 Öğrenci sisteme kayıt oldu.")

    # 4. ÜRÜNLER OLUŞTUR (Her esnafa 3-5 ürün)
    yemekler = [
        ("Tavuk Döner Dürüm", 70, 45), ("Karışık Pizza", 150, 90), ("Mercimek Çorbası", 40, 25),
        ("Adana Kebap", 180, 120), ("Hamburger Menü", 130, 85), ("Soğuk Baklava", 200, 140),
        ("Çiğköfte Dürüm", 50, 30), ("Kruvasan", 60, 35), ("Filtre Kahve", 40, 20),
        ("San Sebastian Cheesecake", 120, 80), ("Lahmacun", 50, 35), ("Pilav Üstü Tavuk", 70, 50)
    ]
    
    urun_ids = []
    for esnaf_id in esnaf_ids:
        for _ in range(random.randint(3, 6)): # Her esnafın 3-6 ürünü olsun
            yemek = random.choice(yemekler)
            ad = yemek[0]
            eski = yemek[1] + random.randint(-10, 20)
            yeni = yemek[2] + random.randint(-5, 10)
            stok = random.randint(1, 10)
            
            # Esnaf adını çek
            esnaf_adi = conn.execute("SELECT ad_soyad FROM kullanicilar WHERE id=?", (esnaf_id,)).fetchone()[0]
            
            cursor = conn.execute('''INSERT INTO urunler (esnaf_id, ad, eski_fiyat, yeni_fiyat, stok, restoran_adi) 
                            VALUES (?, ?, ?, ?, ?, ?)''', 
                            (esnaf_id, ad, eski, yeni, stok, esnaf_adi))
            urun_ids.append(cursor.lastrowid)

    print(f"✅ 100+ Ürün vitrine dizildi (Stoklar ve İndirimler ayarlandı).")

    # 5. SİPARİŞLER VE YORUMLAR (Geçmiş Verisi)
    # Analiz grafiklerinin dolu görünmesi için
    yorum_metinleri = [
        "Harikaydı, çok sıcak geldi.", "Fiyat performans ürünü.", "Biraz soğuktu ama tadı güzel.",
        "Öğrenci dostu mekan!", "Ellerinize sağlık.", "Porsiyon biraz küçüktü.", "Bayıldım, favorim oldu."
    ]
    
    for _ in range(150): # 150 tane geçmiş sipariş üret
        urun_id = random.choice(urun_ids)
        musteri_id = random.choice(ogrenci_ids)
        
        # Ürün sahibini bul
        esnaf_id = conn.execute("SELECT esnaf_id FROM urunler WHERE id=?", (urun_id,)).fetchone()[0]
        
        # Siparişi oluştur (Durumu 'Teslim Edildi' yap ki grafiklere yansısın)
        kod = f"IMC-{random.randint(1000,9999)}"
        cursor = conn.execute('''INSERT INTO siparisler (siparis_kodu, urun_id, musteri_id, esnaf_id, durum) 
                         VALUES (?, ?, ?, ?, ?)''', 
                         (kod, urun_id, musteri_id, esnaf_id, 'Teslim Edildi'))
        
        siparis_id = cursor.lastrowid
        
        # %60 ihtimalle yorum yapılsın
        if random.random() > 0.4:
            puan = random.randint(3, 5)
            yorum = random.choice(yorum_metinleri)
            conn.execute('''INSERT INTO yorumlar (siparis_id, esnaf_id, ogrenci_id, puan, yorum_metni) 
                            VALUES (?, ?, ?, ?, ?)''', 
                            (siparis_id, esnaf_id, musteri_id, puan, yorum))

    conn.commit()
    conn.close()
    print("🚀 SİMÜLASYON TAMAMLANDI! SİTE KULLANIMA HAZIR.")
    print("------------------------------------------------")
    print("🔑 Giriş Bilgileri (Senin İçin):")
    print("Email: admin@imc.com")
    print("Şifre: 123")

if __name__ == '__main__':
    temizle()
    veri_bas()