import pandas as pd
import os

def carregar_csv():
    caminho_base = os.path.join("data", "ingressantes_atualizado.csv")
    try:
        df = pd.read_csv(caminho_base)
        return df
    except Exception as e:
        raise Exception(f"Erro ao carregar a base de dados: {e}")
