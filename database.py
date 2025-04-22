import sqlite3

# Função para conectar ao banco de dados
def conectar_db():
    return sqlite3.connect('banco.db')

# Função para criar as tabelas no banco de dados
def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Criação da tabela de usuários
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        senha TEXT NOT NULL
    )''')
    
    # Criação da tabela de transações
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        tipo TEXT,
        categoria TEXT,
        valor REAL,
        descricao TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )''')
    
    conn.commit()
    conn.close()

# Função para criar um usuário no banco de dados
def criar_usuario(nome_usuario, senha):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (nome_usuario, senha))
    conn.commit()
    conn.close()

# Função para verificar se o usuário existe no banco de dados
def usuario_existe(nome_usuario):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (nome_usuario,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

# Função para verificar a senha do usuário
def verificar_usuario(nome_usuario, senha):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (nome_usuario, senha))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

# Função para adicionar uma transação no banco de dados
def adicionar_transacao(usuario_id, tipo, categoria, valor, descricao):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transacoes (usuario_id, tipo, categoria, valor, descricao) VALUES (?, ?, ?, ?, ?)", 
                   (usuario_id, tipo, categoria, valor, descricao))
    conn.commit()
    conn.close()
