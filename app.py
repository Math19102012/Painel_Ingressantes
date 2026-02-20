import os
import pandas as pd
import streamlit as st
from PIL import Image

from src.load_data import carregar_sharepoint
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
    grafico_recomendacao,
)

# ⚙️ Configuração inicial
st.set_page_config(page_title="Análise Ingressantes")
st.title("📊 Análise Perfil dos Ingressantes")

# 📥 Carregar dados do SharePoint
try:
    df = carregar_sharepoint(
        hostname=st.secrets["SHAREPOINT_HOSTNAME"],
        site_path=st.secrets["SHAREPOINT_SITE_PATH"],
        list_name=st.secrets["SHAREPOINT_LIST_NAME"],
    )

    st.success("Base carregada da API do SharePoint ✅")

    # 🔥 DEBUG CRÍTICO (NÃO REMOVER AGORA)
    st.write("### 🔍 Colunas carregadas do SharePoint:")
    st.write(df.columns.tolist())

except Exception as erro:
    st.error(f"Erro ao carregar da API: {erro}")
    st.stop()

# 🖼 Logo
logo_path = os.path.join("src", "assets", "LOGO FECAP VERDE.png")
if os.path.exists(logo_path):
    st.sidebar.image(Image.open(logo_path), width=200)
else:
    st.sidebar.warning(f"Logo não encontrada: {logo_path}")

# 🕓 Tratamento de datas
if "Hora de início" in df.columns:
    df["Hora de início"] = pd.to_datetime(df["Hora de início"], errors="coerce", dayfirst=True)

    def extrair_semestre(data):
        if pd.isnull(data):
            return None
        return f"{data.year}-{1 if data.month <= 6 else 2}"

    df["Semestre"] = df["Hora de início"].apply(extrair_semestre)
else:
    df["Semestre"] = None

# 🖱️ Filtros
st.sidebar.title("Filtros de Análise")

curso_col = "Qual o seu Curso?"
periodo_col = "Qual é o seu período?"

curso = st.sidebar.selectbox(
    "Selecione o Curso",
    ["Todos"] + list(df[curso_col].dropna().unique()) if curso_col in df.columns else ["Todos"]
)

periodo = st.sidebar.selectbox(
    "Selecione o Turno",
    ["Todos"] + list(df[periodo_col].dropna().unique()) if periodo_col in df.columns else ["Todos"]
)

semestres_disponiveis = sorted(df["Semestre"].dropna().unique(), reverse=True) if "Semestre" in df.columns else []
semestre = st.sidebar.selectbox("Período Letivo", ["Todos"] + semestres_disponiveis)

# 📄 Aplicar filtros
df_filtrado = df.copy()

if curso != "Todos" and curso_col in df.columns:
    df_filtrado = df_filtrado[df_filtrado[curso_col] == curso]

if periodo != "Todos" and periodo_col in df.columns:
    df_filtrado = df_filtrado[df_filtrado[periodo_col] == periodo]

if semestre != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Semestre"] == semestre]

st.sidebar.markdown(f"**Total de respostas: {len(df_filtrado)}**")

# 📊 GRÁFICOS (com proteção contra erro)
def safe_plot(func, df):
    try:
        func(df)
    except Exception as e:
        st.warning(f"Erro no gráfico {func.__name__}: {e}")

safe_plot(grafico_renda, df_filtrado)
safe_plot(grafico_cargo, df_filtrado)
safe_plot(grafico_primeira_faculdade, df_filtrado)
safe_plot(grafico_canais_agrupados, df_filtrado)

st.markdown("---")

# 🔎 Subcategorias
categoria_detalhe = st.selectbox(
    "Explorar categoria:",
    ["", "Indicação", "Pesquisa Online", "Redes Sociais", "Comunicação",
     "Eventos", "Reputação/Ranking", "Programas Públicos", "Convênios"]
)

if categoria_detalhe:
    safe_plot(lambda df: grafico_subcategorias(df, categoria_detalhe), df_filtrado)

# 🔥 Esses estavam quebrando — agora protegidos
safe_plot(grafico_influencia_fatores, df_filtrado)
safe_plot(grafico_satisfacao_processos, df_filtrado)
safe_plot(grafico_categoria_outros_processos, df_filtrado)

st.markdown("---")

# 🔍 Subcategorias por instituição
categoria_proc = st.selectbox(
    "Explorar tipo de instituição:",
    ["", "Privadas", "Federais", "Estaduais", "Não prestou", "Outro"]
)

if categoria_proc:
    safe_plot(lambda df: grafico_subcategorias_processo(df, categoria_proc), df_filtrado)

safe_plot(grafico_percepcao_qualidade, df_filtrado)
safe_plot(grafico_motivos_escolha, df_filtrado)
safe_plot(grafico_expectativas_curso, df_filtrado)
safe_plot(grafico_objetivos_profissionais, df_filtrado)
safe_plot(grafico_recomendacao, df_filtrado)
