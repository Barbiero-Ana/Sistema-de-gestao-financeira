import sqlite3

def conectar():
    return sqlite3.connect('financas.db', check_same_thread=False)

def criar_tabelas(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                genero TEXT,
                idade INTEGER,
                profissao TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                tipo TEXT,
                categoria TEXT,
                valor REAL,
                data TEXT,
                FOREIGN KEY(username) REFERENCES users(username))''')
    conn.commit()
