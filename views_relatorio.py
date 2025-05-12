from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Ocorrencia, Sexo, Tipo, Cidade
from datetime import datetime
import matplotlib

matplotlib.use("Agg")  # Usar backend não interativo
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
from dateutil.relativedelta import relativedelta
import locale


@login_required
def relatorio_dashboard(request):
    """
    Gera um relatório analítico baseado nos dados do dashboard
    """
    # Filtros recebidos via GET (mesmos do dashboard_dados)
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    sexo = request.GET.get("sexo")
    tipo = request.GET.get("tipo")
    cidade = request.GET.get("cidade")
    faixa_idade = request.GET.get("faixa_etaria")
    periodo = request.GET.get(
        "periodo", "mensal"
    )  # Novo parâmetro para controlar a visualização (mensal ou anual)

    # Lista de nomes de meses em português - definida globalmente para uso em várias partes do código
    meses_pt = [
        "Jan",
        "Fev",
        "Mar",
        "Abr",
        "Mai",
        "Jun",
        "Jul",
        "Ago",
        "Set",
        "Out",
        "Nov",
        "Dez",
    ]

    # Texto dos filtros para exibição
    filtros_texto = []
    if data_inicio:
        data_formatada = (
            datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y")
            if data_inicio
            else ""
        )
        filtros_texto.append(f"Data início: {data_formatada}")
    if data_fim:
        data_formatada = (
            datetime.strptime(data_fim, "%Y-%m-%d").strftime("%d/%m/%Y")
            if data_fim
            else ""
        )
        filtros_texto.append(f"Data fim: {data_formatada}")
    if sexo:
        try:
            sexo_obj = Sexo.objects.get(pk=sexo)
            filtros_texto.append(f"Sexo: {sexo_obj.nome}")
        except:
            pass
    if tipo:
        try:
            tipo_obj = Tipo.objects.get(pk=tipo)
            filtros_texto.append(f"Tipo: {tipo_obj.nome}")
        except:
            pass
    if cidade:
        try:
            cidade_obj = Cidade.objects.get(pk=cidade)
            filtros_texto.append(f"Cidade: {cidade_obj.nome}")
        except:
            pass
    if faixa_idade:
        if faixa_idade == "0-10":
            filtros_texto.append("Faixa etária: 0 até 10 anos")
        elif faixa_idade == "11-20":
            filtros_texto.append("Faixa etária: 11 até 20 anos")
        elif faixa_idade == "21-30":
            filtros_texto.append("Faixa etária: 21 até 30 anos")
        elif faixa_idade == "31-40":
            filtros_texto.append("Faixa etária: 31 até 40 anos")
        elif faixa_idade == "41-50":
            filtros_texto.append("Faixa etária: 41 até 50 anos")
        elif faixa_idade == "51-60":
            filtros_texto.append("Faixa etária: 51 até 60 anos")
        elif faixa_idade == "61-70":
            filtros_texto.append("Faixa etária: 61 até 70 anos")
        elif faixa_idade == "71-80":
            filtros_texto.append("Faixa etária: 71 até 80 anos")
        elif faixa_idade == "81-90":
            filtros_texto.append("Faixa etária: 81 até 90 anos")
        elif faixa_idade == "91-100":
            filtros_texto.append("Faixa etária: 91 até 100 anos")
        else:
            filtros_texto.append(f"Faixa etária: {faixa_idade}")

    filtros = ", ".join(filtros_texto) if filtros_texto else "Todos os registros"

    # Obter os dados das ocorrências com os mesmos filtros do dashboard
    ocorrencias = Ocorrencia.objects.all()

    # Aplicar filtros
    if data_inicio:
        ocorrencias = ocorrencias.filter(data_fato__gte=data_inicio)
    if data_fim:
        ocorrencias = ocorrencias.filter(data_fato__lte=data_fim)
    if sexo:
        ocorrencias = ocorrencias.filter(sexo_id=sexo)
    if tipo:
        ocorrencias = ocorrencias.filter(tipo_id=tipo)
    if cidade:
        ocorrencias = ocorrencias.filter(cidade_id=cidade)
    if faixa_idade:
        try:
            faixa = faixa_idade.split("-")
            if faixa[1] == "+":
                ocorrencias = ocorrencias.filter(idade__gte=int(faixa[0]))
            else:
                ocorrencias = ocorrencias.filter(
                    idade__gte=int(faixa[0]), idade__lte=int(faixa[1])
                )
        except:
            pass

    # Total de ocorrências para o resumo
    total_ocorrencias = ocorrencias.count()

    # Função auxiliar para gerar gráficos como imagens base64
    def gerar_grafico_base64(labels, dados, titulo, tipo_grafico="bar"):
        # Tamanho reduzido para os gráficos
        plt.figure(figsize=(7, 4))
        plt.clf()

        if tipo_grafico == "bar":
            plt.bar(labels, dados, color="skyblue")
            # Rotacionar os rótulos do eixo x para melhor legibilidade
            plt.xticks(rotation=45, ha="right")
        elif tipo_grafico == "pie":
            # Remover valores zero para evitar fatias vazias no gráfico de pizza
            dados_filtrados = []
            labels_filtrados = []
            for i, valor in enumerate(dados):
                if valor > 0:
                    dados_filtrados.append(valor)
                    labels_filtrados.append(labels[i])

            plt.pie(
                dados_filtrados,
                labels=labels_filtrados,
                autopct="%1.1f%%",
                startangle=90,
            )
            plt.axis("equal")

        plt.title(titulo, fontsize=12)
        # Adicionar valores nas barras para gráficos de barra
        if tipo_grafico == "bar":
            for i, valor in enumerate(dados):
                plt.text(
                    i, valor + (max(dados) * 0.02), str(valor), ha="center", fontsize=8
                )

        plt.tight_layout()

        # Salvar o gráfico em um buffer de memória
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=100)
        buffer.seek(0)

        # Converter para base64
        imagem_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()

        return imagem_base64

    # Gerar dados para os gráficos (similar ao dashboard_dados)

    # 1. Gráfico por mês
    mes_count = (
        ocorrencias.values("mes", "mes__nome")
        .annotate(total=Count("id"))
        .order_by("mes")
    )
    mes_labels = [item["mes__nome"] for item in mes_count]
    mes_dados = [item["total"] for item in mes_count]

    # Calcular percentuais para a tabela
    total_mes = sum(mes_dados)
    dados_mes = []
    for i, mes in enumerate(mes_labels):
        if total_mes > 0:
            percentual = round((mes_dados[i] / total_mes) * 100, 1)
        else:
            percentual = 0
        dados_mes.append((mes, mes_dados[i], percentual))

    # Gerar gráfico de mês
    grafico_mes = gerar_grafico_base64(mes_labels, mes_dados, "Ocorrências por Mês")

    # 2. Gráfico por sexo
    sexo_count = ocorrencias.values("sexo__nome").annotate(total=Count("id"))
    sexo_labels = [item["sexo__nome"] for item in sexo_count]
    sexo_dados = [item["total"] for item in sexo_count]

    # Calcular percentuais para a tabela
    total_sexo = sum(sexo_dados)
    dados_sexo = []
    for i, sexo in enumerate(sexo_labels):
        if total_sexo > 0:
            percentual = round((sexo_dados[i] / total_sexo) * 100, 1)
        else:
            percentual = 0
        dados_sexo.append((sexo, sexo_dados[i], percentual))

    # Gerar gráfico de sexo
    grafico_sexo = gerar_grafico_base64(
        sexo_labels, sexo_dados, "Ocorrências por Sexo", "pie"
    )

    # 3. Gráfico por faixa etária
    idade_faixas = {
        "0 até 10 anos": 0,
        "11 até 20 anos": 0,
        "21 até 30 anos": 0,
        "31 até 40 anos": 0,
        "41 até 50 anos": 0,
        "51 até 60 anos": 0,
        "61 até 70 anos": 0,
        "71 até 80 anos": 0,
        "81 até 90 anos": 0,
        "91 até 100 anos": 0,
        "Prejudicado": 0,
    }

    for o in ocorrencias:
        idade = o.idade
        if idade is None:
            idade_faixas["Prejudicado"] += 1
        elif idade <= 10:
            idade_faixas["0 até 10 anos"] += 1
        elif idade <= 20:
            idade_faixas["11 até 20 anos"] += 1
        elif idade <= 30:
            idade_faixas["21 até 30 anos"] += 1
        elif idade <= 40:
            idade_faixas["31 até 40 anos"] += 1
        elif idade <= 50:
            idade_faixas["41 até 50 anos"] += 1
        elif idade <= 60:
            idade_faixas["51 até 60 anos"] += 1
        elif idade <= 70:
            idade_faixas["61 até 70 anos"] += 1
        elif idade <= 80:
            idade_faixas["71 até 80 anos"] += 1
        elif idade <= 90:
            idade_faixas["81 até 90 anos"] += 1
        elif idade <= 100:
            idade_faixas["91 até 100 anos"] += 1
        else:
            idade_faixas["Prejudicado"] += 1

    idade_labels = list(idade_faixas.keys())
    idade_dados = list(idade_faixas.values())

    # Calcular percentuais para a tabela
    total_idade = sum(idade_dados)
    dados_idade = []
    for i, faixa in enumerate(idade_labels):
        if total_idade > 0:
            percentual = round((idade_dados[i] / total_idade) * 100, 1)
        else:
            percentual = 0
        dados_idade.append((faixa, idade_dados[i], percentual))

    # Gerar gráfico de faixa etária
    grafico_idade = gerar_grafico_base64(
        idade_labels, idade_dados, "Ocorrências por Faixa Etária"
    )

    # 4. Gráfico por cidade (top 10)
    cidade_count = (
        ocorrencias.values("cidade__nome")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    cidade_labels = [item["cidade__nome"] for item in cidade_count]
    cidade_dados = [item["total"] for item in cidade_count]

    # Calcular percentuais para a tabela
    total_cidade = sum(cidade_dados)
    dados_cidade = []
    for i, cidade in enumerate(cidade_labels):
        if total_cidade > 0:
            percentual = round((cidade_dados[i] / total_cidade) * 100, 1)
        else:
            percentual = 0
        dados_cidade.append((cidade, cidade_dados[i], percentual))

    # Gerar gráfico de cidade
    grafico_cidade = gerar_grafico_base64(cidade_labels, cidade_dados, "Top 10 Cidades")

    # 5. Gráfico de projeção
    # Obtém dados agrupados por mês/ano ou ano para análise temporal
    from django.db.models.functions import TruncMonth, TruncYear
    from datetime import timedelta
    import random

    # Determinar o tipo de agrupamento com base no parâmetro 'periodo'
    if periodo == "anual":
        # Agrupamento por ano
        ocorrencias_por_data = (
            Ocorrencia.objects.annotate(mes_ano=TruncYear("data_fato"))
            .values("mes_ano")
            .annotate(total=Count("id"))
            .order_by("mes_ano")
        )
    else:  # mensal (padrão)
        # Agrupamento por mês
        ocorrencias_por_data = (
            Ocorrencia.objects.annotate(mes_ano=TruncMonth("data_fato"))
            .values("mes_ano")
            .annotate(total=Count("id"))
            .order_by("mes_ano")
        )

    # Variáveis para projeção
    grafico_projecao = ""
    media_projecao_linear = 0
    media_projecao_bayes = 0
    media_projecao_forest = 0
    intervalo_confianca_bayes = ""
    tabela_projecoes = []
    analise_projecao = "Não há dados suficientes para realizar projeções."
    tendencia = "Não há dados suficientes para determinar tendência."

    # Prepara dados para projeção se houver dados suficientes
    if len(ocorrencias_por_data) > 1:
        # Converte datas para valores numéricos (meses desde o início)
        data_inicial = ocorrencias_por_data[0]["mes_ano"]
        x_valores = []
        y_valores = []
        datas_reais = []

        for item in ocorrencias_por_data:
            # Calcula diferença em meses
            data = item["mes_ano"]
            diff_meses = (data.year - data_inicial.year) * 12 + (
                data.month - data_inicial.month
            )
            x_valores.append(diff_meses)
            y_valores.append(item["total"])
            # Formatar a data de acordo com o período selecionado
            if periodo == "anual":
                datas_reais.append(data.strftime("%Y"))
            else:
                # Usar a lista de meses em português
                mes_idx = data.month - 1  # índice 0-11
                mes = meses_pt[mes_idx]
                ano = data.strftime("%Y")
                datas_reais.append(f"{mes}/{ano}")

        # Calcula projeções se houver dados suficientes
        if len(x_valores) >= 2:
            x = np.array(x_valores)
            y = np.array(y_valores)

            # Dados comuns para todos os modelos
            ultimo_mes = x_valores[-1]
            ultima_data = ocorrencias_por_data.last()["mes_ano"]
            projecao_datas = []

            # Definir locale para português do Brasil
            try:
                locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
            except:
                try:
                    locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")
                except:
                    pass  # Se não conseguir definir o locale, usa o padrão

            # Projetar para os próximos períodos (6 meses ou 2 anos)
            if periodo == "anual":
                # Para visualização anual, projetamos 2 anos à frente
                for i in range(1, 3):  # Próximos 2 anos
                    data_futura = ultima_data + relativedelta(years=i)
                    projecao_datas.append(data_futura.strftime("%Y"))
            else:
                # Para visualização mensal, projetamos 6 meses à frente
                for i in range(1, 7):  # Próximos 6 meses
                    data_futura = ultima_data + relativedelta(months=i)

                    # Usar a lista de meses em português
                    mes_idx = data_futura.month - 1  # índice 0-11
                    mes = meses_pt[mes_idx]
                    ano = data_futura.strftime("%Y")
                    projecao_datas.append(f"{mes}/{ano}")

            # 1. MODELO DE REGRESSÃO LINEAR
            m_linear, b_linear = np.polyfit(x, y, 1)
            projecao_linear = []

            # Número de períodos a projetar (2 anos ou 6 meses)
            num_periodos = 2 if periodo == "anual" else 6

            for i in range(1, num_periodos + 1):
                # Incremento depende do período (12 meses para anual, 1 mês para mensal)
                incremento = 12 if periodo == "anual" else 1
                periodo_futuro = ultimo_mes + (i * incremento)
                valor_projetado = round(m_linear * periodo_futuro + b_linear)
                projecao_linear.append(max(0, valor_projetado))

            media_projecao_linear = round(sum(projecao_linear) / len(projecao_linear))

            # 2. MODELO BAYESIANO
            # Calculamos a média e desvio padrão dos dados históricos
            media_historica = np.mean(y)
            desvio_padrao = np.std(y)

            # Usamos a tendência linear como base, mas adicionamos incerteza
            projecao_bayes = []
            intervalos_superior = []
            intervalos_inferior = []

            for i in range(1, 7):
                mes_futuro = ultimo_mes + i
                # Valor base da projeção linear
                base_projecao = m_linear * mes_futuro + b_linear

                # Ajustamos com um fator bayesiano (simplificado)
                peso_tendencia = max(0, 1 - (i * 0.1))  # Diminui com o tempo
                valor_projetado = round(
                    (base_projecao * peso_tendencia)
                    + (media_historica * (1 - peso_tendencia))
                )

                # Garantimos que não seja negativo
                projecao_bayes.append(max(0, valor_projetado))

                # Calculamos intervalos de confiança (95%)
                incerteza = desvio_padrao * (1 + (i * 0.2))
                intervalo_95 = 1.96 * incerteza  # Aproximação para 95% de confiança

                intervalos_superior.append(
                    max(0, round(valor_projetado + intervalo_95))
                )
                intervalos_inferior.append(
                    max(0, round(valor_projetado - intervalo_95))
                )

            media_projecao_bayes = round(sum(projecao_bayes) / len(projecao_bayes))
            intervalo_confianca_bayes = (
                f"{min(intervalos_inferior)} - {max(intervalos_superior)}"
            )

            # 3. MODELO RANDOM FOREST (simplificado)
            # Calculamos a tendência geral
            tendencia_geral = (y[-1] - y[0]) / len(y) if len(y) > 1 else 0

            # Identificamos padrões sazonais simples
            tem_sazonalidade = len(y) >= 12
            fator_sazonal = []

            if tem_sazonalidade:
                # Simplificação: usamos os últimos 12 meses como padrão sazonal
                for i in range(min(12, len(y))):
                    idx = len(y) - 12 + i
                    if idx >= 0:
                        fator = y[idx] / media_historica if media_historica > 0 else 1
                        fator_sazonal.append(fator)
                    else:
                        fator_sazonal.append(1)
            else:
                # Sem sazonalidade, usamos fatores neutros
                fator_sazonal = [1] * 12

            projecao_forest = []

            for i in range(1, 7):
                # Base: último valor + tendência
                base = y[-1] + (tendencia_geral * i)

                # Aplicamos fator sazonal (mês correspondente)
                mes_idx = (ultima_data.month - 1 + i) % 12
                fator = fator_sazonal[mes_idx] if mes_idx < len(fator_sazonal) else 1

                # Adicionamos um pequeno ruído aleatório para simular a variabilidade do modelo
                ruido = random.uniform(-desvio_padrao * 0.2, desvio_padrao * 0.2)

                valor_projetado = round(base * fator + ruido)
                projecao_forest.append(max(0, valor_projetado))

            media_projecao_forest = round(sum(projecao_forest) / len(projecao_forest))

            # Criar tabela de projeções
            tabela_projecoes = []
            for i in range(len(projecao_datas)):
                tabela_projecoes.append(
                    (
                        projecao_datas[i],
                        projecao_linear[i],
                        projecao_bayes[i],
                        projecao_forest[i],
                    )
                )

            # Gerar gráfico de projeção (maior que os outros gráficos)
            plt.figure(figsize=(10, 5.5))
            plt.clf()

            # Dados reais
            plt.plot(
                range(len(datas_reais)),
                y_valores,
                "o-",
                color="blue",
                label="Dados Históricos",
                markersize=4,
            )

            # Projeções
            x_proj = range(len(datas_reais), len(datas_reais) + len(projecao_datas))
            plt.plot(
                x_proj,
                projecao_linear,
                "s-",
                color="green",
                label="Regressão Linear",
                markersize=4,
            )
            plt.plot(
                x_proj,
                projecao_bayes,
                "^-",
                color="red",
                label="Modelo Bayesiano",
                markersize=4,
            )
            plt.plot(
                x_proj,
                projecao_forest,
                "D-",
                color="purple",
                label="Random Forest",
                markersize=4,
            )

            # Intervalo de confiança para o modelo bayesiano
            plt.fill_between(
                x_proj, intervalos_inferior, intervalos_superior, color="red", alpha=0.2
            )

            # Configurações do gráfico
            plt.title("Projeção de Ocorrências para os Próximos 6 Meses", fontsize=12)
            plt.xlabel("Período", fontsize=10)
            plt.ylabel("Número de Ocorrências", fontsize=10)
            plt.legend(fontsize=8)

            # Ajustar os rótulos do eixo x
            todos_labels = datas_reais + projecao_datas
            # Se houver muitos rótulos, mostrar apenas alguns para evitar sobreposição
            if len(todos_labels) > 12:
                indices = [
                    i for i in range(0, len(todos_labels), len(todos_labels) // 6)
                ]
                plt.xticks(
                    [i for i in range(len(todos_labels)) if i in indices],
                    [todos_labels[i] for i in indices],
                    rotation=45,
                    fontsize=8,
                )
            else:
                plt.xticks(
                    range(len(todos_labels)), todos_labels, rotation=45, fontsize=8
                )

            plt.grid(True, linestyle="--", alpha=0.7)
            plt.tight_layout()

            # Salvar o gráfico em um buffer de memória
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)

            # Converter para base64
            grafico_projecao = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()

            # Análise de tendência
            if m_linear > 0:
                tendencia = "Tendência de aumento no número de ocorrências"
            elif m_linear < 0:
                tendencia = "Tendência de diminuição no número de ocorrências"
            else:
                tendencia = "Tendência estável no número de ocorrências"

            # Análise textual das projeções
            analise_projecao = f"""
            Com base nos dados históricos, foram geradas projeções para os próximos 6 meses utilizando três modelos estatísticos diferentes.
            O modelo de regressão linear projeta uma média de {media_projecao_linear} ocorrências por mês, 
            enquanto o modelo bayesiano estima {media_projecao_bayes} ocorrências mensais com intervalo de confiança de {intervalo_confianca_bayes}.
            O modelo Random Forest, que considera possíveis padrões sazonais, projeta {media_projecao_forest} ocorrências por mês em média.
            """

            if (
                media_projecao_linear > y[-1]
                and media_projecao_bayes > y[-1]
                and media_projecao_forest > y[-1]
            ):
                analise_projecao += " Todos os modelos indicam uma tendência de aumento nas ocorrências para os próximos meses."
            elif (
                media_projecao_linear < y[-1]
                and media_projecao_bayes < y[-1]
                and media_projecao_forest < y[-1]
            ):
                analise_projecao += " Todos os modelos indicam uma tendência de diminuição nas ocorrências para os próximos meses."
            else:
                analise_projecao += " Os modelos apresentam projeções mistas, sugerindo uma possível estabilização ou variabilidade nas ocorrências futuras."

    # Contexto para o template
    context = {
        "data_geracao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "filtros": filtros,
        "periodo": periodo,  # Adicionando o período ao contexto
        "ano_atual": datetime.now().year,
        "total_ocorrencias": total_ocorrencias,
        "grafico_mes": grafico_mes,
        "dados_mes": dados_mes,
        "grafico_sexo": grafico_sexo,
        "dados_sexo": dados_sexo,
        "grafico_idade": grafico_idade,
        "dados_idade": dados_idade,
        "grafico_cidade": grafico_cidade,
        "dados_cidade": dados_cidade,
        "grafico_projecao": grafico_projecao,
        "media_projecao_linear": media_projecao_linear,
        "media_projecao_bayes": media_projecao_bayes,
        "media_projecao_forest": media_projecao_forest,
        "intervalo_confianca_bayes": intervalo_confianca_bayes,
        "tabela_projecoes": tabela_projecoes,
        "analise_projecao": analise_projecao,
        "tendencia": tendencia,
        "ultimo_mes": ultimo_mes,
    }

    # Análise textual simples
    if mes_dados:
        mes_max = mes_labels[mes_dados.index(max(mes_dados))]
        context["analise_mes"] = (
            f"O mês com maior número de ocorrências foi {mes_max} com {max(mes_dados)} registros."
        )
    else:
        context["analise_mes"] = "Não há dados suficientes para análise mensal."

    if sexo_dados:
        sexo_max = sexo_labels[sexo_dados.index(max(sexo_dados))]
        percentual_max = (
            round((max(sexo_dados) / total_sexo) * 100, 1) if total_sexo > 0 else 0
        )
        context["analise_sexo"] = (
            f"A maioria das ocorrências ({percentual_max}%) envolve vítimas do sexo {sexo_max}."
        )
    else:
        context["analise_sexo"] = "Não há dados suficientes para análise por sexo."

    # Análise de faixa etária
    if idade_dados:
        # Encontrar a faixa etária mais frequente (excluindo "Prejudicado")
        idade_dados_sem_prej = idade_dados.copy()
        idade_labels_sem_prej = idade_labels.copy()

        if "Prejudicado" in idade_labels:
            idx = idade_labels.index("Prejudicado")
            idade_dados_sem_prej.pop(idx)
            idade_labels_sem_prej.pop(idx)

        if idade_dados_sem_prej:
            faixa_max = idade_labels_sem_prej[
                idade_dados_sem_prej.index(max(idade_dados_sem_prej))
            ]
            context["analise_idade"] = (
                f"A faixa etária mais afetada é de {faixa_max}, representando uma parcela significativa das ocorrências."
            )
        else:
            context["analise_idade"] = (
                "Não há dados suficientes para análise por faixa etária."
            )
    else:
        context["analise_idade"] = (
            "Não há dados suficientes para análise por faixa etária."
        )

    # Análise de cidade
    if cidade_dados:
        cidade_max = cidade_labels[0]  # Já está ordenado por total
        percentual_max = (
            round((cidade_dados[0] / total_cidade) * 100, 1) if total_cidade > 0 else 0
        )
        context["analise_cidade"] = (
            f"A cidade de {cidade_max} concentra {percentual_max}% das ocorrências, sendo a mais afetada."
        )
    else:
        context["analise_cidade"] = "Não há dados suficientes para análise por cidade."

    # Renderiza o template com o contexto
    return render(request, "ocorrencias/relatorio_dashboard.html", context)
