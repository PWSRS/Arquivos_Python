from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from .models import Ocorrencia

def ocorrencia_ajax_list(request):
    """
    Função para substituir a classe OcorrenciaAjaxListView
    """
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