"""
Projeto Integrador - Desenvolvimento Low Code em Ciência de Dados
Dashboard de Análise do Catálogo da Netflix
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Dashboard Netflix - PI Senac",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CARREGAMENTO E PREPARAÇÃO DOS DADOS
# ============================================================
# URLs públicas que servem o dataset Netflix Titles (Kaggle, shivamb).
# A função tenta carregar a primeira que funcionar.
FONTES_DADOS = [
    "https://cdn.jsdelivr.net/gh/allenkong221/netflix-titles-dataset@main/netflix_titles.csv",
    "https://cdn.jsdelivr.net/gh/lijesh010/Netflix_dataset_Exploratory_Data_Analysis_Python_Project@main/netflix_titles.csv",
    "https://raw.githubusercontent.com/allenkong221/netflix-titles-dataset/main/netflix_titles.csv",
]

@st.cache_data
def carregar_dados():
    """Carrega e prepara o dataset da Netflix.

    Tenta primeiro um arquivo local 'netflix_titles.csv'. Se não existir,
    busca em fontes públicas conhecidas. O resultado é cacheado pelo Streamlit.
    """
    df = None

    # 1. tenta carregar arquivo local
    if os.path.exists("netflix_titles.csv"):
        df = pd.read_csv("netflix_titles.csv")

    # 2. caso não exista, tenta as fontes públicas
    if df is None:
        for url in FONTES_DADOS:
            try:
                df = pd.read_csv(url)
                break
            except Exception:
                continue

    if df is None:
        raise RuntimeError(
            "Não foi possível carregar o dataset. "
            "Verifique a conexão ou disponibilize o arquivo netflix_titles.csv localmente."
        )

    # Tratamento de nulos nas colunas categóricas
    df["country"] = df["country"].fillna("Não informado")
    df["director"] = df["director"].fillna("Não informado")
    df["cast"] = df["cast"].fillna("Não informado")
    df["rating"] = df["rating"].fillna("Sem classificação")

    # Conversão de datas
    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
    df["ano_adicionado"] = df["date_added"].dt.year
    df["mes_adicionado"] = df["date_added"].dt.month

    # Padronização do tipo
    df["type"] = df["type"].str.strip()

    return df

try:
    df = carregar_dados()
except Exception as erro:
    st.error(f"❌ Erro ao carregar dataset: {erro}")
    st.stop()

# ============================================================
# CABEÇALHO
# ============================================================
st.title("🎬 Dashboard de Análise do Catálogo da Netflix")
st.markdown(
    "Aplicação desenvolvida em **Streamlit** (low code) como parte do "
    "**Projeto Integrador** do curso de Ciência de Dados — Senac."
)
st.divider()

# ============================================================
# BARRA LATERAL - FILTROS
# ============================================================
st.sidebar.header("🔎 Filtros")

# Filtro 1: tipo de conteúdo
tipos_disponiveis = ["Todos"] + sorted(df["type"].dropna().unique().tolist())
tipo_selecionado = st.sidebar.selectbox("Tipo de conteúdo", tipos_disponiveis)

# Filtro 2: intervalo de anos de lançamento
ano_min = int(df["release_year"].min())
ano_max = int(df["release_year"].max())
intervalo_ano = st.sidebar.slider(
    "Ano de lançamento",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, ano_max)
)

# Filtro 3: país (extraído da coluna country que pode ter múltiplos países)
todos_paises = sorted(
    set(
        pais.strip()
        for paises in df["country"].dropna()
        for pais in paises.split(",")
        if pais.strip() and pais.strip() != "Não informado"
    )
)
paises_selecionados = st.sidebar.multiselect(
    "Países (deixe vazio para todos)",
    options=todos_paises,
    default=[]
)

# Aplicação dos filtros
df_filtrado = df.copy()

if tipo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["type"] == tipo_selecionado]

df_filtrado = df_filtrado[
    (df_filtrado["release_year"] >= intervalo_ano[0]) &
    (df_filtrado["release_year"] <= intervalo_ano[1])
]

if paises_selecionados:
    df_filtrado = df_filtrado[
        df_filtrado["country"].apply(
            lambda x: any(p in x for p in paises_selecionados) if pd.notna(x) else False
        )
    ]

# ============================================================
# INDICADORES (KPIs)
# ============================================================
st.subheader("📊 Indicadores Gerais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Títulos", f"{len(df_filtrado):,}".replace(",", "."))

with col2:
    qtd_filmes = (df_filtrado["type"] == "Movie").sum()
    st.metric("Filmes", f"{qtd_filmes:,}".replace(",", "."))

with col3:
    qtd_series = (df_filtrado["type"] == "TV Show").sum()
    st.metric("Séries de TV", f"{qtd_series:,}".replace(",", "."))

with col4:
    qtd_paises = df_filtrado["country"].nunique()
    st.metric("Países distintos", qtd_paises)

st.divider()

# ============================================================
# GRÁFICO 1 - DISTRIBUIÇÃO ENTRE FILMES E SÉRIES
# ============================================================
st.subheader("🎞️ Distribuição entre Filmes e Séries de TV")

contagem_tipo = df_filtrado["type"].value_counts().reset_index()
contagem_tipo.columns = ["Tipo", "Quantidade"]

fig_tipo = px.pie(
    contagem_tipo,
    names="Tipo",
    values="Quantidade",
    hole=0.45,
    color_discrete_sequence=["#E50914", "#221F1F"]
)
fig_tipo.update_traces(textinfo="percent+label")
st.plotly_chart(fig_tipo, use_container_width=True)

# ============================================================
# GRÁFICO 2 - TOP 10 PAÍSES PRODUTORES
# ============================================================
st.subheader("🌍 Top 10 Países com Mais Títulos")

# Cada linha pode ter vários países separados por vírgula
lista_paises = (
    df_filtrado["country"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
)
lista_paises = lista_paises[lista_paises != "Não informado"]
top_paises = lista_paises.value_counts().head(10).reset_index()
top_paises.columns = ["País", "Quantidade"]

fig_paises = px.bar(
    top_paises,
    x="Quantidade",
    y="País",
    orientation="h",
    color="Quantidade",
    color_continuous_scale="Reds",
    text="Quantidade"
)
fig_paises.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_paises, use_container_width=True)

# ============================================================
# GRÁFICO 3 - CONTEÚDO ADICIONADO POR ANO
# ============================================================
st.subheader("📅 Títulos Adicionados ao Catálogo por Ano")

por_ano = (
    df_filtrado.dropna(subset=["ano_adicionado"])
    .groupby(["ano_adicionado", "type"])
    .size()
    .reset_index(name="Quantidade")
)
por_ano["ano_adicionado"] = por_ano["ano_adicionado"].astype(int)

fig_ano = px.line(
    por_ano,
    x="ano_adicionado",
    y="Quantidade",
    color="type",
    markers=True,
    labels={"ano_adicionado": "Ano de adição", "type": "Tipo"},
    color_discrete_map={"Movie": "#E50914", "TV Show": "#221F1F"}
)
st.plotly_chart(fig_ano, use_container_width=True)

# ============================================================
# GRÁFICO 4 - CLASSIFICAÇÃO INDICATIVA
# ============================================================
st.subheader("🔞 Distribuição por Classificação Indicativa")

contagem_rating = df_filtrado["rating"].value_counts().head(10).reset_index()
contagem_rating.columns = ["Classificação", "Quantidade"]

fig_rating = px.bar(
    contagem_rating,
    x="Classificação",
    y="Quantidade",
    color="Quantidade",
    color_continuous_scale="Reds",
    text="Quantidade"
)
st.plotly_chart(fig_rating, use_container_width=True)

# ============================================================
# GRÁFICO 5 - GÊNEROS MAIS FREQUENTES
# ============================================================
st.subheader("🎭 Top 10 Gêneros Mais Frequentes")

# A coluna 'listed_in' contém vários gêneros separados por vírgula
contador_generos = Counter()
for generos in df_filtrado["listed_in"].dropna():
    for genero in generos.split(","):
        contador_generos[genero.strip()] += 1

top_generos = pd.DataFrame(
    contador_generos.most_common(10),
    columns=["Gênero", "Quantidade"]
)

fig_generos = px.bar(
    top_generos,
    x="Quantidade",
    y="Gênero",
    orientation="h",
    color="Quantidade",
    color_continuous_scale="Reds",
    text="Quantidade"
)
fig_generos.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_generos, use_container_width=True)

# ============================================================
# TABELA DETALHADA
# ============================================================
st.subheader("📋 Tabela Detalhada dos Títulos Filtrados")

colunas_exibir = ["title", "type", "release_year", "rating", "country", "listed_in"]
renomear = {
    "title": "Título",
    "type": "Tipo",
    "release_year": "Ano",
    "rating": "Classificação",
    "country": "País",
    "listed_in": "Gêneros"
}

tabela = df_filtrado[colunas_exibir].rename(columns=renomear).sort_values("Ano", ascending=False)
st.dataframe(tabela, use_container_width=True, height=400)

# Download dos dados filtrados
st.download_button(
    label="⬇️ Baixar dados filtrados em CSV",
    data=tabela.to_csv(index=False).encode("utf-8"),
    file_name="netflix_filtrado.csv",
    mime="text/csv"
)

# ============================================================
# RODAPÉ
# ============================================================
st.divider()
st.caption(
    "Projeto Integrador — Curso Superior de Tecnologia em Ciência de Dados — Senac EAD. "
    "Dataset: Netflix Movies and TV Shows (Kaggle, 2021)."
)
