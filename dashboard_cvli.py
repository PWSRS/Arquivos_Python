import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Carrega os dados
df = pd.read_excel("cvli_formatado.xlsx")

# Converte a coluna 'Data do fato' para datetime
df["Data do fato"] = pd.to_datetime(df["Data do fato"], errors="coerce")

# Título do dashboard
st.title("📍 Mapa Interativo de Ocorrências CVLI")

# Filtros na barra lateral
with st.sidebar:
    st.header("Filtros")

    # Filtro por ANO
    if "ANO" in df.columns:
        ano_selecionado = st.selectbox(
            "Ano", ["Todos"] + sorted(df["ANO"].dropna().astype(str).unique().tolist())
        )
        if ano_selecionado != "Todos":
            df = df[df["ANO"].astype(str) == ano_selecionado]

    # Filtro por Cidade
    if "Cidade" in df.columns:
        cidade = st.selectbox(
            "Cidade", ["Todas"] + sorted(df["Cidade"].dropna().unique())
        )
        if cidade != "Todas":
            df = df[df["Cidade"] == cidade]

    # Filtro por Bairro
    if "Bairro" in df.columns:
        bairro = st.selectbox(
            "Bairro", ["Todos"] + sorted(df["Bairro"].dropna().unique())
        )
        if bairro != "Todos":
            df = df[df["Bairro"] == bairro]

    # Filtro por OPM
    if "OPM" in df.columns:
        opm = st.selectbox("OPM", ["Todos"] + sorted(df["OPM"].dropna().unique()))
        if opm != "Todos":
            df = df[df["OPM"] == opm]

    # Filtro por Tipo
    if "Tipo" in df.columns:
        tipo = st.selectbox("Tipo", ["Todos"] + sorted(df["Tipo"].dropna().unique()))
        if tipo != "Todos":
            df = df[df["Tipo"] == tipo]

    # Filtro por intervalo de datas (baseado em 'Data do fato')
    if "Data do fato" in df.columns:
        data_min = df["Data do fato"].min()
        data_max = df["Data do fato"].max()
        data_inicio, data_fim = st.date_input(
            "Intervalo de Datas", [data_min, data_max]
        )
        df = df[
            (df["Data do fato"] >= pd.to_datetime(data_inicio))
            & (df["Data do fato"] <= pd.to_datetime(data_fim))
        ]

# Mostrar total filtrado
st.subheader(f"Ocorrências encontradas: {len(df)}")

# Criar mapa
mapa = folium.Map(location=[-15.0, -50.0], zoom_start=5)

# Adicionar marcadores
for _, row in df.iterrows():
    lat = row["Latitude"]
    lon = row["Longitude"]
    if pd.notnull(lat) and pd.notnull(lon):
        popup_info = f"""
        <b>Data:</b> {row.get('Data do fato', '')}<br>
        <b>Tipo:</b> {row.get('Tipo', '')}<br>
        <b>Cidade:</b> {row.get('Cidade', '')}<br>
        <b>Bairro:</b> {row.get('Bairro', '')}<br>
        <b>OPM:</b> {row.get('OPM', '')}
        """
        folium.Marker(
            location=[lat, lon],
            popup=popup_info,
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(mapa)

# Exibir mapa
st_folium(mapa, width=700, height=500)
