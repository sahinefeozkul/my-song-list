import sqlite3

def init_db():
    conn = sqlite3.connect('my_song_list.db')
    
    # Read schema.sql and execute the commands to build tables
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
        
    conn.commit()
    conn.close()
    print("Database initialized successfully using schema.sql.")

if __name__ == '__main__':
    init_db()