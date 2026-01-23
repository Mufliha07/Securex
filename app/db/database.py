import sqlite3

DB_NAME = "users.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            two_fa_enabled INTEGER DEFAULT 0,
            two_fa_secret TEXT
        )
    """)
    conn.commit()
    conn.close()

def create_user(username: str, password: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    conn.commit()
    conn.close()

def get_user(username: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password, two_fa_enabled, two_fa_secret FROM users WHERE username=?",
        (username,)
    )
    row = cur.fetchone()
    conn.close()
    return row

def save_2fa_secret(username: str, secret: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET two_fa_secret=?, two_fa_enabled=0 WHERE username=?",
        (secret, username)
    )
    conn.commit()
    conn.close()

def enable_2fa(username: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET two_fa_enabled=1 WHERE username=?",
        (username,)
    )
    conn.commit()
    conn.close()