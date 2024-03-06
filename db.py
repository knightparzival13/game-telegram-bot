import sqlite3

conn = sqlite3.connect('users.sql')
cur = conn.cursor()

cur.execute(
    'CREATE TABLE IF NOT EXISTS users ('
    'tg_id INT NOT NULL, '
    'status VARCHAR(32) NOT NULL DEFAULT "Участник", '
    'balance INT NOT NULL DEFAULT 0, '
    'diamonds INT NOT NULL DEFAULT 0, '
    'date_of_last_take TEXT DEFAULT NULL, '
    'message_count INT DEFAULT 0, '
    'prefix BIT DEFAULT 0)'
)
conn.commit()
cur.close()
conn.close()
