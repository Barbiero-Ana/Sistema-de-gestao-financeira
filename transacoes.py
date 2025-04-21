import pandas as pd

def adicionar_transacao(conn, usuario, tipo, categoria, valor, data):
    c = conn.cursor()
    c.execute("INSERT INTO transacoes (usuario, tipo, categoria, valor, data) VALUES (?, ?, ?, ?, ?)",
            (usuario, tipo, categoria, valor, data))
    conn.commit()

def carregar_dados_usuario(conn, usuario):
    c = conn.cursor()
    c.execute("SELECT * FROM transacoes WHERE usuario = ?", (usuario,))
    rows = c.fetchall()
    return pd.DataFrame(rows, columns=['id', 'usuario', 'tipo', 'categoria', 'valor', 'data'])
