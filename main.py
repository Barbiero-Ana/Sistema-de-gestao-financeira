import streamlit as st
from database import conectar_db, criar_tabelas
from autentic import verificar_login, verificar_usuario_existente, criar_usuario
from transacoes import adicionar_transacao, carregar_dados_usuario
from dashboard import mostrar_dashboard
from login import login
from cadastro import cadastro

conn = conectar_db()
criar_tabelas(conn)

def pagina_principal(usuario):
    st.title(f"Bem-vindo, {usuario} 👋")
    st.sidebar.success("Logado como: " + usuario)

    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    categoria = st.text_input("Categoria")
    valor = st.number_input("Valor", step=0.01)
    data = st.date_input("Data")

    if st.button("Adicionar Transação"):
        adicionar_transacao(conn, usuario, tipo, categoria, valor, str(data))
        st.success("Transação adicionada com sucesso!")
        st.rerun()

    st.divider()
    df = carregar_dados_usuario(conn, usuario)
    mostrar_dashboard(df)

def main():
    st.set_page_config(page_title="Gerenciador de Orçamento", layout="wide")
    st.sidebar.title("Login / Cadastro")

    menu = st.sidebar.radio("Menu", ["Login", "Criar Conta"])

    if menu == "Login":
        login()
    elif menu == "Criar Conta":
        cadastro()

if __name__ == "__main__":
    main()
