import pandas as pd
import database as db

# Função para adicionar uma transação (receita/despesa)
def adicionar_transacao(conn, usuario, tipo, categoria, valor, data):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
    usuario_id = cursor.fetchone()[0]  # Obtém o id do usuário
    
    db.adicionar_transacao(usuario_id, tipo, categoria, valor, data)

# Função para carregar os dados de transações de um usuário
def carregar_dados_usuario(conn, usuario):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))
    usuario_id = cursor.fetchone()[0]
    
    transacoes = db.carregar_transacoes(usuario_id)
    df = pd.DataFrame(transacoes, columns=['id', 'usuario_id', 'tipo', 'categoria', 'valor', 'data'])
    return df
