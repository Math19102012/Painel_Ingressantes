import streamlit as st
from PIL import Image
import os
import pandas as pd
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

   # Caminho relativo considerando que a imagem está em src/assets
logo_path = os.path.join("src", "assets", "LOGO FECAP VERDE.png")

# Verifica se o arquivo existe antes de tentar abrir
if os.path.exists(logo_path):
    logo_image = Image.open(logo_path)
    st.sidebar.image(logo_image, width=200)
else:
    st.sidebar.warning(f"Logo não encontrada no caminho: {logo_path}")

# 🕓 Converter e extrair semestre
dados["Hora de início"] = pd.to_datetime(dados["Hora de início"], dayfirst=True, errors='coerce')

def extrair_semestre(data):
    if pd.isnull(data):
        return None
    ano = data.year
    semestre = 1 if data.month <= 6 else 2
    return f"{ano}-{semestre}"

dados["Semestre"] = dados["Hora de início"].apply(extrair_semestre)

# 🖱️ Filtros interativos
st.sidebar.title("Filtros de Análise")
st.sidebar.markdown("Use os filtros abaixo para segmentar os dados.")

# Filtro de curso (com opção de 'Todos')
curso = st.sidebar.selectbox("Selecione o Curso", ["Todos"] + list(dados["Qual o seu Curso?"].dropna().unique()))

# Filtro de período letivo (com opção de 'Todos')
periodo = st.sidebar.selectbox("Selecione o Período Letivo", ["Todos"] + list(dados["Qual é o seu período?"].dropna().unique()))

# Filtro de semestre (com opção de 'Todos')
semestres_disponiveis = sorted(dados["Semestre"].dropna().unique(), reverse=True)
semestre = st.sidebar.selectbox("Selecione o Semestre", ["Todos"] + semestres_disponiveis)


# 📄 Aplicar filtros no dataframe
df_filtrado = dados.copy()

if curso != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Qual o seu Curso?"] == curso]

if periodo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Qual é o seu período?"] == periodo]

if semestre != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Semestre"] == semestre]

    # Total de alunos filtrados
total_filtrados = len(df_filtrado)
st.sidebar.markdown(f"**Total de alunos que preencheram a pesquisa: {total_filtrados}**")


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
    options=["", "Indicação", "Pesquisa Online", "Redes Sociais", "Comunicação",
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
