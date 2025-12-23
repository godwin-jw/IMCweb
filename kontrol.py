import sqlite3
import os

# Veritabanı yolunu garanti altına alıyoruz
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

print(f"Hedef Veritabanı: {DB_PATH}")

def tabloyu_sifirla():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("1. Eski 'siparisler' tablosu siliniyor...")
        cursor.execute("DROP TABLE IF EXISTS siparisler;") 

        print("2. Yeni 'siparisler' tablosu oluşturuluyor...")
        # Tabloyu tüm eksik sütunlarla (ogrenci_id, fiyat, durum) sıfırdan kuruyoruz
        cursor.execute("""
            CREATE TABLE siparisler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_id INTEGER NOT NULL,
                ogrenci_id INTEGER NOT NULL,
                tarih TEXT DEFAULT CURRENT_TIMESTAMP,
                fiyat REAL,
                durum TEXT DEFAULT 'Hazırlanıyor',
                FOREIGN KEY (urun_id) REFERENCES urunler (id),
                FOREIGN KEY (ogrenci_id) REFERENCES kullanicilar (id)
            );
        """)

        conn.commit()
        conn.close()
        print("\n✅ TABLO SIFIRLANDI VE YENİDEN OLUŞTURULDU.")
        print("Artık bu hatayı alman imkansız.")

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    tabloyu_sifirla()