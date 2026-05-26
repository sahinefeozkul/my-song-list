import sqlite3

def init_db():
    # Veritabanı dosyasına bağlan (yoksa otomatik oluşturur)
    conn = sqlite3.connect('my_song_list.db')
    cursor = conn.cursor()

    # 1. Tablo: Kullanıcılar (Users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 2. Tablo: Şarkılar (Songs)
    # user_id ile kullanıcı tablosuna bağlanıyor (Foreign Key)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            youtube_id TEXT,
            rating INTEGER,
            genius_note TEXT,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("my song list veritabani ve tablolari basariyla olusturuldu.")

if __name__ == '__main__':
    init_db()