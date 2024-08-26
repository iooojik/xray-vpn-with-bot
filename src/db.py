import sqlite3
from datetime import datetime
from functools import wraps


# Decorator to manage database connection
def db_connection(func):
    @wraps(func)
    def with_connection(*args, **kwargs):
        conn = sqlite3.connect('db/vpn_bot.db')
        try:
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result

    return with_connection


@db_connection
def init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vpn_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            config TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()


@db_connection
def save_vpn_config(conn, user_id, config):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vpn_configs (user_id, config, created_at) 
        VALUES (?, ?, ?)
    ''', (user_id, config, datetime.now().isoformat()))
    conn.commit()


@db_connection
def get_vpn_configs(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT config, created_at FROM vpn_configs WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    return rows
