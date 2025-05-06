# dados.py
import os
import django
import pandas as pd

# Configurações do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cvli.settings")
django.setup()

from ocorrencias.models import Ocorrencia  # importe seu model


def carregar_ocorrencias():
    # Carrega os dados da tabela Ocorrencia com o nome das colunas relacionadas
    qs = Ocorrencia.objects.values(
        "data_fato",
        "tipo__nome",  # nome do tipo de ocorrência
        "cidade__nome",  # nome da cidade
        "bairro",
        "opm",
        "latitude",
        "longitude",
    )
    # Converte para um DataFrame
    df = pd.DataFrame.from_records(qs)

    # Renomeia as colunas para ficar consistente com o resto do código
    df.rename(
        columns={
            "data_fato": "data",  # renomeando para 'data'
            "tipo__nome": "tipo",  # renomeando para 'tipo'
            "cidade__nome": "cidade",  # renomeando para 'cidade'
        },
        inplace=True,
    )

    # Certifique-se de que as colunas de data, latitude e longitude estão no formato correto
    df["data"] = pd.to_datetime(
        df["data"], errors="coerce"
    )  # Converte a coluna de data
    df["latitude"] = pd.to_numeric(
        df["latitude"], errors="coerce"
    )  # Converte para numérico
    df["longitude"] = pd.to_numeric(
        df["longitude"], errors="coerce"
    )  # Converte para numérico

    return df
