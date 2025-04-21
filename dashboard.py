import streamlit as st
import pandas as pd

def mostrar_dashboard(df):
    st.header("📊 Dashboard de Análise")

    if df.empty:
        st.info("Nenhuma transação cadastrada ainda.")
        return

    df['data'] = pd.to_datetime(df['data'])
    df['dia_semana'] = df['data'].dt.day_name()

    gasto_por_dia = df[df['tipo'] == 'Despesa'].groupby('dia_semana')['valor'].sum()
    dia_mais_gasto = gasto_por_dia.idxmax() if not gasto_por_dia.empty else "Nenhum dado"

    total_receitas = df[df['tipo'] == 'Receita']['valor'].sum()
    total_despesas = df[df['tipo'] == 'Despesa']['valor'].sum()
    saldo = total_receitas - total_despesas

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Receitas", f"R$ {total_receitas:.2f}")
    col2.metric("💸 Total Despesas", f"R$ {total_despesas:.2f}")
    col3.metric("📅 Dia de mais gastos", dia_mais_gasto)

    st.subheader("📈 Despesas ao longo do tempo")
    despesas = df[df['tipo'] == 'Despesa'].groupby('data')['valor'].sum().reset_index()
    st.line_chart(despesas.rename(columns={'data': 'index'}).set_index('index'))

    st.subheader("📊 Distribuição de categorias")
    categoria_despesa = df[df['tipo'] == 'Despesa'].groupby('categoria')['valor'].sum()
    if not categoria_despesa.empty:
        st.bar_chart(categoria_despesa)
    else:
        st.write("Sem dados para exibir.")
