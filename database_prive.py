import sqlite3
from datetime import datetime, timedelta

DATABASE_PATH = "prive_bot.db"

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modelos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            nome_completo TEXT NOT NULL,
            canal_free TEXT NOT NULL,
            canal_fan TEXT NOT NULL,
            canal_vip TEXT NOT NULL,
            canal_prive TEXT NOT NULL,
            preco_fan REAL DEFAULT 29.90,
            preco_vip REAL DEFAULT 79.90,
            preco_prive REAL DEFAULT 299.90,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo_id INTEGER NOT NULL,
            canal_tipo TEXT NOT NULL,
            file_id TEXT,
            tipo_midia TEXT,
            caption TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expira_em TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assinantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            modelo_id INTEGER NOT NULL,
            plano TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expira_em TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_modelo(username, nome_completo, preco_fan=29.90, preco_vip=79.90, preco_prive=299.90):
    conn = get_connection()
    cursor = conn.cursor()
    canal_free = f"@{username}_Free"
    canal_fan = f"@{username}_Fans"
    canal_vip = f"@{username}_VIP"
    canal_prive = f"@{username}_Prive"
    cursor.execute("""
        INSERT INTO modelos (username, nome_completo, canal_free, canal_fan, canal_vip, canal_prive,
                            preco_fan, preco_vip, preco_prive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, nome_completo, canal_free, canal_fan, canal_vip, canal_prive,
          preco_fan, preco_vip, preco_prive))
    conn.commit()
    modelo_id = cursor.lastrowid
    conn.close()
    return {"id": modelo_id, "username": username, "nome": nome_completo}

def get_modelos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE ativo = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_modelo_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE username = ? AND ativo = 1", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
