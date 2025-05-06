import pandas as pd
import folium
from dados import carregar_ocorrencias

# Gerar um mapa simples e estático, salvo como arquivo .html, para diretamente no navegador.

# Carrega os dados com Latitude e Longitude em ponto decimal
# df = pd.read_excel("cvli_formatado.xlsx")
df = carregar_ocorrencias()

# Cria um mapa centralizado no meio do Brasil, pode ajustar para sua região
mapa = folium.Map(location=[-15.0, -50.0], zoom_start=5)

# Adiciona um marcador para cada linha do DataFrame
for _, row in df.iterrows():
    lat = row["Latitude"]
    lon = row["Longitude"]

    # Verifica se as coordenadas são válidas
    if pd.notnull(lat) and pd.notnull(lon):
        folium.Marker(
            location=[lat, lon],
            popup=f"Lat: {lat}, Lon: {lon}",
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(mapa)

# Salva o mapa como HTML
mapa.save("mapa_cvli.html")
print("✅ Mapa salvo como 'mapa_cvli.html'. Abra no navegador para visualizar.")
