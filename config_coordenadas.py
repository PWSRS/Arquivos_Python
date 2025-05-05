import pandas as pd
import re


def dms_to_decimal(coord):
    parts = re.split("[°'\"]+", coord)
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    direction = coord.strip()[-1].upper()
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ["S", "W"]:
        decimal *= -1
    return decimal


def split_and_convert(coord_string):
    try:
        lat_str, lon_str = coord_string.split(" ")
        lat = dms_to_decimal(lat_str)
        lon = dms_to_decimal(lon_str)
        return pd.Series([lat, lon])
    except:
        return pd.Series([None, None])


# Carregar o arquivo original
df = pd.read_excel("cvli.xlsx")

# Converter a coluna "Coordenadas"
df[["Latitude", "Longitude"]] = df["Coordenadas"].apply(split_and_convert)

# Exportar apenas as colunas desejadas
df_final = df.copy()
df_final = df_final.drop(
    columns=[
        "Coordenadas",
        "Latitude_corrigida",
        "Longitude_corrigida",
        "latitude_decimal",
        "longitude_decimal",
    ],
    errors="ignore",
)  # ignora se as colunas não existirem

# Salvar como novo Excel com ponto decimal (visível só se abrir em código ou CSV)
df_final.to_excel("cvli_formatado.xlsx", index=False)

print(
    "✅ Arquivo 'cvli_formatado.xlsx' salvo com apenas Latitude e Longitude com ponto decimal."
)
