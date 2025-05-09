from django.contrib import messages
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.urls import reverse_lazy
from .models import (
    Ocorrencia,
    SituacaoCarceraria,
    LocalObito,
    Tipo,
    Cidade,
    Orcrim,
    CausaFato,
    MeioEmpregado,
    Sexo,
    FaixaEtaria,
    Mes,
    Intervalo,
    DiaSemana,
    CorPele,
    TraficoPosse,
    Turno,
    Cliente,
)
from .forms import (
    OcorrenciaForm,
    TipoForm,
    CidadeForm,
    OrcrimForm,
    CausaFatoForm,
    MeioEmpregadoForm,
    ClienteForm,
)
import pandas as pd
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from django.db.models import Q, F
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
import plotly.graph_objs as go


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect("login")  # ou 'ocorrencia_list'
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# IMPORTAR DADOS
class ImportarDadosView(LoginRequiredMixin, View):
    template_name = "ocorrencias/importar_dados.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            excel_file = request.FILES["arquivo"]
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                # Chaves estrangeiras com get_or_create
                faixa_etaria = FaixaEtaria.objects.get_or_create(
                    descricao=row["Faixa etária"]
                )[0]
                sexo = Sexo.objects.get_or_create(nome=row["Sexo"])[0]
                cidade = Cidade.objects.get_or_create(nome=row["Cidade"])[0]
                mes = Mes.objects.get_or_create(nome=row["Mês"])[0]
                intervalo = Intervalo.objects.get_or_create(descricao=row["Intervalo"])[
                    0
                ]
                turno = Turno.objects.get_or_create(descricao=row["Turno"])[0]
                dia_semana = DiaSemana.objects.get_or_create(
                    descricao=row["Dia da semana"]
                )[0]
                tipo = Tipo.objects.get_or_create(nome=row["Tipo"])[0]
                cor_pele = CorPele.objects.get_or_create(descricao=row["Cor de pele"])[
                    0
                ]
                causa_fato = CausaFato.objects.get_or_create(
                    descricao=row["Causa do fato"]
                )[0]
                trafico_posse = TraficoPosse.objects.get_or_create(
                    descricao=row["Tráfico/Posse"]
                )[0]
                orcrim = Orcrim.objects.get_or_create(descricao=row["ORCRIM"])[0]
                meio_empregado = MeioEmpregado.objects.get_or_create(
                    descricao=row["Meio empregado"]
                )[0]
                local_obito = LocalObito.objects.get_or_create(
                    descricao=row["Local do óbito"]
                )[0]
                situacao_carceraria = SituacaoCarceraria.objects.get_or_create(
                    descricao=row["Situação carcerária"]
                )[0]

                # Conversão da hora
                hora_valor = pd.to_datetime(row["Hora"], errors="coerce")
                hora = hora_valor.time() if pd.notna(hora_valor) else None

                # Tratamento de possíveis NaNs para campos numéricos
                ano = int(row["ANO"]) if pd.notna(row["ANO"]) else 0
                idade = int(row["Idade"]) if pd.notna(row["Idade"]) else 0
                ano_registro = (
                    int(row["Ano Registro"]) if pd.notna(row["Ano Registro"]) else 0
                )
                numero_registro = (
                    int(row["Número Inteiro Ocorrência"])
                    if pd.notna(row["Número Inteiro Ocorrência"])
                    else 0
                )

                ocorrencia = Ocorrencia(
                    ano=ano,
                    nome=row["Nome"],
                    idade=idade,
                    faixa_etaria=faixa_etaria,
                    profissao=row["Profissão"],
                    sexo=sexo,
                    documento=row["Documento"],
                    endereco_fato=row["Endereço do fato"],
                    numero=row["NR"],
                    bairro=row["Bairro"],
                    cidade=cidade,
                    opm=row["OPM"],
                    data_fato=pd.to_datetime(row["Data do fato"], errors="coerce"),
                    mes=mes,
                    hora=hora,
                    intervalo=intervalo,
                    turno=turno,
                    dia_semana=dia_semana,
                    tipo=tipo,
                    local_obito=local_obito,
                    cor_pele=cor_pele,
                    possui_antecedentes=row["Possui antecedentes criminais"],
                    situacao_carceraria=situacao_carceraria,
                    causa_fato=causa_fato,
                    trafico_posse=trafico_posse,
                    orcrim=orcrim,
                    coordenadas_geograficas=row["Coordenadas"],
                    latitude=row["Latitude"],
                    longitude=row["Longitude"],
                    historico=row["Histórico"],
                    orgao_registro=row["Órgão Registro"],
                    ano_registro=ano_registro,
                    numero_registro=numero_registro,
                    meio_empregado=meio_empregado,
                    nome_autor=row["Nome do autor(a)"],
                    rg_autor=row["RG do Autor(a)"],
                )

                ocorrencia.save()

            messages.success(request, "Importação realizada com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro na importação: {e}")

        return redirect("importar_dados")


# EXPORTAR DADOS
class ExportarDadosView(LoginRequiredMixin, View):
    def get(self, request):
        ocorrencias = Ocorrencia.objects.select_related(
            "faixa_etaria",
            "sexo",
            "cidade",
            "mes",
            "intervalo",
            "turno",
            "dia_semana",
            "tipo",
            "local_obito",
            "cor_pele",
            "situacao_carceraria",
            "causa_fato",
            "trafico_posse",
            "orcrim",
            "meio_empregado",
        )

        data = []
        for o in ocorrencias:
            data.append(
                {
                    "ANO": o.ano,
                    "Nome": o.nome,
                    "Idade": o.idade,
                    "Faixa etária": o.faixa_etaria.descricao if o.faixa_etaria else "",
                    "Profissão": o.profissao,
                    "Sexo": o.sexo.nome if o.sexo else "",
                    "Documento": o.documento,
                    "Endereço do fato": o.endereco_fato,
                    "NR": o.numero,
                    "Bairro": o.bairro,
                    "Cidade": o.cidade.nome if o.cidade else "",
                    "OPM": o.opm,
                    "Data do fato": o.data_fato,
                    "Mês": o.mes.nome if o.mes else "",
                    "Hora": o.hora,
                    "Intervalo": o.intervalo.descricao if o.intervalo else "",
                    "Turno": o.turno.descricao if o.turno else "",
                    "Dia da semana": o.dia_semana.descricao if o.dia_semana else "",
                    "Tipo": o.tipo.nome if o.tipo else "",
                    "Local do óbito": o.local_obito.descricao if o.local_obito else "",
                    "Cor de pele": o.cor_pele.descricao if o.cor_pele else "",
                    "Possui antecedentes criminais": o.possui_antecedentes,
                    "Situação carcerária": (
                        o.situacao_carceraria.descricao if o.situacao_carceraria else ""
                    ),
                    "Causa do fato": o.causa_fato.descricao if o.causa_fato else "",
                    "Tráfico/Posse": (
                        o.trafico_posse.descricao if o.trafico_posse else ""
                    ),
                    "ORCRIM": o.orcrim.descricao if o.orcrim else "",
                    "Coordenadas": o.coordenadas_geograficas,
                    "Latitude": o.latitude,
                    "Longitude": o.longitude,
                    "Histórico": o.historico,
                    "Órgão Registro": o.orgao_registro,
                    "Ano Registro": o.ano_registro,
                    "Número Inteiro Ocorrência": o.numero_registro,
                    "Meio empregado": (
                        o.meio_empregado.descricao if o.meio_empregado else ""
                    ),
                    "Nome do autor(a)": o.nome_autor,
                    "RG do Autor(a)": o.rg_autor,
                }
            )

        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            "attachment; filename=ocorrencias_exportadas.xlsx"
        )
        df.to_excel(response, index=False)

        return response


# Ocorrências
class OcorrenciaAjaxListView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "").strip()

        # Filtra pelo campo "nome" (case insensitive)
        if query:
            ocorrencias = Ocorrencia.objects.filter(nome__icontains=query)
        else:
            ocorrencias = Ocorrencia.objects.all()

        html = render_to_string(
            "ocorrencias/ocorrencia_tabela_parcial.html", {"ocorrencias": ocorrencias}
        )

        return JsonResponse({"html": html})


class OcorrenciaListView(LoginRequiredMixin, ListView):
    model = Ocorrencia
    template_name = "ocorrencias/ocorrencia_list.html"
    context_object_name = "ocorrencias"
    paginate_by = 50
    ordering = ["-data_fato"]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(nome__icontains=query)

        return queryset


class SomenteSuperuserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class OcorrenciaCreateView(LoginRequiredMixin, SomenteSuperuserMixin, CreateView):
    model = Ocorrencia
    form_class = OcorrenciaForm
    template_name = "ocorrencias/ocorrencia_form.html"
    success_url = reverse_lazy("ocorrencia_list")


class OcorrenciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Ocorrencia
    form_class = OcorrenciaForm
    template_name = "ocorrencias/ocorrencia_form.html"
    success_url = reverse_lazy("ocorrencia_list")


class OcorrenciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Ocorrencia
    template_name = "ocorrencias/ocorrencia_confirm_delete.html"
    success_url = reverse_lazy("ocorrencia_list")


class OcorrenciaDetailView(LoginRequiredMixin, DetailView):
    model = Ocorrencia
    template_name = "ocorrencias/ocorrencia_detail.html"
    context_object_name = "ocorrencia"


# Tipos
class TipoListView(LoginRequiredMixin, ListView):
    model = Tipo
    template_name = "ocorrencias/tipo_list.html"
    context_object_name = "tipos"
    ordering = ["nome"]


class TipoCreateView(LoginRequiredMixin, CreateView):
    model = Tipo
    form_class = TipoForm
    template_name = "ocorrencias/tipo_form.html"
    success_url = reverse_lazy("tipo_list")


class TipoUpdateView(LoginRequiredMixin, UpdateView):
    model = Tipo
    form_class = TipoForm
    template_name = "ocorrencias/tipo_form.html"
    success_url = reverse_lazy("tipo_list")


class TipoDeleteView(LoginRequiredMixin, DeleteView):
    model = Tipo
    template_name = "ocorrencias/tipo_confirm_delete.html"
    success_url = reverse_lazy("tipo_list")


# Cidades
class CidadeListView(LoginRequiredMixin, ListView):
    model = Cidade
    template_name = "ocorrencias/cidade_list.html"
    context_object_name = "cidades"
    ordering = ["nome"]


class CidadeCreateView(LoginRequiredMixin, CreateView):
    model = Cidade
    form_class = CidadeForm
    template_name = "ocorrencias/cidade_form.html"
    success_url = reverse_lazy("cidade_list")


class CidadeUpdateView(LoginRequiredMixin, UpdateView):
    model = Cidade
    form_class = CidadeForm
    template_name = "ocorrencias/cidade_form.html"
    success_url = reverse_lazy("cidade_list")


class CidadeDeleteView(LoginRequiredMixin, DeleteView):
    model = Cidade
    template_name = "ocorrencias/cidade_confirm_delete.html"
    success_url = reverse_lazy("cidade_list")


# ORCRIM
class OrcrimListView(LoginRequiredMixin, ListView):
    model = Orcrim
    template_name = "ocorrencias/orcrim_list.html"
    context_object_name = "orcrims"
    ordering = ["descricao"]


class OrcrimCreateView(LoginRequiredMixin, CreateView):
    model = Orcrim
    form_class = OrcrimForm
    template_name = "ocorrencias/orcrim_form.html"
    success_url = reverse_lazy("orcrim_list")


class OrcrimUpdateView(LoginRequiredMixin, UpdateView):
    model = Orcrim
    form_class = OrcrimForm
    template_name = "ocorrencias/orcrim_form.html"
    success_url = reverse_lazy("orcrim_list")


class OrcrimDeleteView(LoginRequiredMixin, DeleteView):
    model = Orcrim
    template_name = "ocorrencias/orcrim_confirm_delete.html"
    success_url = reverse_lazy("orcrim_list")


# CAUSA DO FATO
class CausaFatoListView(LoginRequiredMixin, ListView):
    model = CausaFato
    template_name = "ocorrencias/causafato_list.html"
    context_object_name = "causas"
    ordering = ["descricao"]


class CausaFatoCreateView(LoginRequiredMixin, CreateView):
    model = CausaFato
    fields = ["descricao"]
    template_name = "ocorrencias/causafato_form.html"
    success_url = reverse_lazy("causafato_list")


class CausaFatoUpdateView(LoginRequiredMixin, UpdateView):
    model = CausaFato
    fields = ["descricao"]
    template_name = "ocorrencias/causafato_form.html"
    success_url = reverse_lazy("causafato_list")


class CausaFatoDeleteView(LoginRequiredMixin, DeleteView):
    model = CausaFato
    template_name = "ocorrencias/causafato_confirm_delete.html"
    success_url = reverse_lazy("causafato_list")


# MEIO EMPREGADO
class MeioEmpregadoListView(LoginRequiredMixin, ListView):
    model = MeioEmpregado
    template_name = "ocorrencias/meioempregado_list.html"
    context_object_name = "meios"
    ordering = ["descricao"]


class MeioEmpregadoCreateView(LoginRequiredMixin, CreateView):
    model = MeioEmpregado
    form_class = MeioEmpregadoForm
    template_name = "ocorrencias/meioempregado_form.html"
    success_url = reverse_lazy("meioempregado_list")


class MeioEmpregadoUpdateView(LoginRequiredMixin, UpdateView):
    model = MeioEmpregado
    form_class = MeioEmpregadoForm
    template_name = "ocorrencias/meioempregado_form.html"
    success_url = reverse_lazy("meioempregado_list")


class MeioEmpregadoDeleteView(LoginRequiredMixin, DeleteView):
    model = MeioEmpregado
    template_name = "ocorrencias/meioempregado_confirm_delete.html"
    success_url = reverse_lazy("meioempregado_list")


# CRIAÇÃO DE GRÁFICOS
def dashboard(request):
    from .models import Sexo, Tipo, Cidade

    context = {
        "sexos": Sexo.objects.all(),
        "tipos": Tipo.objects.all(),
        "cidades": Cidade.objects.all(),
    }
    return render(request, "ocorrencias/dashboard.html", context)


def dashboard_dados(request):
    # Filtros recebidos via GET
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    sexo = request.GET.get("sexo")
    tipo = request.GET.get("tipo")
    cidade = request.GET.get("cidade")
    faixa_idade = request.GET.get("faixa_etaria")

    ocorrencias = Ocorrencia.objects.all()

    # Filtros aplicados
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

    # Gráfico por mês
    mes_count = ocorrencias.values("mes", "mes__nome").annotate(total=Count("id")).order_by("mes")
    mes_labels = [item["mes__nome"] for item in mes_count]
    mes_dados = [item["total"] for item in mes_count]

    # Gráfico por sexo
    sexo_count = ocorrencias.values("sexo__nome").annotate(total=Count("id"))
    sexo_labels = [item["sexo__nome"] for item in sexo_count]
    sexo_dados = [item["total"] for item in sexo_count]

    # Gráfico por faixa etária
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

    # Gráfico por cidade
    cidade_count = (
        ocorrencias.values("cidade__nome")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )
    cidade_labels = [item["cidade__nome"] for item in cidade_count]
    cidade_dados = [item["total"] for item in cidade_count]

    return JsonResponse(
        {
            "mes": {"labels": mes_labels, "dados": mes_dados},
            "sexo": {"labels": sexo_labels, "dados": sexo_dados},
            "idade": {
                "labels": list(idade_faixas.keys()),
                "dados": list(idade_faixas.values()),
            },
            "cidade": {"labels": cidade_labels, "dados": cidade_dados},
        }
    )


def cliente_list(request):
    clientes = Cliente.objects.all().order_by("nome")
    return render(request, "ocorrencias/cliente_list.html", {"clientes": clientes})


def cliente_create(request):
    if request.method == "POST":
        form = ClienteForm(
            request.POST, request.FILES
        )  # Não esquecer de usar request.FILES para imagens
        if form.is_valid():
            form.save()
            return redirect("cliente_list")
    else:
        form = ClienteForm()
    return render(request, "ocorrencias/cliente_form.html", {"form": form})


def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == "POST":
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect("cliente_list")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "ocorrencias/cliente_form.html", {"form": form})


def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    cliente.delete()
    return redirect("cliente_list")
