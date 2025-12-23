import sqlite3

def admin_olustur():
    baglanti = sqlite3.connect('imc_database.db')
    imlec = baglanti.cursor()
    
    try:
        # Rolü 'admin' olan özel bir kullanıcı ekliyoruz
        imlec.execute('''
            INSERT INTO kullanicilar (ad_soyad, email, sifre, rol) 
            VALUES ('Sistem Yöneticisi', 'admin@imc.com', '12345', 'admin')
        ''')
        baglanti.commit()
        print("✅ Admin Kullanıcısı Oluşturuldu!")
        print("📧 Email: admin@imc.com")
        print("🔑 Şifre: 12345")
    except sqlite3.IntegrityError:
        print("⚠️ Bu admin zaten var.")
        
    baglanti.close()

if __name__ == '__main__':
    admin_olustur()