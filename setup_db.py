import sqlite3
import os

# Veritabanı yolunu bul
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def veritabanini_kur():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Hedef Veritabanı: {DB_PATH}")
    print("Tablolar oluşturuluyor...")

    # 1. KULLANICILAR Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            rol TEXT NOT NULL, -- 'ogrenci' veya 'esnaf'
            profil_resmi TEXT,
            enlem REAL,
            boylam REAL
        );
    """)

    # 2. ÜRÜNLER Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urunler (
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

    # 3. SİPARİŞLER Tablosu (Zaten varsa dokunmaz)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS siparisler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siparis_kodu TEXT,
            urun_id INTEGER NOT NULL,
            musteri_id INTEGER NOT NULL, -- Bu eski isim kalabilir, sorun değil
            esnaf_id INTEGER NOT NULL,
            ogrenci_id INTEGER, -- Yeni eklediğimiz
            tarih TEXT DEFAULT CURRENT_TIMESTAMP,
            fiyat REAL,
            durum TEXT DEFAULT 'Hazırlanıyor',
            FOREIGN KEY (urun_id) REFERENCES urunler (id),
            FOREIGN KEY (musteri_id) REFERENCES kullanicilar (id)
        );
    """)

    # 4. FAVORİLER Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favoriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER NOT NULL,
            urun_id INTEGER NOT NULL,
            FOREIGN KEY (ogrenci_id) REFERENCES kullanicilar (id),
            FOREIGN KEY (urun_id) REFERENCES urunler (id)
        );
    """)

    # 5. YORUMLAR Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yorumlar (
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

    conn.commit()
    conn.close()
    print("\n✅ TÜM TABLOLAR BAŞARIYLA OLUŞTURULDU!")
    print("Artık uygulamayı çalıştırabilirsin.")

if __name__ == "__main__":
    veritabanini_kur()