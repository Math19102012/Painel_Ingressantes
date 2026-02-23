import pandas as pd
import streamlit as st


@st.cache_data(ttl=60 * 15)  # cache de 15 minutos
def carregar_dados_local(
    caminho: str = "data/ingressantes_atualizado.csv"
) -> pd.DataFrame:

    try:
        df = pd.read_csv(caminho)
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        return pd.DataFrame()

    # Padroniza nomes de colunas
    df.columns = df.columns.str.strip()

    # Garante colunas esperadas pelo app
    for col in ["Hora de início", "Qual o seu Curso?", "Qual é o seu período?"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Converte datas
    if "Hora de início" in df.columns:
        df["Hora de início"] = pd.to_datetime(
            df["Hora de início"],
            errors="coerce",
            dayfirst=True
        )

    return df
