import pandas as pd
import ast
from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st


nltk.download('stopwords')

def grafico_renda(df: pd.DataFrame):
    st.subheader("💰 Perfil Socioeconômico")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Renda Individual Mensal (R$)**")
        coluna_individual = [col for col in df.columns if "renda individual" in col.lower()]
        if coluna_individual:
            plot_renda(df, coluna_individual[0])
        else:
            st.warning("Coluna de Renda Individual não encontrada.")

    with col2:
        st.markdown("**Renda Familiar Mensal (R$)**")
        coluna_familiar = [col for col in df.columns if "renda familiar" in col.lower()]
        if coluna_familiar:
            plot_renda(df, coluna_familiar[0])
        else:
            st.warning("Coluna de Renda Familiar não encontrada.")


def plot_renda(df, coluna):
    renda_counts = df[coluna].value_counts(dropna=True).sort_index()
    total = renda_counts.sum()
    renda_percent = (renda_counts / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(6, 4))
    renda_percent.sort_values().plot(kind='barh', ax=ax, color="#4E79A7", edgecolor="black")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Faixa de Renda")
    ax.set_title("Distribuição por Faixa de Renda")
    for i, v in enumerate(renda_percent.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
    st.pyplot(fig)

def grafico_cargo(df: pd.DataFrame):
    st.subheader("👔 Situação Profissional dos Ingressantes")

    # Corrigir nome da coluna
    nome_coluna_cargo = [col for col in df.columns if "nível hierárquico" in col.lower()]
    if not nome_coluna_cargo:
        st.warning("Coluna de cargo não encontrada na base de dados.")
        return

    col = nome_coluna_cargo[0]
    cargos_raw = df[col].dropna().astype(str).str.strip().str.lower()

    # Agrupamento manual de categorias similares
    mapeamento = {
        "estagiario": "Estágio",
        "estagiária": "Estágio",
        "estágio": "Estágio",
        "trainee": "Trainee",
        "analista": "Analista",
        "assistente": "Assistente",
        "gerente": "Gestão",
        "coordenação": "Gestão",
        "coordenador": "Gestão",
        "supervisor": "Gestão",
        "diretor": "Alta Liderança",
        "presidente": "Alta Liderança",
        "sem trabalho": "Não trabalha",
        "não trabalha": "Não trabalha",
        "desempregado": "Não trabalha"
    }

    # Classificação por tema
    def categorizar_cargo(c):
        for chave, valor in mapeamento.items():
            if chave in c:
                return valor
        return c.title()

    cargos_limpos = cargos_raw.apply(categorizar_cargo)
    contagem = cargos_limpos.value_counts()
    total = contagem.sum()
    porcentagem = (contagem / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(6, 4))
    porcentagem.sort_values().plot(kind='barh', ax=ax, color="#F28E2B", edgecolor="black")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Cargo")
    ax.set_title("Distribuição por Nível Hierárquico")
    for i, v in enumerate(porcentagem.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
    st.pyplot(fig)

def grafico_primeira_faculdade(df: pd.DataFrame):
    st.subheader("🎓 Primeira Experiência no Ensino Superior")

    col = [c for c in df.columns if "primeira experiência" in c.lower()]
    if not col:
        st.warning("Coluna de primeira experiência não encontrada.")
        return

    coluna = col[0]
    dados = df[coluna].dropna().str.strip()
    contagem = dados.value_counts()
    total = contagem.sum()
    percentual = (contagem / total * 100).round(1)

    fig, ax = plt.subplots()
    cores = ["#59A14F", "#EDC948", "#E15759"]
    ax.pie(percentual, labels=percentual.index, autopct='%1.1f%%', startangle=140, colors=cores, textprops={'fontsize': 10})
    ax.set_title("Primeira Faculdade?")
    st.pyplot(fig)

def grafico_canais_agrupados(df: pd.DataFrame):
    st.subheader("🧭 Canais de Descoberta da FECAP (Agrupado por Categoria)")

    col = [c for c in df.columns if "quais meios" in c.lower()]
    if not col:
        st.warning("Coluna de meios de comunicação não encontrada.")
        return

    coluna = col[0]
    respostas = df[coluna].dropna().astype(str)

    def limpar_item(item):
        return (
            item.strip()
            .lower()
            .replace("[", "")
            .replace("]", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )

    todas_respostas = []
    for linha in respostas:
        for item in linha.split(";"):
            item_limpo = limpar_item(item)
            if item_limpo:
                todas_respostas.append(item_limpo)

    categorias = {
        "Indicação": ["família", "amigos", "professores de ensino médio", "professores de cursinho", "profissionais de mercado"],
        "Pesquisa Online": ["pesquisa na internet (google)", "site da fecap"],
        "Redes Sociais": ["facebook", "instagram", "youtube", "twitter", "linkedin"],
        "Comunicação": ["anúncio na rádio", "anúncios no metrô", "e-mails de divulgação"],
        "Eventos": ["eventos no seu colégio", "feiras estudantis"],
        "Reputação/Ranking": ["rankings especializados (ex.: guia da faculdade)", "matérias na imprensa"],
        "Programas Públicos": ["prouni"],
        "Convênios": ["trabalho na instituição", "convênio com a aasp (oab)", "convênio com empresa em que eu trabalho"]
    }

    def categorizar(item):
        for categoria, termos in categorias.items():
            if item in termos:
                return categoria
        return "Outros"

    categorizados = [categorizar(resposta) for resposta in todas_respostas]
    contagem = pd.Series(categorizados).value_counts()
    total = contagem.sum()
    percentual = (contagem / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(7, 5))
    percentual.sort_values().plot(kind='barh', ax=ax, color="#76B7B2", edgecolor="black")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Categoria")
    ax.set_title("Canais de Descoberta da FECAP (Agrupados)")
    for i, v in enumerate(percentual.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
    st.pyplot(fig)

def grafico_subcategorias(df: pd.DataFrame, categoria_desejada: str):
    st.subheader(f"🔍 Subcategorias em '{categoria_desejada}'")

    col = [c for c in df.columns if "quais meios" in c.lower()]
    if not col:
        st.warning("Coluna de meios de comunicação não encontrada.")
        return

    coluna = col[0]
    respostas = df[coluna].dropna().astype(str)

    def limpar_item(item):
        return (
            item.strip()
            .lower()
            .replace("[", "")
            .replace("]", "")
            .replace('"', "")
            .replace("'", "")
            .strip()
        )

    todas_respostas = []
    for linha in respostas:
        for item in linha.split(";"):
            item_limpo = limpar_item(item)
            if item_limpo:
                todas_respostas.append(item_limpo)

    categorias = {
        "Indicação": ["família", "amigos", "professores de ensino médio", "professores de cursinho", "profissionais de mercado"],
        "Pesquisa Online": ["pesquisa na internet (google)", "site da fecap"],
        "Redes Sociais": ["facebook", "instagram", "youtube", "twitter", "linkedin"],
        "Comunicação": ["anúncio na rádio", "anúncios no metrô", "e-mails de divulgação"],
        "Eventos": ["eventos no seu colégio", "feiras estudantis"],
        "Reputação/Ranking": ["rankings especializados (ex.: guia da faculdade)", "matérias na imprensa"],
        "Programas Públicos": ["prouni"],
        "Convênios": ["trabalho na instituição", "convênio com a aasp (oab)", "convênio com empresa em que eu trabalho"]
    }

    termos = categorias.get(categoria_desejada)
    if not termos:
        st.info("Categoria ainda sem termos definidos.")
        return

    subcontagem = [resp for resp in todas_respostas if resp in termos]
    if not subcontagem:
        st.info("Nenhuma ocorrência encontrada para essa categoria.")
        return

    contagem = pd.Series(subcontagem).value_counts()
    total = contagem.sum()
    percentual = (contagem / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(6, 4))
    percentual.sort_values().plot(kind='barh', ax=ax, color="#FF9DA7", edgecolor="black")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Subcategoria")
    ax.set_title(f"Detalhamento da Categoria: {categoria_desejada}")
    for i, v in enumerate(percentual.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
    st.pyplot(fig)

def grafico_influencia_fatores(df: pd.DataFrame):
    st.subheader("✨ Fatores que Influenciaram a Escolha pela FECAP")

    colunas_influencia = [
        "Proximidade da residência",
        "Proximidade do trabalho",
        "Recomendações de amigos",
        "Recomendações de alunos e ex-alunos",
        "Recomendações de familiares",
        "Recomendações de Professores de Ensino Médio-Básico",
        "Recomendações de Profissionais de Mercado",
        "Informações no Facebook",
        "Informações no Instagram",
        "Informações no Youtube",
        "Informações no Linkedin",
        "Corpo Docente (Professores da FECAP)",
        "Matriz Curricular do Curso",
        "Resultados no ENADE-MEC",
        "Resultados em Rankings (ex: Guia da Faculdade)",
        "Preço do Curso",
        "Instalações e Infraestrutura",
        "Serviços de atendimento e recepção",
        "Prestígio do Curso",
        "Prestígio da Marca FECAP"
    ]

    escala = [
        "Influenciou muito negativamente",
        "Influenciou negativamente",
        "Neutro",
        "Influenciou positivamente",
        "Influenciou muito positivamente"
    ]

    dados_plot = pd.DataFrame()

    for coluna in colunas_influencia:
        if coluna in df.columns:
            contagem = df[coluna].value_counts().reindex(escala, fill_value=0)
            dados_plot[coluna] = contagem

    dados_plot = dados_plot.T
    dados_plot.index.name = "Fator"
    dados_plot.reset_index(inplace=True)

    fig = go.Figure()
    for cat in escala:
        fig.add_trace(go.Bar(
            y=dados_plot["Fator"],
            x=dados_plot[cat],
            name=cat,
            orientation="h"
        ))

    fig.update_layout(
        barmode="stack",
        colorway=["#8B0000", "#FF9999", "#A9A9A9", "#90EE90", "#006400"],
        xaxis_title="Número de Respostas",
        yaxis_title="Fatores",
        title="Influência dos Fatores na Escolha pela FECAP",
        height=800,
        legend_title="Tipo de Influência"
    )

    st.plotly_chart(fig, use_container_width=True)

def grafico_satisfacao_processos(df: pd.DataFrame):
    st.subheader("📞 Satisfação com os Processos de Relacionamento")

    colunas_satisfacao = [
        "Informações da FECAP no Site",
        "Informações do Curso escolhido no site",
        "Atendimento Telefônico quando eu liguei para a FECAP",
        "Atendimento Telefônico quando recebi telefonemas da FECAP",
        "Atendimento pelo WhatsApp",
        "Atendimento por Mídias Sociais",
        "Atendimento por email (sejafecap@fecap.br)",
        "Visita Guiada pelo Campus",
        "Ficha de inscrição do processo seletivo (internet)",
        "Organização da FECAP no dia do Vestibular",
        "Qualidade da prova de vestibular",
        "Acesso aos resultados do processo seletivo (aprovação)",
        "Atendimento na Matrícula",
        "Atendimento no Departamento Financeiro"
    ]

    escala = [
        "Não utilizei",
        "Muito insatisfeito",
        "Insatisfeito",
        "Neutro",
        "Satisfeito",
        "Muito satisfeito"
    ]

    dados_plot = pd.DataFrame()

    for coluna in colunas_satisfacao:
        if coluna in df.columns:
            contagem = df[coluna].value_counts().reindex(escala, fill_value=0)
            dados_plot[coluna] = contagem

    dados_plot = dados_plot.T
    dados_plot.index.name = "Processo"
    dados_plot.reset_index(inplace=True)

    fig = go.Figure()
    for cat in escala:
        fig.add_trace(go.Bar(
            y=dados_plot["Processo"],
            x=dados_plot[cat],
            name=cat,
            orientation="h"
        ))

    fig.update_layout(
        barmode="stack",
        colorway=[
        "#87CEFA",  # Muito satisfeito - verde escuro
        "#8B0000",  # Satisfeito - verde claro
        "#FF9999",  # Neutro - cinza
        "#A9A9A9",  # Insatisfeito - vermelho claro
        "#90EE90",  # Muito insatisfeito - vermelho escuro
        "#006400"   # Não utilizei - azul claro
    ],
        xaxis_title="Número de Respostas",
        yaxis_title="Processo de Relacionamento",
        title="Satisfação com os Processos de Relacionamento da FECAP",
        height=900,
        legend_title="Nível de Satisfação"
    )

    st.plotly_chart(fig, use_container_width=True)

def grafico_categoria_outros_processos(df: pd.DataFrame):
    st.subheader("🏫 Tipo de Instituições em que os Ingressantes Também Prestaram Processo Seletivo")

    col = [c for c in df.columns if "processo seletivo em quais instituições" in c.lower()]
    if not col:
        st.warning("Coluna do processo seletivo em outras instituições não foi encontrada.")
        return

    coluna = col[0]
    respostas = df[coluna].dropna().astype(str)

    # Mapeamento de categorias
    categorias = {
        "Federais": ["Federais (SISU)"],
        "Estaduais": ["USP (Fuvest)", "Unesp", "Unicamp"],
        "Privadas": [
            "FGV", "Insper", "FAAP", "Mackenzie", "PUC", "FEI", "FIAP",
            "Anhembi", "FMU", "Uninove", "UNIP", "Anhanguera", "São Judas", "Unicid"
        ],
        "Não prestou": ["Não Prestei Processo Seletivo em Outra Instituição"],
        "Outro": ["Outro"]
    }

    def categorizar(inst):
        for categoria, lista in categorias.items():
            if inst in lista:
                return categoria
        return "Outro"

    todas_instituicoes = []
    for linha in respostas:
        try:
            if linha.startswith("[") and linha.endswith("]"):
                lista = ast.literal_eval(linha)
                for inst in lista:
                    inst_limpo = inst.strip()
                    if inst_limpo:
                        todas_instituicoes.append(inst_limpo)
            else:
                for inst in linha.split(";"):
                    inst_limpo = inst.strip()
                    if inst_limpo:
                        todas_instituicoes.append(inst_limpo)
        except:
            continue

    categorias_final = [categorizar(inst) for inst in todas_instituicoes]
    contagem = pd.Series(categorias_final).value_counts()
    total = contagem.sum()
    percentual = (contagem / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(6, 4))
    percentual.sort_values().plot(kind='barh', ax=ax, color="#59A14F", edgecolor="black")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Categoria")
    ax.set_title("Categorias de Instituições Prestadas Além da FECAP")
    for i, v in enumerate(percentual.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
    st.pyplot(fig)

def grafico_subcategorias_processo(df: pd.DataFrame, categoria_desejada: str):
    st.subheader(f"🔍 Subcategorias em '{categoria_desejada}'")

    col = [c for c in df.columns if "processo seletivo em quais instituições" in c.lower()]
    if not col:
        st.warning("Coluna do processo seletivo não encontrada.")
        return

    coluna = col[0]
    respostas = df[coluna].dropna().astype(str)

    categorias = {
        "Federais": ["Federais (SISU)"],
        "Estaduais": ["USP (Fuvest)", "Unesp", "Unicamp"],
        "Privadas": [
            "FGV", "Insper", "FAAP", "Mackenzie", "PUC", "FEI", "FIAP",
            "Anhembi", "FMU", "Uninove", "UNIP", "Anhanguera", "São Judas", "Unicid"
        ],
        "Não prestou": ["Não Prestei Processo Seletivo em Outra Instituição"],
        "Outro": ["Outro"]
    }

    import ast
    todas_respostas = []
    for linha in respostas:
        try:
            if linha.startswith("[") and linha.endswith("]"):
                lista = ast.literal_eval(linha)
                for inst in lista:
                    todas_respostas.append(inst.strip())
            else:
                for inst in linha.split(";"):
                    todas_respostas.append(inst.strip())
        except:
            continue

    # Obter termos associados à categoria
    termos_categoria = categorias.get(categoria_desejada, [])
    subrespostas = [resp for resp in todas_respostas if resp in termos_categoria]

    if not subrespostas:
        st.info("Nenhuma ocorrência encontrada para essa categoria.")
        return

    contagem = pd.Series(subrespostas).value_counts()
    total = contagem.sum()
    percentual = (contagem / total * 100).round(1)

    fig, ax = plt.subplots(figsize=(6, 4))
    percentual.sort_values().plot(kind='barh', ax=ax, color="#F28E2B", edgecolor="black")
    ax.set_xlabel("Percentual (%)")
    ax.set_ylabel("Instituição")
    ax.set_title(f"Instituições dentro da categoria: {categoria_desejada}")
    for i, v in enumerate(percentual.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va='center')
    st.pyplot(fig)

def grafico_percepcao_qualidade(df: pd.DataFrame):
    st.subheader("🏛️ Percepção de Qualidade das Instituições de Ensino")

    # Identificar colunas que são as instituições
    colunas_ies = [
        "USP", "FGV", "Insper", "FAAP", "Mackenzie", "PUC", "FECAP",
        "FEI", "FIAP", "Anhembi", "FMU", "Uninove", "UNIP", "Anhanguera"
    ]

    escala = [
        "Não conheço",
        "Péssima",
        "Ruim",
        "Regular",
        "Ótima",
        "Excelente"
    ]

    dados_plot = pd.DataFrame()

    for coluna in colunas_ies:
        if coluna in df.columns:
            contagem = df[coluna].value_counts().reindex(escala, fill_value=0)
            dados_plot[coluna] = contagem

    dados_plot = dados_plot.T
    dados_plot.index.name = "Instituição"
    dados_plot.reset_index(inplace=True)

    # Construir gráfico de barras empilhadas
    fig = go.Figure()
    for cat in escala:
        fig.add_trace(go.Bar(
            y=dados_plot["Instituição"],
            x=dados_plot[cat],
            name=cat,
            orientation="h"
        ))

    fig.update_layout(
        barmode="stack",
        colorway=[
        "#D3D3D3",  # Não conheço
        "#8B0000",  # Péssima
        "#FF9999",  # Ruim
        "#A9A9A9",  # Regular
        "#90EE90",  # Ótima
        "#006400"   # Excelente
        ],
        xaxis_title="Número de Respostas",
        yaxis_title="Instituição de Ensino",
        title="Percepção de Qualidade das Instituições de Ensino",
        height=900,
        legend_title="Nível de Qualidade"
    )

    st.plotly_chart(fig, use_container_width=True)

def limpar_texto(texto, tipo="motivos"):
    # Lista de stopwords em português
    stop_words = set(stopwords.words("portuguese"))
    
    # Palavras indesejadas para motivos de escolha
    palavras_indesejadas_motivos = {
        "fecap", "curso", "faculdade", "ensino", "boa", "gostei", "ano", "atenção", "outra", "alta", "dentro",
        "pesquisei", "achei", "Paulo", "falar", "principalmente", "forte", "motivo", "grande", "escolhido",
        "possui", "interesse", "outras", "pois", "ter", "foco", "quanto", "quero", "Paulo", "pais", "acredito",
        "fiz", "oferece", "devido", "bom", "anos", "consegui", "objetivo", "Paulo", "todo", "nota", "o", "a",
        "que", "de", "e", "para", "com", "sobre", "também", "fazer", "meu", "trabalho", "minha", "um", "uma", 
        "localização", "escolhi", 'além', "bem", "muito", "vi", "ainda", "pai", "porque", "instituição", "ótima",
        "boa", "pessoas"
    }

    # Palavras indesejadas para expectativas do curso
    palavras_indesejadas_expectativas = {
        "fecap", "curso", "faculdade", "grade", "curricular", "ensino", "professores", "boa", "instituição", "nota", "espero", "tornar", "boas", "conseguir", ""
        "o", "a", "que", "de", "e", "para", "com", "sobre", "também", "fazer", "meu", "trabalho", "minha", "um", 
        "uma", "localização", "escolhi", "mercado", "profissional", "experiência", "desenvolver", "aprendizado", 
        "alto", "área", "espero", "expectativa", "bastante", "qualidade", "trabalhar", "aprender"
    }
    
    # Palavras indesejadas para objetivos de vida
    palavras_indesejadas_objetivos = {
        "objetivo", "profissional", "vida", "futuro", "carreira", "crescimento", "desenvolvimento", 
        "pessoal", "expectativa", "sucesso", "trabalho", "realização", "conquista", "qualidade", 
        "aprender", "experiência", "aproveitar", "mercado", "carreira", "ser", "muito", "novos", 
        "desafios", "vencer","busco", "em", "minha", "meu", "espero", "alcançar", 
        "adquirir", "fazer", "aproveitar", "ter", "Ter", "possa", ".", "assim", "surtando", "Médio",
        ""
    }

    # Escolher a lista de palavras indesejadas com base no tipo de texto
    if tipo == "motivos":
        palavras_indesejadas = palavras_indesejadas_motivos
    elif tipo == "expectativas":
        palavras_indesejadas = palavras_indesejadas_expectativas
    else:
        palavras_indesejadas = palavras_indesejadas_objetivos

    # Quebrar o texto em palavras
    palavras = texto.split()

    # Remover stopwords e palavras indesejadas
    palavras_limpas = [p for p in palavras if p.lower() not in stop_words and p.lower() not in palavras_indesejadas]

    return " ".join(palavras_limpas)

def grafico_motivos_escolha(df: pd.DataFrame):
    st.subheader("🎯 Motivos para Escolher a FECAP")

    coluna = "Os motivos de sua escolha pela FECAP"
    
    if coluna not in df.columns:
        st.warning("Coluna dos motivos de escolha não foi encontrada.")
        return

    respostas = df[coluna].dropna().astype(str)
    respostas_limpas = respostas.apply(limpar_texto)
    todas_respostas = " ".join(respostas_limpas)

    # Contar as palavras e ordenar por frequência
    palavras_frequentes = pd.Series(todas_respostas.split()).value_counts().reset_index()
    palavras_frequentes.columns = ["Palavra", "Frequência"]

    # Selecionar as 20 palavras mais frequentes
    palavras_top_20 = palavras_frequentes.head(21)

    # Gerar a nuvem de palavras com as 20 palavras mais frequentes
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(palavras_top_20["Palavra"]))

    # Mostrar a nuvem de palavras
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

    # Exibir as palavras mais frequentes com percentuais
    palavras_top_20["Percentual"] = (palavras_top_20["Frequência"] / palavras_top_20["Frequência"].sum() * 100).round(2)

    # Exibir a tabela com as top 20 palavras
    st.dataframe(palavras_top_20)

def grafico_expectativas_curso(df: pd.DataFrame):
    st.subheader("🎓 Expectativas com o Curso Escolhido")

    coluna = "Suas expectativas quanto ao Curso escolhido"
    
    if coluna not in df.columns:
        st.warning("Coluna das expectativas quanto ao curso escolhido não foi encontrada.")
        return

    # Obter as respostas da coluna
    respostas = df[coluna].dropna().astype(str)

    # Limpar as respostas
    respostas_limpas = respostas.apply(limpar_texto)

    # Unir todas as respostas em uma única string
    todas_respostas = " ".join(respostas_limpas)

    # Contar as palavras e ordenar por frequência
    palavras_frequentes = pd.Series(todas_respostas.split()).value_counts().reset_index()
    palavras_frequentes.columns = ["Palavra", "Frequência"]

    # Selecionar as 20 palavras mais frequentes
    palavras_top_20 = palavras_frequentes.head(21)

    # Gerar a nuvem de palavras com as 20 palavras mais frequentes
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(palavras_top_20["Palavra"]))

    # Mostrar a nuvem de palavras
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

    # Exibir as palavras mais frequentes com percentuais
    palavras_top_20["Percentual"] = (palavras_top_20["Frequência"] / palavras_top_20["Frequência"].sum() * 100).round(2)

    # Exibir a tabela com as top 20 palavras
    st.dataframe(palavras_top_20)

def grafico_objetivos_profissionais(df: pd.DataFrame):
    st.subheader("🌟 Objetivos Profissionais e de Vida")

    coluna = "Seus objetivos profissionais e de vida."
    
    if coluna not in df.columns:
        st.warning("Coluna dos objetivos profissionais e de vida não foi encontrada.")
        return

    # Obter as respostas da coluna
    respostas = df[coluna].dropna().astype(str)

    # Limpar as respostas
    respostas_limpas = respostas.apply(limpar_texto)

    # Unir todas as respostas em uma única string
    todas_respostas = " ".join(respostas_limpas)

    # Contar as palavras e ordenar por frequência
    palavras_frequentes = pd.Series(todas_respostas.split()).value_counts().reset_index()
    palavras_frequentes.columns = ["Palavra", "Frequência"]

    # Selecionar as 20 palavras mais frequentes
    palavras_top_20 = palavras_frequentes.head(21)

    # Gerar a nuvem de palavras com as 20 palavras mais frequentes
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(palavras_top_20["Palavra"]))

    # Mostrar a nuvem de palavras
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(plt)

    # Exibir as palavras mais frequentes com percentuais
    palavras_top_20["Percentual"] = (palavras_top_20["Frequência"] / palavras_top_20["Frequência"].sum() * 100).round(2)

    # Exibir a tabela com as top 20 palavras
    st.dataframe(palavras_top_20)

def grafico_recomendacao(df: pd.DataFrame):
    st.subheader("💬 Recomendação da FECAP")

    coluna = "Considerando sua experiência até o momento da matrícula na FECAP, o quanto você nos recomendaria a seus amigos e familiares?"
    
    if coluna not in df.columns:
        st.warning("Coluna de recomendação não foi encontrada.")
        return

    # Obter as respostas da coluna
    respostas = df[coluna].dropna().astype(int)

    # Contar as respostas de 0 a 10
    recomendacao_contagem = respostas.value_counts().sort_index()

    # Gerar gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    recomendacao_contagem.plot(kind='bar', ax=ax, color='#4E79A7', edgecolor="black")
    ax.set_xlabel("Escala de Recomendação")
    ax.set_ylabel("Número de Respostas")
    ax.set_title("Distribuição da Recomendação da FECAP")
    ax.set_xticks(range(11))
    ax.set_xticklabels(range(11))
    for i, v in enumerate(recomendacao_contagem):
        ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=10)

    # Mostrar o gráfico no Streamlit
    st.pyplot(fig)