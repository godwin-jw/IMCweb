from itsdangerous import URLSafeTimedSerializer
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import sqlite3
import random
import math
import uuid
from datetime import timedelta

app = Flask(__name__)

# --- AYARLAR ---
app.config['SECRET_KEY'] = 'imc_proje_cok_gizli_anahtar'
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
app.secret_key = 'imc_proje_cok_gizli_anahtar'
app.permanent_session_lifetime = timedelta(days=7)

app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Resim Yükleme Klasörü
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    try: os.makedirs(UPLOAD_FOLDER)
    except: pass

# Veritabanı Yolu
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- MERKEZİ GÜNCELLEME SİSTEMİ ---
@app.before_request
def kullanici_bilgilerini_tazele():
    # Sadece statik dosyalar (resim, css vb.) hariç çalışsın, performansı yormasın
    if request.endpoint and 'static' in request.endpoint:
        return

    if 'user_id' in session:
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT ad_soyad, profil_resmi, rol FROM kullanicilar WHERE id = ?', (session['user_id'],)).fetchone()
            conn.close()
            
            if user:
                # Kullanıcı bulundu, bilgileri tazele
                resim = user['profil_resmi']
                if not resim or resim == 'None': resim = 'default.png'
                
                session['foto'] = resim
                session['ad_soyad'] = user['ad_soyad']
                session['rol'] = user['rol']
            else:
                # KRİTİK DÜZELTME:
                # Session'da ID var ama veritabanında kullanıcı yok!
                # Bu durumda oturumu temizle ki sonsuz döngüye girmesin.
                session.clear()
                
        except Exception as e:
            # Hata olursa sessiz kalma, konsola yaz ki görelim
            print(f"Session tazeleme hatası: {e}")
            # Veritabanı hatası varsa güvenli tarafta kalıp çıkış yaptıralım
            # session.clear()

# --- YARDIMCI FONKSİYONLAR ---
def mesafe_hesapla(lat1, lon1, lat2, lon2):
    if not lat1 or not lat2 or not lon1 or not lon2: return 999.9
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        R = 6371 
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return round(R * c, 1)
    except: return 999.9

# --- GELİŞMİŞ ROZET SİSTEMİ (GÜNCELLENDİ) ---
def rozet_bilgisi_al(user_id):
    conn = get_db_connection()
    try:
        # Sadece "Teslim Edildi" olan siparişleri say
        row = conn.execute("SELECT COUNT(*) FROM siparisler WHERE musteri_id = ? AND durum = 'Teslim Edildi'", (user_id,)).fetchone()
        sayi = row[0] if row else 0
    except:
        sayi = 0
    conn.close()
    
    # Rozet Hedefleri
    if sayi >= 50:
        return {"isim": "Doğa Dostu Efsane 🌳", "renk": "success", "sayi": sayi, "hedef": 50, "yuzde": 100, "sonraki": "Maksimum Seviye"}
    elif sayi >= 20:
        return {"isim": "Gıda Kahramanı 🦸", "renk": "primary", "sayi": sayi, "hedef": 50, "yuzde": int((sayi/50)*100), "sonraki": "Doğa Dostu Efsane"}
    elif sayi >= 5:
        return {"isim": "Kurtarıcı 🍞", "renk": "info", "sayi": sayi, "hedef": 20, "yuzde": int((sayi/20)*100), "sonraki": "Gıda Kahramanı"}
    else:
        return {"isim": "Acemi Kurtarıcı 👶", "renk": "secondary", "sayi": sayi, "hedef": 5, "yuzde": int((sayi/5)*100), "sonraki": "Kurtarıcı"}

# --- ROTALAR ---

@app.route('/')
def ana_sayfa():
    if 'user_id' in session:
        return redirect(url_for('esnaf_paneli') if session['rol'] == 'esnaf' else url_for('ogrenci_paneli'))
    return redirect(url_for('giris_yap'))

@app.route('/giris', methods=['GET', 'POST'])
def giris_yap():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        sifre = request.form.get('sifre', '').strip()
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM kullanicilar WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and str(user['sifre']).strip() == str(sifre):
            session.permanent = True
            session['user_id'] = user['id']
            # Diğer bilgiler before_request ile otomatik dolacak
            return redirect(url_for('esnaf_paneli') if user['rol'] == 'esnaf' else url_for('ogrenci_paneli'))
        else:
            flash('Hatalı e-posta veya şifre.', 'danger')
            
    return render_template('login.html')

@app.route('/kayit', methods=['POST'])
def kayit_ol():
    ad = request.form['ad_soyad']
    email = request.form['email']
    sifre = request.form['sifre']
    rol = request.form['rol']
    enlem = request.form.get('enlem') or 39.7767
    boylam = request.form.get('boylam') or 30.5206
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO kullanicilar (ad_soyad, email, sifre, rol, enlem, boylam, profil_resmi) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (ad, email, sifre, rol, enlem, boylam, 'default.png'))
        conn.commit()
        flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
    except sqlite3.IntegrityError:
        flash('Bu e-posta zaten kullanımda.', 'warning')
    conn.close()
    return redirect(url_for('giris_yap'))

@app.route('/cikis')
def cikis_yap():
    session.clear()
    return redirect(url_for('giris_yap'))

@app.route('/ogrenci')
def ogrenci_paneli():
    if 'user_id' not in session: return redirect(url_for('giris_yap'))
    
    conn = get_db_connection()
    
    arama_terimi = request.args.get('q', '')
    min_fiyat = request.args.get('min_fiyat', 0, type=int)
    max_fiyat = request.args.get('max_fiyat', 5000, type=int)
    siralama = request.args.get('siralama', 'varsayilan')
    sadece_stok = request.args.get('sadece_stok')

    sql_query = '''
        SELECT u.*, k.ad_soyad as restoran_adi, k.enlem, k.boylam 
        FROM urunler u 
        JOIN kullanicilar k ON u.esnaf_id = k.id
        WHERE u.yeni_fiyat BETWEEN ? AND ?
    '''
    params = [min_fiyat, max_fiyat]

    if arama_terimi:
        sql_query += " AND (u.ad LIKE ? OR k.ad_soyad LIKE ?)"
        params.extend([f'%{arama_terimi}%', f'%{arama_terimi}%'])
    
    if sadece_stok:
        sql_query += " AND u.stok > 0"

    urunler_db = conn.execute(sql_query, params).fetchall()
    
    urun_listesi = []
    ogr_lat = session.get('lat', 39.9208)
    ogr_lng = session.get('lng', 32.8541)

    for row in urunler_db:
        u = dict(row)
        dist = ((u['enlem'] - ogr_lat)**2 + (u['boylam'] - ogr_lng)**2)**0.5 * 100 
        u['mesafe'] = round(dist, 1)

        if u['eski_fiyat'] and u['eski_fiyat'] > u['yeni_fiyat']:
            u['indirim_orani'] = int(((u['eski_fiyat'] - u['yeni_fiyat']) / u['eski_fiyat']) * 100)
        else:
            u['indirim_orani'] = 0
        
        fav_check = conn.execute("SELECT 1 FROM favoriler WHERE urun_id=? AND ogrenci_id=?", (u['id'], session['user_id'])).fetchone()
        u['favori_mi'] = True if fav_check else False
        
        if not u.get('resim'): u['resim'] = 'default_food.png'
        urun_listesi.append(u)

    conn.close()

    if siralama == 'fiyat_artan':
        urun_listesi.sort(key=lambda x: x['yeni_fiyat'])
    elif siralama == 'fiyat_azalan':
        urun_listesi.sort(key=lambda x: x['yeni_fiyat'], reverse=True)
    elif siralama == 'mesafe':
        urun_listesi.sort(key=lambda x: x['mesafe'])
    elif siralama == 'indirim':
        urun_listesi.sort(key=lambda x: x['indirim_orani'], reverse=True)
    
    # ROZET BİLGİSİNİ AL (Sadece isim ve renk)
    rozet_data = rozet_bilgisi_al(session['user_id'])

    return render_template('student.html', 
                           urunler=urun_listesi, 
                           kullanici=session.get('ad_soyad'), 
                           rozet=rozet_data['isim'],
                           rozet_renk=rozet_data['renk'],
                           arama_terimi=arama_terimi,
                           sayfa_tipi='kesfet',
                           secili_filtreler={
                               'min': min_fiyat,
                               'max': max_fiyat,
                               'sort': siralama,
                               'stok': sadece_stok
                           })

@app.route('/harita')
def harita_gorunumu():
    if 'user_id' not in session: return redirect(url_for('giris_yap'))
    
    rozet_data = rozet_bilgisi_al(session['user_id'])
    
    return render_template('map_view.html', 
                           kullanici=session.get('ad_soyad'), 
                           rozet=rozet_data['isim'], 
                           rozet_renk=rozet_data['renk'],
                           enlem=session.get('lat', 39.9208), 
                           boylam=session.get('lng', 32.8541))

@app.route('/satin-al', methods=['POST'])
def satin_al():
    urun_id = request.form['urun_id']
    conn = get_db_connection()
    urun = conn.execute('SELECT * FROM urunler WHERE id = ?', (urun_id,)).fetchone()
    if urun and urun['stok'] > 0:
        conn.execute('UPDATE urunler SET stok = stok - 1 WHERE id = ?', (urun_id,))
        kod = f"IMC-{random.randint(1000,9999)}"
        conn.execute('INSERT INTO siparisler (siparis_kodu, urun_id, musteri_id, esnaf_id, ogrenci_id, fiyat, durum) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (kod, urun_id, session['user_id'], urun['esnaf_id'], session['user_id'], urun['yeni_fiyat'], 'Hazırlanıyor'))
        conn.commit()
        flash(f"Kodunuz: #{kod}", "success")
    else:
        flash("Stok bitti!", "danger")
    conn.close()
    return redirect(url_for('ogrenci_paneli'))

@app.route('/favorilerim')
def favorilerim():
    if 'user_id' not in session: return redirect(url_for('giris_yap'))
    conn = get_db_connection()
    
    favoriler = conn.execute('''
        SELECT u.*, k.ad_soyad as restoran_adi, k.enlem, k.boylam 
        FROM urunler u
        JOIN favoriler f ON u.id = f.urun_id
        JOIN kullanicilar k ON u.esnaf_id = k.id
        WHERE f.ogrenci_id = ?
    ''', (session['user_id'],)).fetchall()
    
    urun_listesi = []
    ogr_lat = session.get('lat', 39.9208) 
    ogr_lng = session.get('lng', 32.8541)

    for row in favoriler:
        u = dict(row)
        if not u.get('resim'): u['resim'] = 'default_food.png'
        dist = ((u['enlem'] - ogr_lat)**2 + (u['boylam'] - ogr_lng)**2)**0.5 * 100
        u['mesafe'] = round(dist, 1)
        if u['eski_fiyat'] and u['eski_fiyat'] > u['yeni_fiyat']:
            u['indirim_orani'] = int(((u['eski_fiyat'] - u['yeni_fiyat']) / u['eski_fiyat']) * 100)
        else:
            u['indirim_orani'] = 0
        u['favori_mi'] = True
        urun_listesi.append(u)
    
    conn.close()
    rozet_data = rozet_bilgisi_al(session['user_id'])

    return render_template('student.html', 
                           urunler=urun_listesi, 
                           kullanici=session.get('ad_soyad'), 
                           sayfa_tipi='favori', 
                           rozet=rozet_data['isim'], 
                           rozet_renk=rozet_data['renk'], 
                           arama_terimi="", 
                           secili_filtreler={'min': 0,'max': 5000,'sort': 'varsayilan','stok': None})

@app.route('/favori-islem/<int:urun_id>')
def favori_islem(urun_id):
    if session.get('rol') != 'ogrenci': return redirect(url_for('giris_yap'))
    conn = get_db_connection()
    var_mi = conn.execute('SELECT * FROM favoriler WHERE ogrenci_id = ? AND urun_id = ?', (session['user_id'], urun_id)).fetchone()
    if var_mi: conn.execute('DELETE FROM favoriler WHERE id = ?', (var_mi['id'],))
    else: conn.execute('INSERT INTO favoriler (ogrenci_id, urun_id) VALUES (?, ?)', (session['user_id'], urun_id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('ogrenci_paneli'))

@app.route('/siparislerim')
def siparislerim():
    if 'user_id' not in session: return redirect(url_for('giris_yap'))
    conn = get_db_connection()
    siparisler = conn.execute('''
        SELECT s.*, u.ad as urun_adi, k.ad_soyad as restoran_adi, s.durum
        FROM siparisler s
        JOIN urunler u ON s.urun_id = u.id
        JOIN kullanicilar k ON u.esnaf_id = k.id
        WHERE s.ogrenci_id = ?
        ORDER BY s.tarih DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    rozet_data = rozet_bilgisi_al(session['user_id'])

    return render_template('orders.html', siparisler=siparisler, kullanici=session.get('ad_soyad'), rozet=rozet_data['isim'], rozet_renk=rozet_data['renk'])

@app.route('/yorum-yap', methods=['POST'])
def yorum_yap():
    conn = get_db_connection()
    conn.execute('INSERT INTO yorumlar (siparis_id, esnaf_id, ogrenci_id, puan, yorum_metni) VALUES (?, ?, ?, ?, ?)',
                 (request.form['siparis_id'], request.form['esnaf_id'], session['user_id'], request.form['puan'], request.form['yorum']))
    conn.commit()
    conn.close()
    flash("Yorum yapıldı!", "success")
    return redirect(url_for('siparislerim'))

# --- ESNAF PANELİ ---
@app.route('/esnaf', methods=['GET', 'POST'])
def esnaf_paneli():
    if session.get('rol') != 'esnaf': return redirect(url_for('giris_yap'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        ad = request.form['ad']
        eski_fiyat = request.form['eski']
        yeni_fiyat = request.form['yeni']
        stok = request.form['stok']
        
        dosya = request.files.get('urun_resmi')
        resim_adi = 'default_food.png'

        if dosya and dosya.filename:
            ext = os.path.splitext(dosya.filename)[1]
            benzersiz_isim = f"yemek_{session['user_id']}_{uuid.uuid4().hex[:8]}{ext}"
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], benzersiz_isim))
            resim_adi = benzersiz_isim

        conn.execute('INSERT INTO urunler (esnaf_id, ad, eski_fiyat, yeni_fiyat, stok, restoran_adi, resim) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (session['user_id'], ad, eski_fiyat, yeni_fiyat, stok, session['ad_soyad'], resim_adi))
        conn.commit()
        return redirect(url_for('esnaf_paneli'))
    
    urunler = conn.execute('SELECT * FROM urunler WHERE esnaf_id = ? ORDER BY id DESC', (session['user_id'],)).fetchall()
    yorumlar = conn.execute('SELECT yorumlar.*, kullanicilar.ad_soyad as ogrenci_adi FROM yorumlar JOIN kullanicilar ON yorumlar.ogrenci_id = kullanicilar.id WHERE yorumlar.esnaf_id = ? ORDER BY id DESC', (session['user_id'],)).fetchall()
    ortalama = conn.execute('SELECT AVG(puan) FROM yorumlar WHERE esnaf_id = ?', (session['user_id'],)).fetchone()[0]
    puan = round(ortalama, 1) if ortalama else 0
    conn.close()
    return render_template('shop.html', urunler=urunler, yorumlar=yorumlar, puan=puan, kullanici=session.get('ad_soyad'))

@app.route('/stok-guncelle', methods=['POST'])
def stok_guncelle():
    conn = get_db_connection()
    conn.execute('UPDATE urunler SET stok = ? WHERE id = ? AND esnaf_id = ?', (request.form['yeni_stok'], request.form['urun_id'], session['user_id']))
    conn.commit()
    conn.close()
    flash("Stok güncellendi.", "success")
    return redirect(url_for('esnaf_paneli'))

@app.route('/urun-sil/<int:urun_id>')
def urun_sil(urun_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM urunler WHERE id = ? AND esnaf_id = ?', (urun_id, session['user_id']))
    conn.execute('DELETE FROM favoriler WHERE urun_id = ?', (urun_id,))
    conn.commit()
    conn.close()
    flash("Ürün silindi.", "success")
    return redirect(url_for('esnaf_paneli'))

@app.route('/kod-dogrula', methods=['POST'])
def kod_dogrula():
    kod = request.form.get('kod', '').strip().upper().replace('#', '')
    conn = get_db_connection()
    siparis = conn.execute('SELECT * FROM siparisler WHERE siparis_kodu = ?', (kod,)).fetchone()
    if siparis:
        if siparis['durum'] == 'Bekliyor' or siparis['durum'] == 'Hazırlanıyor':
            conn.execute("UPDATE siparisler SET durum = 'Teslim Edildi' WHERE id = ?", (siparis['id'],))
            conn.commit()
            flash("KOD ONAYLANDI!", "success")
        else: flash("Kod kullanılmış!", "warning")
    else: flash("Geçersiz Kod!", "danger")
    conn.close()
    return redirect(url_for('esnaf_paneli'))

@app.route('/esnaf-analiz')
def esnaf_analiz():
    if session.get('rol') != 'esnaf': return redirect(url_for('giris_yap'))
    conn = get_db_connection()
    user_id = session['user_id']
    ciro = conn.execute("SELECT SUM(urunler.yeni_fiyat) FROM siparisler JOIN urunler ON siparisler.urun_id = urunler.id WHERE siparisler.esnaf_id = ? AND siparisler.durum = 'Teslim Edildi'", (user_id,)).fetchone()[0] or 0
    toplam_siparis = conn.execute("SELECT COUNT(*) FROM siparisler WHERE esnaf_id = ? AND durum = 'Teslim Edildi'", (user_id,)).fetchone()[0]
    populer = conn.execute('''SELECT urunler.ad, COUNT(siparisler.id) as satis_sayisi FROM siparisler JOIN urunler ON siparisler.urun_id = urunler.id WHERE siparisler.esnaf_id = ? AND siparisler.durum = 'Teslim Edildi' GROUP BY urunler.ad ORDER BY satis_sayisi DESC LIMIT 5''', (user_id,)).fetchall()
    conn.close()
    return render_template('analytics.html', toplam_kazanc=ciro, toplam_siparis=toplam_siparis, urun_isimleri=[p['ad'] for p in populer], satis_sayilari=[p['satis_sayisi'] for p in populer], kullanici=session.get('ad_soyad'))

@app.route('/yonetici')
def yonetici_paneli():
    conn = get_db_connection()
    stats = {
        'uye': conn.execute('SELECT COUNT(*) FROM kullanicilar').fetchone()[0],
        'esnaf': conn.execute("SELECT COUNT(*) FROM kullanicilar WHERE rol = 'esnaf'").fetchone()[0],
        'siparis': conn.execute("SELECT COUNT(*) FROM siparisler WHERE durum = 'Teslim Edildi'").fetchone()[0],
        'tasarruf': conn.execute("SELECT SUM(urunler.eski_fiyat - urunler.yeni_fiyat) FROM siparisler JOIN urunler ON siparisler.urun_id = urunler.id WHERE siparisler.durum = 'Teslim Edildi'").fetchone()[0] or 0
    }
    kullanicilar = conn.execute('SELECT * FROM kullanicilar ORDER BY id DESC LIMIT 20').fetchall()
    conn.close()
    return render_template('admin.html', toplam_uye=stats['uye'], toplam_esnaf=stats['esnaf'], toplam_siparis=stats['siparis'], toplam_tasarruf=int(stats['tasarruf']), kullanicilar=kullanicilar)

@app.route('/kullanici-sil/<int:user_id>')
def kullanici_sil(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM kullanicilar WHERE id = ?', (user_id,))
    conn.execute('DELETE FROM urunler WHERE esnaf_id = ?', (user_id,))
    conn.execute('DELETE FROM siparisler WHERE esnaf_id = ? OR musteri_id = ?', (user_id, user_id))
    conn.commit()
    conn.close()
    flash('Kullanıcı silindi.', 'warning')
    return redirect(url_for('yonetici_paneli'))

@app.route('/ayarlar', methods=['GET', 'POST'])
def ayarlar():
    if 'user_id' not in session: return redirect(url_for('giris_yap'))
    conn = get_db_connection()
    
    if request.method == 'POST':
        ad = request.form['ad_soyad']
        email = request.form['email']
        yeni_sifre = request.form.get('yeni_sifre')
        dosya = request.files.get('profil_foto')
        enlem = request.form.get('enlem')
        boylam = request.form.get('boylam')
        
        mevcut_user = conn.execute('SELECT * FROM kullanicilar WHERE id = ?', (session['user_id'],)).fetchone()
        
        # Eğer güncelleme sırasında kullanıcı bulunamazsa hata vermesin diye kontrol
        if mevcut_user is None:
            conn.close()
            session.clear()
            return redirect(url_for('giris_yap'))

        resim_adi = mevcut_user['profil_resmi']
        
        if dosya and dosya.filename:
            ext = os.path.splitext(dosya.filename)[1]
            benzersiz_isim = f"{session['user_id']}_{uuid.uuid4().hex[:8]}{ext}"
            if resim_adi and resim_adi != 'default.png':
                try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], resim_adi))
                except: pass
            dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], benzersiz_isim))
            resim_adi = benzersiz_isim

        sifre_sql = mevcut_user['sifre']
        if yeni_sifre and len(yeni_sifre.strip()) > 0:
            sifre_sql = yeni_sifre
            
        lat_sql = enlem if enlem else mevcut_user['enlem']
        lng_sql = boylam if boylam else mevcut_user['boylam']
        
        try:
            conn.execute('''UPDATE kullanicilar SET ad_soyad=?, email=?, sifre=?, profil_resmi=?, enlem=?, boylam=? WHERE id=?''', 
                         (ad, email, sifre_sql, resim_adi, lat_sql, lng_sql, session['user_id']))
            conn.commit()
            session['ad_soyad'] = ad
            session['foto'] = resim_adi
            flash('Profil ve konum bilgileri güncellendi.', 'success')
        except sqlite3.IntegrityError:
            flash('Bu e-posta adresi kullanımda!', 'danger')
            
    # --- DÜZELTME BURADA BAŞLIYOR ---
    u = conn.execute('SELECT * FROM kullanicilar WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    # EĞER KULLANICI BULUNAMAZSA (HATA BURADAN KAYNAKLANIYORDU)
    if u is None:
        session.clear() # Bozuk oturumu temizle
        flash('Kullanıcı bilgisi bulunamadı. Lütfen tekrar giriş yapın.', 'danger')
        return redirect(url_for('giris_yap'))
    # -------------------------------

    # --- AYARLAR SAYFASI İÇİN DETAYLI ROZET BİLGİSİ ---
    rozet_detay = rozet_bilgisi_al(session['user_id'])
    
    return render_template('settings.html', u=u, rozet=rozet_detay)

@app.route('/hesap-sil-kendi')
def hesap_sil_kendi():
    if 'user_id' not in session: return redirect(url_for('giris_yap'))
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute('DELETE FROM kullanicilar WHERE id = ?', (user_id,))
    conn.execute('DELETE FROM urunler WHERE esnaf_id = ?', (user_id,))
    conn.execute('DELETE FROM siparisler WHERE esnaf_id = ? OR musteri_id = ?', (user_id, user_id))
    conn.execute('DELETE FROM yorumlar WHERE esnaf_id = ? OR ogrenci_id = ?', (user_id, user_id))
    conn.execute('DELETE FROM favoriler WHERE ogrenci_id = ?', (user_id,))
    conn.commit()
    conn.close()
    session.clear()
    flash('Hesabınız kalıcı olarak silindi.', 'info')
    return redirect(url_for('giris_yap'))

@app.route('/sifremi-unuttum', methods=['GET', 'POST'])
def sifremi_unuttum():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM kullanicilar WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user:
            flash('Sıfırlama linki e-posta adresinize (konsola) gönderildi.', 'info')
        else:
            flash('Sıfırlama linki e-posta adresinize (konsola) gönderildi.', 'info')
        return redirect(url_for('giris_yap'))
    return render_template('forgot_password.html')

@app.route('/sifre-sifirla/<token>', methods=['GET', 'POST'])
def sifre_sifirla(token):
    try: email = s.loads(token, salt='sifre-sifirlama', max_age=3600)
    except:
        flash('Link geçersiz veya süresi dolmuş.', 'danger')
        return redirect(url_for('sifremi_unuttum'))
    if request.method == 'POST':
        yeni_sifre = request.form['yeni_sifre']
        conn = get_db_connection()
        conn.execute('UPDATE kullanicilar SET sifre = ? WHERE email = ?', (yeni_sifre, email))
        conn.commit()
        conn.close()
        flash('Şifreniz başarıyla güncellendi.', 'success')
        return redirect(url_for('giris_yap'))
    return render_template('reset_password.html', token=token)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)