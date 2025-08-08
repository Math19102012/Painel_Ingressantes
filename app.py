import streamlit as st
from PIL import Image
from src.load_data import carregar_csv
from src.visualizations import (
    grafico_renda,
    grafico_cargo,
    grafico_primeira_faculdade,
    grafico_canais_agrupados,
    grafico_subcategorias, 
    grafico_influencia_fatores,
    grafico_satisfacao_processos,
    grafico_categoria_outros_processos,
    grafico_subcategorias_processo,
    grafico_percepcao_qualidade,
    grafico_motivos_escolha,
    grafico_expectativas_curso,
    grafico_objetivos_profissionais,
    grafico_recomendacao
)

# ⚙️ Configurações iniciais
st.set_page_config(page_title="Análise Ingressantes")
st.title("📊 Análise Perfil dos Ingressantes")


# 📥 Carregar dados
try:
    dados = carregar_csv()
    st.success("Base de dados carregada com sucesso.")
except Exception as erro:
    st.error(f"Erro ao carregar a base de dados: {erro}")
    st.stop()

# 🎨 Adicionar o logo da FECAP
#logo_path = "C:\Users\40939444828\Desktop\Projetos\Auxiliar de Qualidade JR II\painel_ingressantes_fecap\src\assets\LOGO FECAP VERDE.png"

#st.sidebar.image(logo_image, width=200)  # Ajuste o tamanho conforme necessário

# 🖱️ Filtros interativos
st.sidebar.title("Filtros de Análise")
st.sidebar.markdown("Use os filtros abaixo para segmentar os dados.")

# Filtro de curso (com opção de 'Todos')
curso = st.sidebar.selectbox("Selecione o Curso", ["Todos"] + list(dados["Qual o seu Curso?"].unique()))

# Filtro de período letivo (com opção de 'Todos')
periodo = st.sidebar.selectbox("Selecione o Período Letivo", ["Todos"] + list(dados["Qual é o seu período?"].unique()))

# Total de alunos que preencheram a pesquisa
total_alunos = len(dados)
st.sidebar.markdown(f"**Total de alunos que preencheram a pesquisa: {total_alunos}**")

# Filtros aplicados no dataframe
if curso != "Todos" and periodo != "Todos":
    df_filtrado = dados[(dados["Qual o seu Curso?"] == curso) & (dados["Qual é o seu período?"] == periodo)]
elif curso != "Todos":
    df_filtrado = dados[dados["Qual o seu Curso?"] == curso]
elif periodo != "Todos":
    df_filtrado = dados[dados["Qual é o seu período?"] == periodo]
else:
    df_filtrado = dados  # Sem filtro, mostra todos os dados

# 📊 Visualizações com os dados filtrados
grafico_renda(df_filtrado)
grafico_cargo(df_filtrado)
grafico_primeira_faculdade(df_filtrado)
grafico_canais_agrupados(df_filtrado)

# 📌 Filtro dinâmico para ver subcategorias
st.markdown("---")
st.subheader("🔎 Exploração de Subcategorias por Canal de Comunicação")
categoria_detalhe = st.selectbox(
    "Deseja explorar alguma categoria mais a fundo?",
    options=[ "", "Indicação", "Pesquisa Online", "Redes Sociais", "Comunicação",
              "Eventos", "Reputação/Ranking", "Programas Públicos", "Convênios"]
)

if categoria_detalhe:
    grafico_subcategorias(df_filtrado, categoria_detalhe)

grafico_influencia_fatores(df_filtrado)
grafico_satisfacao_processos(df_filtrado)
grafico_categoria_outros_processos(df_filtrado)

st.markdown("---")
st.subheader("🔍 Subcategorias por Tipo de Instituição")
categoria_proc = st.selectbox(
    "Deseja explorar alguma categoria de instituição mais a fundo?",
    ["", "Privadas", "Federais", "Estaduais", "Não prestou", "Outro"]
)

if categoria_proc:
    grafico_subcategorias_processo(df_filtrado, categoria_proc)

grafico_percepcao_qualidade(df_filtrado)
grafico_motivos_escolha(df_filtrado)
grafico_expectativas_curso(df_filtrado)
grafico_objetivos_profissionais(df_filtrado)
grafico_recomendacao(df_filtrado)
