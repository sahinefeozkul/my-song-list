from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_my_song_list'

def get_db_connection():
    conn = sqlite3.connect('my_song_list.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ana Sayfa
@app.route('/')
def index():
    # Eğer kullanıcı giriş yapmışsa (session'da user_id varsa)
    if 'user_id' in session:
        return f"<h1>Hoşgeldin, {session['username']}!</h1> <a href='/logout'>Çıkış Yap</a>"
    # Giriş yapmamışsa
    return "<h1>my song list</h1> <a href='/login'>Giriş Yap</a> | <a href='/register'>Kayıt Ol</a>"

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