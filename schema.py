import sqlite3

def veritabani_kur():
    baglanti = sqlite3.connect('imc_database.db')
    imlec = baglanti.cursor()

    # 1. Kullanıcılar
    imlec.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad_soyad TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            sifre TEXT NOT NULL,
            rol TEXT NOT NULL,
            enlem REAL,
            boylam REAL,
            profil_resmi TEXT DEFAULT 'default.png',
            telefon TEXT,
            acilis_saati TEXT,
            kapanis_saati TEXT,
            adres_tarifi TEXT,
            diyet_tercihi TEXT DEFAULT 'Yok'
        )
    ''')

    # 2. Ürünler
    imlec.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            esnaf_id INTEGER,
            ad TEXT NOT NULL,
            eski_fiyat REAL,
            yeni_fiyat REAL,
            stok INTEGER,
            restoran_adi TEXT,
            FOREIGN KEY(esnaf_id) REFERENCES kullanicilar(id)
        )
    ''')

    # 3. Siparişler
    imlec.execute('''
        CREATE TABLE IF NOT EXISTS siparisler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siparis_kodu TEXT UNIQUE NOT NULL,
            urun_id INTEGER,
            musteri_id INTEGER,
            esnaf_id INTEGER, 
            durum TEXT DEFAULT 'Bekliyor',
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. Yorumlar
    imlec.execute('''
        CREATE TABLE IF NOT EXISTS yorumlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siparis_id INTEGER,
            esnaf_id INTEGER,
            ogrenci_id INTEGER,
            puan INTEGER,
            yorum_metni TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. FAVORİLER (YENİ TABLO)
    imlec.execute('''
        CREATE TABLE IF NOT EXISTS favoriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ogrenci_id INTEGER,
            urun_id INTEGER,
            FOREIGN KEY(ogrenci_id) REFERENCES kullanicilar(id),
            FOREIGN KEY(urun_id) REFERENCES urunler(id)
        )
    ''')
    
    baglanti.commit()
    baglanti.close()
    print("✅ Veritabanı FULL ÖZELLİK (Favoriler Dahil) kuruldu!")

if __name__ == '__main__':
    veritabani_kur()