import pandas as pd

def adicionar_transacao(conn, username, tipo, categoria, valor, data):
    c = conn.cursor()
    c.execute("INSERT INTO transacoes (username, tipo, categoria, valor, data) VALUES (?, ?, ?, ?, ?)",
            (username, tipo, categoria, valor, data))
    conn.commit()

def carregar_dados_usuario(conn, username):
    c = conn.cursor()
    c.execute("SELECT * FROM transacoes WHERE username = ?", (username,))
    rows = c.fetchall()
    return pd.DataFrame(rows, columns=['id', 'username', 'tipo', 'categoria', 'valor', 'data'])
