import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect('vpn_bot.db')
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
    conn.close()


def save_vpn_config(user_id, config):
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vpn_configs (user_id, config, created_at) 
        VALUES (?, ?, ?)
    ''', (user_id, config, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_vpn_configs(user_id):
    conn = sqlite3.connect('vpn_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT config, created_at FROM vpn_configs WHERE user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
