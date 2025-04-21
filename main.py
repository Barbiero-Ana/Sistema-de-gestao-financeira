import streamlit as st
from database import conectar, criar_tabelas
from autentic import verificar_login, verificar_usuario_existente, criar_usuario
from transacoes import adicionar_transacao, carregar_dados_usuario
from dashboard import mostrar_dashboard

conn = conectar()
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
        usuario = st.sidebar.text_input("Usuário")
        senha = st.sidebar.text_input("Senha", type="password")

        if st.sidebar.button("Entrar"):
            if verificar_login(conn, usuario, senha):
                st.session_state['usuario'] = usuario
                st.rerun()
            else:
                st.sidebar.error("Usuário ou senha incorretos.")

    elif menu == "Criar Conta":
        novo_usuario = st.sidebar.text_input("Novo Usuário")
        nova_senha = st.sidebar.text_input("Nova Senha", type="password")
        genero = st.sidebar.selectbox("Gênero", ["Masculino", "Feminino", "Outro", "Prefiro não dizer"])
        idade = st.sidebar.number_input("Idade", min_value=10, max_value=120, step=1)
        profissao = st.sidebar.text_input("Profissão")

        if st.sidebar.button("Criar"):
            if novo_usuario == "" or nova_senha == "":
                st.sidebar.warning("Preencha todos os campos.")
            elif verificar_usuario_existente(conn, novo_usuario):
                st.sidebar.error("Erro: nome de usuário já está sendo utilizado.")
            else:
                if criar_usuario(conn, novo_usuario, nova_senha, genero, idade, profissao):
                    st.sidebar.success("Conta criada com sucesso! Faça login.")
                else:
                    st.sidebar.error("Erro ao criar conta.")

    if 'usuario' in st.session_state:
        pagina_principal(st.session_state['usuario'])

main()
