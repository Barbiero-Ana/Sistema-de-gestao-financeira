import streamlit as st
import database as db

# Função principal
def main():
    # Criar as tabelas (se ainda não existirem) antes de qualquer outra operação
    db.criar_tabelas()

    # Verifica se o usuário já está logado
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = None
    
    if 'login_sucesso' not in st.session_state:
        st.session_state.login_sucesso = False

    if not st.session_state.login_sucesso:
        # Se não estiver logado, exibe login ou cadastro
        escolha = st.selectbox("Escolha uma opção", ["Login", "Cadastro"])
        
        if escolha == "Login":
            login()
        elif escolha == "Cadastro":
            cadastro()
    else:
        # Se estiver logado, exibe a tela para adicionar transações
        adicionar_transacoes()

# Função de login
def login():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    
    if st.button("Login"):
        if db.verificar_usuario(usuario, senha):
            st.session_state.usuario_logado = usuario
            st.session_state.login_sucesso = True
            st.rerun()  # Atualiza a página
        else:
            st.error("Usuário ou senha inválidos!")

# Função de cadastro
def cadastro():
    st.title("Cadastro")
    novo_usuario = st.text_input("Novo Usuário")
    nova_senha = st.text_input("Nova Senha", type="password")
    
    if st.button("Cadastrar"):
        if db.usuario_existe(novo_usuario):
            st.error("Usuário já existe.")
        else:
            db.criar_usuario(novo_usuario, nova_senha)
            st.success("Cadastro realizado com sucesso!")
            st.session_state.usuario_logado = novo_usuario
            st.session_state.login_sucesso = True
            st.rerun()  # Atualiza a página

# Função para adicionar transações
def adicionar_transacoes():
    st.title("Adicionar Gastos/Receitas")
    
    tipo = st.selectbox("Tipo", ["Gasto", "Receita"])
    categoria = st.text_input("Categoria")
    valor = st.number_input("Valor", min_value=0.01, step=0.01)
    descricao = st.text_area("Descrição")
    
    if st.button("Adicionar"):
        if tipo and categoria and valor and descricao:
            db.adicionar_transacao(st.session_state.usuario_logado, tipo, categoria, valor, descricao)
            st.success("Transação adicionada com sucesso!")
        else:
            st.error("Por favor, preencha todos os campos.")

if __name__ == "__main__":
    main()
