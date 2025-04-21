# desenvolver o gerenciador de vida financeira e implementar com streamlit + gráficos interativos do matplotlib

import time
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title='Gestão de custos', layout='wide')
st.markdown('--------------')

st.header('Insira uma nova despesa: ')

col1, col2 = st.columns(2)

with col1:
    st.subheader('basic inputs de teste')

    nome = st.text_input('Digite seu nome: ', placeholder='Seu nome aqui')

    idade = st.number_input('Digite sua idade: ')


    altura = st.slider('Sua altura (metros): ', 1.0, 2.5, 1.7)

    profissao = st.selectbox(
        'Selecione sua profissão:',
        ['Desenvolvedor', 'Cientista de dados', 'Designer', 'Outros']
    )

    yes = st.checkbox('Concordo com os termos de uso')

    genero = st.radio('Gênero: ', ['Masculino', 'Feminino', 'Prefiro não informar'])

    if st.button('Salvar dados'):
        st.session_state.dados_usuarios = {
            'Nome': nome,
            'Idade': idade,
            'Altura': altura,
            'Profissão': profissao,
            'Concordou': yes,
            'Gênero': genero
        }
        st.success('Dados salvos com sucesso')

with col2:
    st.subheader('Resultados')
    if 'dados_usuarios' in st.session_state:
        st.write('===== dados salvos e armazenados ====')
        st.json(st.session_state.dados_usuarios)
    else:
        st.warning('Nenhum dado salvo ainda....')

    arqv = st.file_uploader('Carregar arquivo .CSV', type='csv')
    if arqv is not None:
        dados_csv = pd.read_csv(arqv)
        st.write('Pré-visualização do arquivo:')
        st.dataframe(dados_csv.head())

    cor = st.color_picker('Escolha uma cor:', '#00FF00')
    st.write(f'Cor selecionada: {cor}')

    comentario = st.text_area('Deixe seu comentário aqui...: ')
    if comentario:
        st.write('Seu comentário:')
        st.code(comentario)

st.header('2. Outros componentes úteis')

st.subheader('Progress bar')
progresso = st.progress(0)
for i in range(100):
    progresso.progress(i + 1)

if st.button('Processar dados'):
    with st.spinner('Processando...'):
        time.sleep(2)
        st.balloons()

with st.expander('Clique aqui para ver informações adicionais'):
    st.write("""
        Este é um conteúdo adicional que pode ser mostrado ou ocultado
            - Item 1
            - Item 2
            - Item 3
            - Item 4
            """)

st.subheader('métricas')
col1, col2, col3 = st.columns(3)
col1.metric('Temperatura', '25 ºC', '1.2 ºC')
col2.metric('Velocidade', '120 km/h', '-8 km/h')
col3.metric('Umidade', '65%', '4%')

st.header('3. Trabalhando com DataFrames')

data = pd.DataFrame({
    'Data': pd.date_range(start='2025-04-17', periods=100),
    'Valor': np.random.randn(100).cumsum(),
    'Categoria': np.random.choice(['A', 'B', 'C'], 100)
})

st.subheader('Dataframe de exemplo: ')
st.download_button(
    label='Baixar CSV',
    data=data.to_csv(index=False).encode('utf-8'),
    file_name='Dados_exemplo.csv',
    mime='text/csv'
)


st.header('4. Visualização com Seaborn')

tab1, tab2, tab3 = st.tabs(['Linha', 'Barras', 'Boxplot'])

with tab1:
    st.subheader('Gráfico de linha')
    fig, ax = plt.subplots()
    sns.lineplot(data=data, x='Data', y='Valor', ax=ax)
    st.pyplot(fig)
    st.markdown('*Gráfico mostrando a evolução temporal dos valores*')


with tab2:
    st.subheader('Gráfico de barras')
    fig, ax = plt.subplots()
    sns.barplot(data=data, x='Data', y='Valor', ax=ax)
    st.pyplot(fig)
    st.markdown('*Média de valores por categoria*')

with tab3:
    st.subheader('Gráfico de boxplot')
    fig, ax = plt.subplots()
    sns.boxplot(data=data, x='Categoria', y='Valor', ax=ax)
    st.pyplot(fig)
    st.markdown('*Distribuição dos valores porn categoria*')


st.header('5. Componentes interativos')
col1, col2 = st.columns(2)

with col1:
    st.subheader('Filtro de dados')
    min_val = int(data['Valor'].min())
    max_val = int(data['Valor'].max())
    selected_range = st.slider(
        'Selecione o intervalo de valores:',
        min_val, max_val,(min_val, max_val)
    )

    filtered_data = data[
        (data['Valor'] >= selected_range[0]) &
        (data['Valor'] <= selected_range[1])
    ]
    st.write(f'Registros filtrados: {len(filtered_data)}')

with col2:
    st.subheader('Seleção de categoria')

    selected_category = st.selectbox(
        'Escolha uma categoria',
        data['Categoria'].unique()
    )
    st.write(data[data['Categoria'] == selected_category])

st.header('6. Organização do Layout')

st.subheader('Usando colunas')

col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Total de registos', len(data))

with col2:
    st.metric('Média de valores', f"{data['Valor'].mean():.2f}")

with col3:
    st.metric('Valor máximo', f"{data['Valor'].max():.2f}")

st.subheader('Expanders para organização')
with st.expander('Controle de exibição'):
    st.write(data)


st.subheader('Controle de exibição')

if st.checkbox('Mostrar informações estatisticas'):
    st.write(data.describe())