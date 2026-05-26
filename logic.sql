-- User Registration
INSERT INTO users (username, password_hash) VALUES (?, ?);

-- User Login Authentication
SELECT * FROM users WHERE username = ?;

-- Create: Add New Song (US1)
INSERT INTO songs (title, artist, youtube_id, rating, genius_note, user_id)
VALUES (?, ?, ?, ?, ?, ?);