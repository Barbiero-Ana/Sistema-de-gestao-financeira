import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import plotly.express as px
import os

# Configuração da página
st.set_page_config(page_title="Gerenciador de Orçamento", layout="wide")

# Funções de banco de dados
def criar_tabelas():
    with sqlite3.connect('banco.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        usuario TEXT PRIMARY KEY,
                        senha TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS transacoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT,
                        tipo TEXT,
                        categoria TEXT,
                        valor REAL,
                        data TEXT,
                        FOREIGN KEY(usuario) REFERENCES usuarios(usuario))''')

criar_tabelas()

# Funções de autenticação
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(usuario, senha):
    with sqlite3.connect('banco.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, hash_senha(senha)))
        return c.fetchone()

def criar_usuario(usuario, senha):
    if not usuario or not senha:
        st.error("Usuário e senha não podem estar vazios.")
        return False
    if len(usuario) < 3:
        st.error("O usuário deve ter pelo menos 3 caracteres.")
        return False
    with sqlite3.connect('banco.db') as conn:
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, hash_senha(senha)))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            st.error("Usuário já existe.")
            return False
        except Exception as e:
            st.error(f"Erro ao criar usuário: {e}")
            return False

# Interface de login/cadastro
def tela_login():
    col1, col2 = st.columns([1, 1])

    with col1:
        st.title("💸 Gerenciador de Orçamento")
        menu = st.selectbox("Login / Criar Conta", ["Login", "Criar Conta"])

        if menu == "Login":
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                if verificar_login(usuario, senha):
                    st.session_state['usuario_logado'] = usuario
                    st.success(f"Bem-vindo, {usuario}!")
                else:
                    st.error("Usuário ou senha incorretos.")
        else:
            novo_usuario = st.text_input("Novo Usuário")
            nova_senha = st.text_input("Nova Senha", type="password")
            if st.button("Criar Conta"):
                if criar_usuario(novo_usuario, nova_senha):
                    st.success("Conta criada com sucesso! Faça login.")
                else:
                    st.error("Erro ao criar conta. Tente outro nome.")

    with col2:
        if os.path.exists("/Users/anabarbiero/Documents/GitHub/Sistema-de-gestao-financeira/Cyberfinancial.png"):
            st.image("/Users/anabarbiero/Documents/GitHub/Sistema-de-gestao-financeira/Cyberfinancial.png", width=600)
        else:
            st.warning("Imagem 'logo.png' não encontrada.")

# Funções de transação
def adicionar_transacao(usuario, tipo, categoria, valor, data):
    if valor <= 0:
        st.error("O valor deve ser maior que zero.")
        return False
    try:
        with sqlite3.connect('banco.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO transacoes (usuario, tipo, categoria, valor, data) VALUES (?, ?, ?, ?, ?)",
                      (usuario, tipo, categoria, valor, data))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar transação: {e}")
        return False

def carregar_dados(usuario):
    with sqlite3.connect('banco.db') as conn:
        df = pd.read_sql_query("SELECT * FROM transacoes WHERE usuario = ?", conn, params=(usuario,))
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d', errors='coerce')
    else:
        df = pd.DataFrame(columns=['id', 'usuario', 'tipo', 'categoria', 'valor', 'data'])
    return df

# Dashboard
def mostrar_dashboard(df):
    st.subheader("📊 Dashboard Financeiro")

    if df.empty:
        st.info("Nenhuma transação registrada ainda.")
        return

    total_receitas = df[df["tipo"] == "Receita"]["valor"].sum()
    total_despesas = df[df["tipo"] == "Despesa"]["valor"].sum()
    saldo = total_receitas - total_despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Receitas", f"R$ {total_receitas:.2f}")
    col2.metric("💸 Total Despesas", f"R$ {total_despesas:.2f}")
    col3.metric("📈 Saldo Atual", f"R$ {saldo:.2f}")

    # Dia com mais gastos
    df_despesas = df[df["tipo"] == "Despesa"].copy()
    if not df_despesas.empty:
        df_despesas['dia_semana'] = df_despesas['data'].dt.day_name()
        dia_mais_gasto = df_despesas.groupby('dia_semana')["valor"].sum().idxmax()
        st.info(f"📅 Dia com mais gastos: **{dia_mais_gasto}**")

    # Tipo de gráfico escolhido
    tipo_grafico = st.selectbox("Escolha o tipo de gráfico", ["Linha", "Barra", "Pizza"])

    if tipo_grafico == "Linha":
        st.write("### 📉 Despesas ao Longo do Tempo")
        df_plot = df[df["tipo"] == "Despesa"].groupby("data")["valor"].sum().reset_index()
        fig = px.line(df_plot, x="data", y="valor", title="Evolução das Despesas")
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Barra":
        st.write("### 📊 Despesas por Categoria")
        categoria_despesas = df[df["tipo"] == "Despesa"].groupby("categoria")["valor"].sum().reset_index()
        fig = px.bar(categoria_despesas, x="categoria", y="valor", title="Gastos por Categoria", color="valor")
        st.plotly_chart(fig, use_container_width=True)

    elif tipo_grafico == "Pizza":
        st.write("### 🥧 Distribuição das Despesas")
        categoria_despesas = df[df["tipo"] == "Despesa"].groupby("categoria")["valor"].sum().reset_index()
        fig = px.pie(categoria_despesas, names='categoria', values='valor', title='Distribuição por Categoria')
        st.plotly_chart(fig, use_container_width=True)

# Página principal após login
def pagina_principal(usuario):
    st.sidebar.title(f"👤 Usuário: {usuario}")
    opcoes = st.sidebar.radio("Navegar", ["➕ Nova Transação", "📊 Ver Dashboard"])

    if opcoes == "➕ Nova Transação":
        st.subheader("➕ Adicionar Receita/Despesa")
        with st.form("form_transacao"):
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Educação", "Salário", "Outros"])
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
            data = st.date_input("Data", value=datetime.today())
            submit = st.form_submit_button("Salvar")
            if submit:
                if adicionar_transacao(usuario, tipo, categoria, valor, data.strftime('%Y-%m-%d')):
                    st.success("Transação adicionada com sucesso!")

    elif opcoes == "📊 Ver Dashboard":
        df = carregar_dados(usuario)
        mostrar_dashboard(df)

# Execução principal
if "usuario_logado" in st.session_state:
    pagina_principal(st.session_state['usuario_logado'])
else:
    tela_login()