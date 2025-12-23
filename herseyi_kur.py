import sqlite3
import os
import random

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def sistemi_kur():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"Hedef Veritabanı: {DB_PATH}")
    
    # 1. TEMİZLİK
    print("🧹 Eski tablolar temizleniyor...")
    tablolar = ["siparisler", "yorumlar", "favoriler", "urunler", "kullanicilar"]
    for tablo in tablolar:
        cursor.execute(f"DROP TABLE IF EXISTS {tablo}")

    # 2. KURULUM
    print("🏗️ Tablolar yeniden inşa ediliyor...")
    
    cursor.execute("""
        CREATE TABLE kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            rol TEXT NOT NULL,
            profil_resmi TEXT DEFAULT 'default.png',
            enlem REAL,
            boylam REAL
        );
    """)

    cursor.execute("""
        CREATE TABLE urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            esnaf_id INTEGER NOT NULL,
            ad TEXT NOT NULL,
            eski_fiyat REAL,
            yeni_fiyat REAL NOT NULL,
            stok INTEGER NOT NULL,
            restoran_adi TEXT,
            resim TEXT DEFAULT 'default_food.png',
            FOREIGN KEY (esnaf_id) REFERENCES kullanicilar (id)
        );
    """)

    cursor.execute("""
        CREATE TABLE siparisler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siparis_kodu TEXT, 
            urun_id INTEGER NOT NULL,
            musteri_id INTEGER NOT NULL,
            esnaf_id INTEGER NOT NULL,
            ogrenci_id INTEGER,
            tarih TEXT DEFAULT CURRENT_TIMESTAMP,
            fiyat REAL,
            durum TEXT DEFAULT 'Hazırlanıyor',
            FOREIGN KEY (urun_id) REFERENCES urunler (id),
            FOREIGN KEY (musteri_id) REFERENCES kullanicilar (id)
        );
    """)

    cursor.execute("""
        CREATE TABLE favoriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER NOT NULL,
            urun_id INTEGER NOT NULL,
            FOREIGN KEY (ogrenci_id) REFERENCES kullanicilar (id),
            FOREIGN KEY (urun_id) REFERENCES urunler (id)
        );
    """)

    cursor.execute("""
        CREATE TABLE yorumlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siparis_id INTEGER NOT NULL,
            esnaf_id INTEGER NOT NULL,
            ogrenci_id INTEGER NOT NULL,
            puan INTEGER,
            yorum_metni TEXT,
            tarih TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (siparis_id) REFERENCES siparisler (id)
        );
    """)

    # 3. VERİ GİRİŞİ
    print("🌱 İçerikler (Esnaflar ve Yemekler) ekleniyor...")
    
    esnaflar = [
        ("Lezzet Dünyası", "lezzet@imc.com", "1234", "esnaf", 39.9210, 32.8545),
        ("Kampüs Cafe", "kampus@imc.com", "1234", "esnaf", 39.9220, 32.8550),
        ("Analı Kızlı", "ana@imc.com", "1234", "esnaf", 39.9200, 32.8530),
        ("Fırıncı Baba", "firin@imc.com", "1234", "esnaf", 39.9250, 32.8500),
    ]

    esnaf_idlari = []
    for ad, email, sifre, rol, lat, lng in esnaflar:
        cursor.execute("INSERT INTO kullanicilar (ad_soyad, email, sifre, rol, profil_resmi, enlem, boylam) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (ad, email, sifre, rol, 'default.png', lat, lng))
        esnaf_idlari.append(cursor.lastrowid)

    # --- BURASI GÜNCELLENDİ: Ekmek eklendi ---
    yemekler = [
        ("Ekmek Arası Tavuk Döner", 150, 70, "doner.jpg"),
        ("Mercimek Çorbası", 60, 30, "corba.jpg"),
        ("Karışık Pizza", 250, 120, "pizza.jpg"),
        ("Hamburger", 200, 100, "burger.jpg"),
        ("Dilimlenmiş Ekmek", 25, 15, "ekmek.jpg"), # <--- YENİ
        ("Künefe", 50, 25, "tatli.jpg")
    ]

    for _ in range(25): 
        esnaf_id = random.choice(esnaf_idlari)
        # Listeden rastgele seçiyoruz (isim, eski, yeni, RESİM)
        yemek_adi, eski, yeni, resim_dosyasi = random.choice(yemekler)
        restoran_adi = cursor.execute("SELECT ad_soyad FROM kullanicilar WHERE id=?", (esnaf_id,)).fetchone()[0]
        
        cursor.execute("""
            INSERT INTO urunler (esnaf_id, ad, eski_fiyat, yeni_fiyat, stok, restoran_adi, resim) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (esnaf_id, yemek_adi, eski, yeni, random.randint(1, 10), restoran_adi, resim_dosyasi))

    conn.commit()
    conn.close()
    print("\n✅ SİSTEM TAMAMEN KURULDU! 'ekmek.jpg' dosyası kullanıldı.")

if __name__ == "__main__":
    sistemi_kur()