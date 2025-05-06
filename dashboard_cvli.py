import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from dados import carregar_ocorrencias

# Criar um dashboard interativo com filtros dinâmicos usando o Streamlit,
# exibindo o mapa em tempo real baseado nas seleções feitas pelo usuário.

# Carrega os dados diretamente do banco
df = carregar_ocorrencias()

# Converte a coluna 'data' para datetime
df["data"] = pd.to_datetime(df["data"], errors="coerce")

# Extrai o ano para filtro
df["ano"] = df["data"].dt.year

# Título do dashboard
st.title("📍 Mapa Interativo de Ocorrências CVLI")

# Filtros na barra lateral
with st.sidebar:
    st.header("Filtros")

    # Filtro por ANO
    ano_selecionado = st.selectbox(
        "Ano", ["Todos"] + sorted(df["ano"].dropna().astype(str).unique().tolist())
    )
    if ano_selecionado != "Todos":
        df = df[df["ano"].astype(str) == ano_selecionado]

    # Filtro por Cidade
    cidade = st.selectbox("Cidade", ["Todas"] + sorted(df["cidade"].dropna().unique()))
    if cidade != "Todas":
        df = df[df["cidade"] == cidade]

    # Filtro por Bairro
    bairro = st.selectbox("Bairro", ["Todos"] + sorted(df["bairro"].dropna().unique()))
    if bairro != "Todos":
        df = df[df["bairro"] == bairro]

    # Filtro por OPM
    opm = st.selectbox("OPM", ["Todos"] + sorted(df["opm"].dropna().unique()))
    if opm != "Todos":
        df = df[df["opm"] == opm]

    # Filtro por Tipo
    tipo = st.selectbox("Tipo", ["Todos"] + sorted(df["tipo"].dropna().unique()))
    if tipo != "Todos":
        df = df[df["tipo"] == tipo]

    # Filtro por intervalo de datas
    data_min = df["data"].min()
    data_max = df["data"].max()
    data_inicio, data_fim = st.date_input("Intervalo de Datas", [data_min, data_max])
    df = df[
        (df["data"] >= pd.to_datetime(data_inicio))
        & (df["data"] <= pd.to_datetime(data_fim))
    ]

# Mostrar total filtrado
st.subheader(f"Ocorrências encontradas: {len(df)}")

# Criar mapa
mapa = folium.Map(location=[-15.0, -50.0], zoom_start=5)

# Adicionar marcadores
for _, row in df.iterrows():
    lat = row["latitude"]
    lon = row["longitude"]
    if pd.notnull(lat) and pd.notnull(lon):
        popup_info = f"""
        <b>Data:</b> {row.get('data', '')}<br>
        <b>Tipo:</b> {row.get('tipo', '')}<br>
        <b>Cidade:</b> {row.get('cidade', '')}<br>
        <b>Bairro:</b> {row.get('bairro', '')}<br>
        <b>OPM:</b> {row.get('opm', '')}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_info,
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(mapa)

# Exibir mapa
st_folium(mapa, width=700, height=500)
