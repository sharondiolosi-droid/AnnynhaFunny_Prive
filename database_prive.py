"""
===============================================
AnnynhaFunny_PriveBot - Banco de Dados
===============================================
"""

import sqlite3
import json
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
            mensagem_id INTEGER,
            file_id TEXT,
            tipo_midia TEXT,
            caption TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expira_em TIMESTAMP,
            FOREIGN KEY (modelo_id) REFERENCES modelos(id)
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
            expira_em TIMESTAMP,
            FOREIGN KEY (modelo_id) REFERENCES modelos(id)
        )
    """)

    conn.commit()
    conn.close()

# ????????????????????????????????????????????
# MODELOS
# ????????????????????????????????????????????

def add_modelo(username, nome_completo, preco_fan=29.90, preco_vip=79.90, preco_prive=299.90):
    conn = get_connection()
    cursor = conn.cursor()

    canal_free = f"@{username}{PREFIXO_FREE}"
    canal_fan = f"@{username}{PREFIXO_FAN}"
    canal_vip = f"@{username}{PREFIXO_VIP}"
    canal_prive = f"@{username}{PREFIXO_PRIVE}"

    cursor.execute("""
        INSERT INTO modelos (username, nome_completo, canal_free, canal_fan, canal_vip, canal_prive,
                            preco_fan, preco_vip, preco_prive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, nome_completo, canal_free, canal_fan, canal_vip, canal_prive,
          preco_fan, preco_vip, preco_prive))

    conn.commit()
    modelo_id = cursor.lastrowid
    conn.close()

    return {
        "id": modelo_id,
        "username": username,
        "nome": nome_completo,
        "canal_free": canal_free,
        "canal_fan": canal_fan,
        "canal_vip": canal_vip,
        "canal_prive": canal_prive
    }

def get_modelos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE ativo = 1 ORDER BY id")
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

def get_modelo_by_id(modelo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM modelos WHERE id = ? AND ativo = 1", (modelo_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# ????????????????????????????????????????????
# DROPS
# ????????????????????????????????????????????

def add_drop(modelo_id, canal_tipo, file_id, tipo_midia, caption="", expira_horas=48):
    conn = get_connection()
    cursor = conn.cursor()

    expira_em = datetime.now() + timedelta(hours=expira_horas)

    cursor.execute("""
        INSERT INTO drops (modelo_id, canal_tipo, file_id, tipo_midia, caption, expira_em)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (modelo_id, canal_tipo, file_id, tipo_midia, caption, expira_em.isoformat()))

    conn.commit()
    drop_id = cursor.lastrowid
    conn.close()
    return drop_id

def get_drops(modelo_id, canal_tipo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM drops
        WHERE modelo_id = ? AND canal_tipo = ?
        ORDER BY criado_em DESC LIMIT 10
    """, (modelo_id, canal_tipo))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ????????????????????????????????????????????
# ASSINANTES
# ????????????????????????????????????????????

def add_assinante(telegram_id, modelo_id, plano, expira_dias=30):
    conn = get_connection()
    cursor = conn.cursor()

    expira_em = datetime.now() + timedelta(days=expira_dias)

    cursor.execute("""
        INSERT INTO assinantes (telegram_id, modelo_id, plano, expira_em)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, modelo_id, plano, expira_em.isoformat()))

    conn.commit()
    assinante_id = cursor.lastrowid
    conn.close()
    return assinante_id

def get_assinantes(modelo_id, plano=None):
    conn = get_connection()
    cursor = conn.cursor()

    if plano:
        cursor.execute("""
            SELECT * FROM assinantes
            WHERE modelo_id = ? AND plano = ? AND ativo = 1
        """, (modelo_id, plano))
    else:
        cursor.execute("""
            SELECT * FROM assinantes
            WHERE modelo_id = ? AND ativo = 1
        """, (modelo_id,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_assinante(telegram_id, modelo_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM assinantes
        WHERE telegram_id = ? AND modelo_id = ? AND ativo = 1
    """, (telegram_id, modelo_id))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def renovar_assinante(assinante_id, dias=30):
    conn = get_connection()
    cursor = conn.cursor()

    nova_expira = datetime.now() + timedelta(days=dias)

    cursor.execute("""
        UPDATE assinantes
        SET expira_em = ?, ativo = 1
        WHERE id = ?
    """, (nova_expira.isoformat(), assinante_id))

    conn.commit()
    conn.close()

def cancelar_assinante(assinante_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE assinantes SET ativo = 0 WHERE id = ?
    """, (assinante_id,))

    conn.commit()
    conn.close()
