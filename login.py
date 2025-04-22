import streamlit as st
import database as db

def login():
    st.title("🔐 Login")

    col1, col2, col3 = st.columns([1, 2, 1])  # Centraliza na coluna do meio

    with col2:
        usuario = st.text_input("Nome de usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if db.verificar_usuario(usuario, senha):
                st.success("Login realizado com sucesso!")
                st.session_state['usuario'] = usuario
                st.rerun()  # Força o reload da página após login bem-sucedido
            else:
                st.error("Usuário ou senha inválidos.")
