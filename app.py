import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(page_title="Gerenciador de Orçamento", layout="wide")

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
                        moeda TEXT,
                        FOREIGN KEY(usuario) REFERENCES usuarios(usuario))''')
        c.execute('''CREATE TABLE IF NOT EXISTS metas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT,
                        categoria TEXT,
                        valor REAL,
                        periodo TEXT,
                        FOREIGN KEY(usuario) REFERENCES usuarios(usuario))''')
        c.execute("PRAGMA table_info(transacoes)")
        columns = [info[1] for info in c.fetchall()]
        if 'moeda' not in columns:
            c.execute("ALTER TABLE transacoes ADD COLUMN moeda TEXT DEFAULT 'BRL'")
            c.execute("UPDATE transacoes SET moeda = 'BRL' WHERE moeda IS NULL")

criar_tabelas()

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
        if os.path.exists("./img/Cyberfinancial.png"):
            st.image("./img/Cyberfinancial.png", width=600)
        else:
            st.warning("Imagem 'logo.png' não encontrada.")

def adicionar_transacao(usuario, tipo, categoria, valor, data, moeda):
    if valor <= 0:
        st.error("O valor deve ser maior que zero.")
        return False
    try:
        with sqlite3.connect('banco.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO transacoes (usuario, tipo, categoria, valor, data, moeda) VALUES (?, ?, ?, ?, ?, ?)",
                    (usuario, tipo, categoria, valor, data, moeda))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar transação: {e}")
        return False

def editar_transacao(transacao_id, usuario, tipo, categoria, valor, data, moeda):
    if valor <= 0:
        st.error("O valor deve ser maior que zero.")
        return False
    try:
        with sqlite3.connect('banco.db') as conn:
            c = conn.cursor()
            c.execute("UPDATE transacoes SET tipo = ?, categoria = ?, valor = ?, data = ?, moeda = ? WHERE id = ? AND usuario = ?",
                    (tipo, categoria, valor, data, moeda, transacao_id, usuario))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao editar transação: {e}")
        return False

def excluir_transacao(transacao_id, usuario):
    try:
        with sqlite3.connect('banco.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM transacoes WHERE id = ? AND usuario = ?", (transacao_id, usuario))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir transação: {e}")
        return False

def adicionar_meta(usuario, categoria, valor, periodo):
    if valor <= 0:
        st.error("O valor da meta deve ser maior que zero.")
        return False
    try:
        with sqlite3.connect('banco.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO metas (usuario, categoria, valor, periodo) VALUES (?, ?, ?, ?)",
                    (usuario, categoria, valor, periodo))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar meta: {e}")
        return False

def carregar_metas(usuario):
    with sqlite3.connect('banco.db') as conn:
        df = pd.read_sql_query("SELECT * FROM metas WHERE usuario = ?", conn, params=(usuario,))
    if df.empty:
        df = pd.DataFrame(columns=['id', 'usuario', 'categoria', 'valor', 'periodo'])
    return df

def converter_moeda(valor, moeda):
    taxas = {'BRL': 1.0, 'USD': 5.0, 'EUR': 6.0}
    return valor * taxas.get(moeda, 1.0)

def carregar_dados(usuario, filtro_periodo=None, mes=None, ano=None):
    with sqlite3.connect('banco.db') as conn:
        query = "SELECT * FROM transacoes WHERE usuario = ?"
        params = [usuario]
        if filtro_periodo == "Por mês" and mes and ano:
            query += " AND strftime('%m', data) = ? AND strftime('%Y', data) = ?"
            params.extend([f"{mes:02d}", str(ano)])
        elif filtro_periodo == "Por ano" and ano:
            query += " AND strftime('%Y', data) = ?"
            params.append(str(ano))
        df = pd.read_sql_query(query, conn, params=tuple(params))
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d', errors='coerce')
        if 'moeda' not in df.columns:
            df['moeda'] = 'BRL'
        df['valor_brl'] = df.apply(lambda x: converter_moeda(x['valor'], x['moeda']), axis=1)
    else:
        df = pd.DataFrame(columns=['id', 'usuario', 'tipo', 'categoria', 'valor', 'data', 'moeda', 'valor_brl'])
    return df

def exportar_dados(df, filtro_periodo, mes=None, ano=None):
    if df.empty:
        return None, None
    filename = "transacoes"
    if filtro_periodo == "Por mês" and mes and ano:
        filename += f"_{ano}_{mes:02d}"
    elif filtro_periodo == "Por ano" and ano:
        filename += f"_{ano}"
    filename += ".csv"
    csv_data = df.to_csv(index=False, encoding='utf-8')
    return csv_data.encode('utf-8'), filename

def calcular_tendencias(df):
    if df.empty:
        return pd.DataFrame(columns=['mes_ano']), pd.DataFrame(columns=['mes_ano'])
    df['mes_ano'] = df['data'].dt.to_period('M')
    tendencias = df.groupby(['mes_ano', 'categoria'])['valor_brl'].sum().unstack().fillna(0)
    tendencias_pct = tendencias.pct_change().replace([float('inf'), -float('inf')], 0).fillna(0) * 100
    tendencias.index = tendencias.index.astype(str)
    tendencias_pct.index = tendencias_pct.index.astype(str)
    return tendencias, tendencias_pct

def verificar_metas(df, metas, filtro_periodo, mes, ano):
    if metas.empty or df.empty:
        return []
    alertas = []
    df_despesas = df[df['tipo'] == 'Despesa'].copy()
    if filtro_periodo == "Por mês" and mes and ano:
        df_despesas = df_despesas[(df_despesas['data'].dt.month == mes) & (df_despesas['data'].dt.year == ano)]
    for _, meta in metas.iterrows():
        gastos = df_despesas[df_despesas['categoria'] == meta['categoria']]['valor_brl'].sum()
        if gastos > meta['valor']:
            alertas.append(f"Meta excedida para {meta['categoria']}: Gastos R${gastos:.2f} > Meta R${meta['valor']:.2f}")
    return alertas

def mostrar_dashboard(usuario):
    if 'mostrar_receitas' not in st.session_state:
        st.session_state.mostrar_receitas = True
    if 'mostrar_despesas' not in st.session_state:
        st.session_state.mostrar_despesas = True
    if 'mostrar_saldo' not in st.session_state:
        st.session_state.mostrar_saldo = True
    if 'graficos_selecionados' not in st.session_state:
        st.session_state.graficos_selecionados = ["Barplot", "Boxplot", "Scatterplot", "Histograma", "KDE Plot"]
    st.subheader("📊 Dashboard Financeiro")
    col1, col2 = st.columns(2)
    with col1:
        filtro_periodo = st.selectbox("Filtrar por período", ["Todas as transações", "Por mês", "Por ano"])
    with col2:
        st.multiselect("Gráficos a exibir", ["Barplot", "Boxplot", "Scatterplot", "Histograma", "KDE Plot"], 
                    default=st.session_state.graficos_selecionados, key="graficos_selecionados")
    mes = None
    ano = None
    if filtro_periodo == "Por mês":
        col3, col4 = st.columns(2)
        with col3:
            mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda x: datetime(2025, x, 1).strftime("%B"))
        with col4:
            ano = st.number_input("Ano", min_value=2000, max_value=2099, value=datetime.today().year)
    elif filtro_periodo == "Por ano":
        ano = st.number_input("Ano", min_value=2000, max_value=2099, value=datetime.today().year)
    df = carregar_dados(usuario, filtro_periodo, mes, ano)
    metas = carregar_metas(usuario)
    csv_data, filename = exportar_dados(df, filtro_periodo, mes, ano)
    if csv_data and filename:
        st.download_button(
            label="Exportar Transações (CSV)",
            data=csv_data,
            file_name=filename,
            mime="text/csv"
        )
    if df.empty:
        st.info("Nenhuma transação registrada para o período selecionado.")
        return
    st.subheader("Personalizar Métricas")
    col5, col6, col7 = st.columns(3)
    with col5:
        st.checkbox("Mostrar Total Receitas", value=st.session_state.mostrar_receitas, key="mostrar_receitas")
    with col6:
        st.checkbox("Mostrar Total Despesas", value=st.session_state.mostrar_despesas, key="mostrar_despesas")
    with col7:
        st.checkbox("Mostrar Saldo Atual", value=st.session_state.mostrar_saldo, key="mostrar_saldo")
    total_receitas = df[df["tipo"] == "Receita"]["valor_brl"].sum()
    total_despesas = df[df["tipo"] == "Despesa"]["valor_brl"].sum()
    saldo = total_receitas - total_despesas
    col8, col9, col10 = st.columns(3)
    if st.session_state.mostrar_receitas:
        col8.metric("💰 Total Receitas", f"R$ {total_receitas:.2f}")
    if st.session_state.mostrar_despesas:
        col9.metric("💸 Total Despesas", f"R$ {total_despesas:.2f}")
    if st.session_state.mostrar_saldo:
        col10.metric("📈 Saldo Atual", f"R$ {saldo:.2f}")
    alertas = verificar_metas(df, metas, filtro_periodo, mes, ano)
    for alerta in alertas:
        st.warning(alerta)
    df_despesas = df[df["tipo"] == "Despesa"].copy()
    if not df_despesas.empty:
        df_despesas['dia_semana'] = df_despesas['data'].dt.day_name()
        dia_mais_gasto = df_despesas.groupby('dia_semana')["valor_brl"].sum().idxmax()
        st.info(f"📅 Dia com mais gastos: **{dia_mais_gasto}**")
    tendencias, tendencias_pct = calcular_tendencias(df_despesas)
    if not tendencias.empty:
        st.subheader("📈 Análise de Tendências")
        st.write("Variações Percentuais Mensais por Categoria")
        st.dataframe(tendencias_pct, use_container_width=True)
        fig = px.line(tendencias, title="Tendências de Gastos por Categoria")
        st.plotly_chart(fig, use_container_width=True)
    if st.session_state.graficos_selecionados:
        st.subheader("Gráficos")
        for tipo_grafico in st.session_state.graficos_selecionados:
            if tipo_grafico == "Barplot":
                st.write("### 📊 Despesas por Categoria")
                categoria_despesas = df_despesas.groupby("categoria")["valor_brl"].sum().reset_index()
                fig = px.bar(categoria_despesas, x="categoria", y="valor_brl", title="Gastos por Categoria", color="valor_brl")
                st.plotly_chart(fig, use_container_width=True)
            elif tipo_grafico == "Boxplot":
                st.write("### 📈 Distribuição de Despesas por Categoria")
                fig = px.box(df_despesas, x="categoria", y="valor_brl", title="Distribuição de Despesas por Categoria")
                st.plotly_chart(fig, use_container_width=True)
            elif tipo_grafico == "Scatterplot":
                st.write("### 📍 Despesas ao Longo do Tempo")
                fig = px.scatter(df_despesas, x="data", y="valor_brl", color="categoria", title="Despesas ao Longo do Tempo")
                st.plotly_chart(fig, use_container_width=True)
            elif tipo_grafico == "Histograma":
                st.write("### 📶 Distribuição dos Valores de Despesas")
                fig = px.histogram(df_despesas, x="valor_brl", nbins=30, title="Histograma dos Valores de Despesas")
                st.plotly_chart(fig, use_container_width=True)
            elif tipo_grafico == "KDE Plot":
                st.write("### 📉 Estimativa de Densidade de Despesas")
                kde = go.Figure()
                kde.add_trace(go.Histogram(x=df_despesas["valor_brl"], histnorm='probability density', nbinsx=30, name="Histograma"))
                if not df_despesas["valor_brl"].empty:
                    values = df_despesas["valor_brl"]
                    hist, bins = np.histogram(values, bins=30, density=True)
                    bin_centers = (bins[:-1] + bins[1:]) / 2
                    sigma = values.std() / 5
                    kde_values = np.zeros_like(bin_centers)
                    for v in values:
                        kde_values += np.exp(-((bin_centers - v) ** 2) / (2 * sigma ** 2)) / (np.sqrt(2 * np.pi) * sigma)
                    kde_values /= len(values)
                    kde.add_trace(go.Scatter(x=bin_centers, y=kde_values, mode='lines', name="KDE"))
                kde.update_layout(title="Estimativa de Densidade de Despesas", xaxis_title="Valor (R$)", yaxis_title="Densidade")
                st.plotly_chart(kde, use_container_width=True)

def gerenciar_transacoes(usuario):
    st.subheader("🗂 Gerenciar Transações")
    df = carregar_dados(usuario)
    if df.empty:
        st.info("Nenhuma transação registrada.")
        return
    st.dataframe(df[['id', 'tipo', 'categoria', 'valor', 'data', 'moeda', 'valor_brl']], use_container_width=True)
    st.write("IDs válidos:", ", ".join(df['id'].astype(str).tolist()))
    transacao_id = st.number_input("ID da Transação", min_value=1, step=1)
    acao = st.selectbox("Ação", ["Editar", "Excluir"])
    if acao == "Editar":
        transacao = df[df['id'] == transacao_id]
        if transacao.empty:
            st.warning(f"Transação com ID {transacao_id} não encontrada. Escolha um ID válido.")
        else:
            with st.form("form_editar_transacao"):
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=0 if transacao['tipo'].iloc[0] == "Receita" else 1)
                categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Educação", "Salário", "Outros"], 
                                        index=["Alimentação", "Transporte", "Lazer", "Educação", "Salário", "Outros"].index(transacao['categoria'].iloc[0]))
                valor = st.number_input("Valor", min_value=0.01, value=float(transacao['valor'].iloc[0]), format="%.2f")
                data = st.date_input("Data", value=pd.to_datetime(transacao['data'].iloc[0]))
                moeda = st.selectbox("Moeda", ["BRL", "USD", "EUR"], index=["BRL", "USD", "EUR"].index(transacao['moeda'].iloc[0]))
                submit = st.form_submit_button("Salvar Alterações")
                if submit:
                    if editar_transacao(transacao_id, usuario, tipo, categoria, valor, data.strftime('%Y-%m-%d'), moeda):
                        st.success("Transação editada com sucesso!")
    elif acao == "Excluir":
        if st.button("Confirmar Exclusão"):
            if excluir_transacao(transacao_id, usuario):
                st.success("Transação excluída com sucesso!")
            else:
                st.error("Transação não encontrada ou erro ao excluir.")

def gerenciar_metas(usuario):
    st.subheader("🎯 Gerenciar Metas de Orçamento")
    with st.form("form_meta"):
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Educação", "Outros"])
        valor = st.number_input("Valor da Meta (R$)", min_value=0.01, format="%.2f")
        periodo = st.selectbox("Período", ["Mensal"])
        submit = st.form_submit_button("Adicionar Meta")
        if submit:
            if adicionar_meta(usuario, categoria, valor, periodo):
                st.success("Meta adicionada com sucesso!")
    metas = carregar_metas(usuario)
    if not metas.empty:
        st.write("Metas Atuais")
        st.dataframe(metas[['categoria', 'valor', 'periodo']], use_container_width=True)

def pagina_principal(usuario):
    st.sidebar.title(f"👤 Usuário: {usuario}")
    opcoes = st.sidebar.radio("Navegar", ["➕ Nova Transação", "📊 Ver Dashboard", "🗂 Gerenciar Transações", "🎯 Gerenciar Metas"])
    if opcoes == "➕ Nova Transação":
        st.subheader("➕ Adicionar Receita/Despesa")
        with st.form("form_transacao"):
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Educação", "Salário", "Outros"])
            valor = st.number_input("Valor", min_value=0.01, format="%.2f")
            data = st.date_input("Data", value=datetime.today())
            moeda = st.selectbox("Moeda", ["BRL", "USD", "EUR"])
            submit = st.form_submit_button("Salvar")
            if submit:
                if adicionar_transacao(usuario, tipo, categoria, valor, data.strftime('%Y-%m-%d'), moeda):
                    st.success("Transação adicionada com sucesso!")
    elif opcoes == "📊 Ver Dashboard":
        mostrar_dashboard(usuario)
    elif opcoes == "🗂 Gerenciar Transações":
        gerenciar_transacoes(usuario)
    elif opcoes == "🎯 Gerenciar Metas":
        gerenciar_metas(usuario)

if "usuario_logado" in st.session_state:
    pagina_principal(st.session_state['usuario_logado'])
else:
    tela_login()