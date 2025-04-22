import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def mostrar_dashboard(df):
    st.header("📊 Dashboard de Análise")

    if df.empty:
        st.info("Nenhuma transação cadastrada ainda.")
        return

    df['data'] = pd.to_datetime(df['data'])
    df['dia_semana'] = df['data'].dt.day_name()

    # Métricas principais
    total_receitas = df[df['tipo'] == 'Receita']['valor'].sum()
    total_despesas = df[df['tipo'] == 'Despesa']['valor'].sum()
    saldo = total_receitas - total_despesas

    gasto_por_dia = df[df['tipo'] == 'Despesa'].groupby('dia_semana')['valor'].sum()
    dia_mais_gasto = gasto_por_dia.idxmax() if not gasto_por_dia.empty else "Nenhum dado"

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Receitas", f"R$ {total_receitas:.2f}")
    col2.metric("💸 Total Despesas", f"R$ {total_despesas:.2f}")
    col3.metric("📅 Dia com mais gastos", dia_mais_gasto)

    st.divider()
    st.subheader("📈 Visualização de Gráficos")

    tipo_grafico = st.selectbox(
        "Escolha o tipo de gráfico",
        ["Lineplot", "Histograma", "Gráfico de Barras", "Count Plot", "Scatterplot", "KDE Plot", "Boxplot"]
    )

    # Filtrar apenas despesas para os gráficos
    df_despesas = df[df['tipo'] == 'Despesa'].copy()

    if df_despesas.empty:
        st.warning("Você ainda não registrou despesas suficientes para gerar os gráficos.")
        return

    plt.figure(figsize=(10, 5))

    if tipo_grafico == "Lineplot":
        df_grouped = df_despesas.groupby('data')['valor'].sum().reset_index()
        sns.lineplot(data=df_grouped, x='data', y='valor')
        plt.title("Despesas ao longo do tempo")

    elif tipo_grafico == "Histograma":
        sns.histplot(df_despesas['valor'], bins=20, kde=True)
        plt.title("Distribuição dos valores das despesas")

    elif tipo_grafico == "Gráfico de Barras":
        df_grouped = df_despesas.groupby('categoria')['valor'].sum().sort_values(ascending=False).reset_index()
        sns.barplot(data=df_grouped, x='valor', y='categoria')
        plt.title("Total de despesas por categoria")

    elif tipo_grafico == "Count Plot":
        sns.countplot(data=df_despesas, y='categoria')
        plt.title("Frequência de categorias de despesas")

    elif tipo_grafico == "Scatterplot":
        sns.scatterplot(data=df_despesas, x='data', y='valor', hue='categoria')
        plt.title("Dispersão de despesas ao longo do tempo")

    elif tipo_grafico == "KDE Plot":
        sns.kdeplot(data=df_despesas['valor'], fill=True)
        plt.title("Distribuição de densidade das despesas")

    elif tipo_grafico == "Boxplot":
        sns.boxplot(data=df_despesas, x='categoria', y='valor')
        plt.title("Boxplot de despesas por categoria")
        plt.xticks(rotation=45)

    st.pyplot(plt.gcf())
