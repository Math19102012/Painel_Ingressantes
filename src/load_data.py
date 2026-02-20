import pandas as pd
import streamlit as st
from .sharepoint_client import GraphClient, normalize_columns


def _client_from_secrets() -> GraphClient:
    s = st.secrets
    return GraphClient(
        tenant_id=s["GRAPH_TENANT_ID"],
        client_id=s["GRAPH_CLIENT_ID"],
        client_secret=s["GRAPH_CLIENT_SECRET"],
    )


@st.cache_data(ttl=60 * 15)  # cache de 15 minutos
def carregar_sharepoint(
    hostname: str,
    site_path: str,
    list_name: str,
) -> pd.DataFrame:

    try:
        client = _client_from_secrets()

        # 🔗 Conecta no SharePoint
        site_id = client.get_site_id(hostname, site_path)
        list_id = client.get_list_id_by_name(site_id, list_name)

        # 📥 Busca dados
        rows = client.fetch_list_items(site_id, list_id)

        if not rows:
            st.warning("Nenhum dado retornado da lista do SharePoint.")
            return pd.DataFrame()

        df = pd.DataFrame(rows)

        # 🔍 DEBUG: ver colunas brutas
        print("COLUNAS BRUTAS DO SHAREPOINT:")
        print(df.columns.tolist())

        # 🔄 Normaliza colunas
        df = normalize_columns(df)

        # 🔍 DEBUG: ver colunas após tratamento
        print("COLUNAS NORMALIZADAS:")
        print(df.columns.tolist())

        # 🧱 Garante colunas mínimas (evita quebra do app)
        colunas_esperadas = [
            "Hora de início",
            "Qual o seu Curso?",
            "Qual é o seu período?",
            "Renda Individual Mensal (R$)",
            "Renda Familiar Mensal (R$)",
            "Cargo",
        ]

        for col in colunas_esperadas:
            if col not in df.columns:
                df[col] = pd.NA

        # 📅 Converte datas
        if "Hora de início" in df.columns:
            df["Hora de início"] = pd.to_datetime(
                df["Hora de início"],
                errors="coerce",
                dayfirst=True
            )

        return df

    except Exception as e:
        st.error(f"Erro ao carregar dados do SharePoint: {e}")
        return pd.DataFrame()


def carregar_csv(caminho: str = "data/ingressantes.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(caminho)

        print("COLUNAS CSV:")
        print(df.columns.tolist())

        return df

    except Exception as e:
        st.error(f"Erro ao carregar CSV: {e}")
        return pd.DataFrame()
