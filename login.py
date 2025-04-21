import streamlit as st
import database as db

def login():
    st.title("🔐 Login")

    col1, col2, col3 = st.columns([1, 2, 1])  # Centraliza na coluna do meio

    with col2:
        usuario = st.text_input("Nome de usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            # Verificar se o usuário existe e se a senha está correta
            if db.usuario_existe(usuario):  # Verifica se o usuário existe
                if db.verificar_usuario(usuario, senha):  # Verifica se a senha está correta
                    st.success("Login realizado com sucesso!")
                    st.session_state['usuario'] = usuario
                    st.experimental_rerun()  # Força o reload da página após login bem-sucedido
                else:
                    st.error("Senha inválida.")
            else:
                st.error("Usuário não encontrado.")
