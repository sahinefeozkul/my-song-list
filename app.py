from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_my_song_list'

def get_db_connection():
    conn = sqlite3.connect('my_song_list.db')
    conn.row_factory = sqlite3.Row
    return conn

# YouTube linkinden sadece ID'yi çıkartan Business Logic
def extract_youtube_id(url):
    if not url:
        return None
    # Hem kısa (youtu.be) hem uzun (youtube.com) linkleri yakalar
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# Ana Sayfa
@app.route('/')
def index():
    if 'user_id' in session:
        # Kullanıcı giriş yaptıysa şarkı ekleme butonu da çıksın
        return f"<h1>Hoşgeldin, {session['username']}!</h1> <a href='/add_song'>Yeni Şarkı Ekle</a> | <a href='/logout'>Çıkış Yap</a>"
    return "<h1>my song list</h1> <a href='/login'>Giriş Yap</a> | <a href='/register'>Kayıt Ol</a>"

# Şarkı Ekleme (Create) İşlemi - US1
@app.route('/add_song', methods=('GET', 'POST'))
def add_song():
    # Eğer kullanıcı giriş yapmamışsa direkt login sayfasına at
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        youtube_link = request.form['youtube_link']
        rating = request.form['rating']
        genius_note = request.form['genius_note']
        user_id = session['user_id'] # Hangi kullanıcı ekliyor?
        
        # Linki parçala ve sadece ID'yi al
        youtube_id = extract_youtube_id(youtube_link)
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO songs (title, artist, youtube_id, rating, genius_note, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, artist, youtube_id, rating, genius_note, user_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index')) # Ekledikten sonra ana sayfaya dön
        
    return render_template('add_song.html')

# Kayıt Olma
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            hashed_pw = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect(url_for('login')) # Kayıt başarılıysa direkt giriş sayfasına yönlendir
        except sqlite3.IntegrityError:
            conn.close()
            return "<h1>Hata: Bu kullanıcı adı alınmış.</h1> <a href='/register'>Tekrar dene</a>"
        
    return render_template('register.html')

# Giriş Yapma
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        # Kullanıcı yoksa veya şifre eşleşmiyorsa
        if user is None or not check_password_hash(user['password_hash'], password):
            return "<h1>Hata: Yanlış kullanıcı adı veya şifre.</h1> <a href='/login'>Tekrar dene</a>"
        
        # Giriş başarılıysa session (oturum) oluştur
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('index'))
        
    return render_template('login.html')

# Çıkış Yapma
@app.route('/logout')
def logout():
    session.clear() # Oturumu temizle
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)