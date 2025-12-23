import sqlite3

def veritabanini_onar():
    try:
        # Veritabanına bağlan
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        print("Veritabanı onarımı başlatılıyor...")

        # 1. ogrenci_id Sütununu Ekle
        try:
            cursor.execute("ALTER TABLE siparisler ADD COLUMN ogrenci_id INTEGER;")
            print("✅ 'ogrenci_id' sütunu başarıyla eklendi.")
        except sqlite3.OperationalError:
            print("ℹ️ 'ogrenci_id' sütunu zaten mevcut.")

        # 2. fiyat Sütununu Ekle (Garanti olsun diye)
        try:
            cursor.execute("ALTER TABLE siparisler ADD COLUMN fiyat REAL;")
            print("✅ 'fiyat' sütunu başarıyla eklendi.")
        except sqlite3.OperationalError:
            print("ℹ️ 'fiyat' sütunu zaten mevcut.")

        # 3. durum Sütununu Ekle
        try:
            cursor.execute("ALTER TABLE siparisler ADD COLUMN durum TEXT DEFAULT 'Hazırlanıyor';")
            print("✅ 'durum' sütunu başarıyla eklendi.")
        except sqlite3.OperationalError:
            print("ℹ️ 'durum' sütunu zaten mevcut.")

        conn.commit()
        conn.close()
        print("\n🎉 İşlem tamamlandı! Artık 'python app.py' ile projeyi başlatabilirsin.")

    except Exception as e:
        print(f"❌ Bir hata oluştu: {e}")

if __name__ == "__main__":
    veritabanini_onar()