from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'gizli_anahtar_my_song_list'

# Helper function for database connection
def get_db_connection():
    conn = sqlite3.connect('my_song_list.db')
    conn.row_factory = sqlite3.Row
    return conn

# Business Logic: Extract YouTube ID from URL
def extract_youtube_id(url):
    if not url:
        return None
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

# Home Page Route
@app.route('/')
def index():
    if 'user_id' in session:
        return f"<h1>Hoşgeldin, {session['username']}!</h1> <a href='/add_song'>Yeni Şarkı Ekle</a> | <a href='/logout'>Çıkış Yap</a>"
    return "<h1>my song list</h1> <a href='/login'>Giriş Yap</a> | <a href='/register'>Kayıt Ol</a>"

# User Registration
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
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return "<h1>Hata: Bu kullanıcı adı alınmış.</h1> <a href='/register'>Tekrar dene</a>"
        
    return render_template('register.html')

# User Login
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user is None or not check_password_hash(user['password_hash'], password):
            return "<h1>Hata: Yanlış kullanıcı adı veya şifre.</h1> <a href='/login'>Tekrar dene</a>"
        
        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('index'))
        
    return render_template('login.html')

# User Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Create: Add New Song - US1
@app.route('/add_song', methods=('GET', 'POST'))
def add_song():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        youtube_link = request.form['youtube_link']
        rating = request.form['rating']
        genius_note = request.form['genius_note']
        user_id = session['user_id']
        
        youtube_id = extract_youtube_id(youtube_link)
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO songs (title, artist, youtube_id, rating, genius_note, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, artist, youtube_id, rating, genius_note, user_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
        
    return render_template('add_song.html')

if __name__ == '__main__':
    app.run(debug=True)