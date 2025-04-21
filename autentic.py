import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(conn, usuario, senha):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (usuario, hash_senha(senha)))
    return c.fetchone()

def verificar_usuario_existente(conn, usuario):
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (usuario,))
    return c.fetchone() is not None

def criar_usuario(conn, usuario, senha, genero, idade, profissao):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, genero, idade, profissao) VALUES (?, ?, ?, ?, ?)",
                (usuario, hash_senha(senha), genero, idade, profissao))
        conn.commit()
        return True
    except:
        return False
