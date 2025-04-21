import sqlite3

# Função para conectar ao banco de dados
def conectar_db():
    conn = sqlite3.connect('usuarios.db')
    return conn

# Função para verificar se o nome de usuário já existe
def usuario_existe(nome_usuario):
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ?", (nome_usuario,))
    usuario = cursor.fetchone()
    
    conn.close()
    
    return usuario is not None  # Retorna True se o usuário já existir

# Função para verificar se o usuário e a senha estão corretos
def verificar_usuario(nome_usuario, senha):
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (nome_usuario, senha))
    usuario = cursor.fetchone()
    
    conn.close()
    
    return usuario is not None  # Retorna True se a combinação de usuário e senha for válida

# Função para criar um novo usuário
def criar_usuario(nome_usuario, senha, idade, genero, profissao):
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Criação da tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        senha TEXT,
                        idade INTEGER,
                        genero TEXT,
                        profissao TEXT)''')
    
    cursor.execute("INSERT INTO usuarios (usuario, senha, idade, genero, profissao) VALUES (?, ?, ?, ?, ?)", 
                   (nome_usuario, senha, idade, genero, profissao))
    conn.commit()
    conn.close()

# Função para criar as tabelas de usuários e transações
def criar_tabelas(conn):
    cursor = conn.cursor()

    # Criação da tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        senha TEXT,
                        idade INTEGER,
                        genero TEXT,
                        profissao TEXT)''')

    # Criação da tabela de transações (gastos/receitas)
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT,
                        tipo TEXT,
                        categoria TEXT,
                        valor REAL,
                        data TEXT)''')

    conn.commit()
    conn.close()

# Função para adicionar uma despesa ou receita
def adicionar_transacao(conn, usuario, tipo, categoria, valor, data):
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO transacoes (usuario, tipo, categoria, valor, data) VALUES (?, ?, ?, ?, ?)", 
                (usuario, tipo, categoria, valor, data))
    conn.commit()

# Função para obter todas as transações de um usuário
def obter_transacoes(conn, usuario):
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transacoes WHERE usuario = ?", (usuario,))
    transacoes = cursor.fetchall()
    
    return transacoes
