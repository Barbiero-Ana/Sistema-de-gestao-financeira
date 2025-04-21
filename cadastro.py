import streamlit as st
import database as db

def cadastro():
    st.title("📝 Criar nova conta")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        novo_usuario = st.text_input("Nome de usuário")
        nova_senha = st.text_input("Senha", type="password")
        idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
        genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro", "Prefiro não dizer"])
        profissao = st.text_input("Profissão")

        if st.button("Cadastrar"):
            if db.usuario_existe(novo_usuario):
                st.error("Erro: nome de usuário já está sendo utilizado.")
            else:
                db.criar_usuario(novo_usuario, nova_senha, idade, genero, profissao)
                st.success("Conta criada com sucesso! Faça login na página inicial.")
