import sqlite3
import os
import random

# Veritabanı yolunu bul
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def sahte_veri_yukle():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🌱 Veritabanı yeşillendiriliyor (Veri Ekleniyor)...")

    # 1. Örnek Esnaflar Oluştur
    esnaflar = [
        ("Lezzet Dünyası", "lezzet@imc.com", "1234", "esnaf", "doner.jpg", 39.9210, 32.8545),
        ("Kampüs Cafe", "kampus@imc.com", "1234", "esnaf", "cafe.jpg", 39.9220, 32.8550),
        ("Analı Kızlı Ev Yemekleri", "ana@imc.com", "1234", "esnaf", "corba.jpg", 39.9200, 32.8530),
        ("Pizza Kulesi", "pizza@imc.com", "1234", "esnaf", "pizza.jpg", 39.9250, 32.8500),
    ]

    esnaf_idleri = []

    for ad, email, sifre, rol, resim, lat, lng in esnaflar:
        try:
            cursor.execute("INSERT INTO kullanicilar (ad_soyad, email, sifre, rol, profil_resmi, enlem, boylam) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                           (ad, email, sifre, rol, resim, lat, lng))
            esnaf_idleri.append(cursor.lastrowid)
            print(f"✅ Esnaf Eklendi: {ad}")
        except sqlite3.IntegrityError:
            print(f"ℹ️ Esnaf zaten var: {ad}")

    # 2. Örnek Yemekler Oluştur
    yemekler = [
        ("Tavuk Döner Dürüm", 150, 70, "doner.jpg"),
        ("Mercimek Çorbası", 60, 30, "corba.jpg"),
        ("Karışık Pizza (Orta)", 250, 120, "pizza.jpg"),
        ("Hamburger Menü", 200, 100, "burger.jpg"),
        ("Kuru Fasulye & Pilav", 120, 60, "kuru.jpg"),
        ("Sütlaç", 50, 25, "tatli.jpg"),
        ("Ayran", 20, 10, "icecek.jpg"),
        ("Et Döner Porsiyon", 300, 150, "doner.jpg")
    ]

    if not esnaf_idleri:
        # Eğer esnaflar önceden ekliyse ID'lerini çekelim
        esnaf_idleri = [row[0] for row in cursor.execute("SELECT id FROM kullanicilar WHERE rol='esnaf'").fetchall()]

    for _ in range(20): # 20 tane rastgele ürün ekle
        esnaf_id = random.choice(esnaf_idleri)
        yemek_adi, eski, yeni, resim = random.choice(yemekler)
        stok = random.randint(1, 10)
        
        # Restoran adını bul
        restoran_adi = cursor.execute("SELECT ad_soyad FROM kullanicilar WHERE id=?", (esnaf_id,)).fetchone()[0]

        cursor.execute("""
            INSERT INTO urunler (esnaf_id, ad, eski_fiyat, yeni_fiyat, stok, restoran_adi, resim) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (esnaf_id, yemek_adi, eski, yeni, stok, restoran_adi, resim))

    conn.commit()
    conn.close()
    print("\n🎉 İŞLEM TAMAM! Keşfet sayfası artık dopdolu.")

if __name__ == "__main__":
    sahte_veri_yukle()