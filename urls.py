from django.urls import path, include
from . import views
from .views import OcorrenciaAjaxListView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Ocorrências
    path("", views.OcorrenciaListView.as_view(), name="ocorrencia_list"),
    path("nova/", views.OcorrenciaCreateView.as_view(), name="ocorrencia_create"),
    path("<int:pk>/", views.OcorrenciaDetailView.as_view(), name="ocorrencia_detail"),
    path(
        "<int:pk>/editar/", views.OcorrenciaUpdateView.as_view(), name="ocorrencia_edit"
    ),
    path(
        "<int:pk>/excluir/",
        views.OcorrenciaDeleteView.as_view(),
        name="ocorrencia_delete",
    ),
    # Tipos
    path("tipos/", views.TipoListView.as_view(), name="tipo_list"),
    path("tipos/novo/", views.TipoCreateView.as_view(), name="tipo_create"),
    path("tipos/<int:pk>/editar/", views.TipoUpdateView.as_view(), name="tipo_update"),
    path("tipos/<int:pk>/excluir/", views.TipoDeleteView.as_view(), name="tipo_delete"),
    # Cidades
    path("cidades/", views.CidadeListView.as_view(), name="cidade_list"),
    path("cidades/nova/", views.CidadeCreateView.as_view(), name="cidade_create"),
    path(
        "cidades/<int:pk>/editar/",
        views.CidadeUpdateView.as_view(),
        name="cidade_update",
    ),
    path(
        "cidades/<int:pk>/excluir/",
        views.CidadeDeleteView.as_view(),
        name="cidade_delete",
    ),
    # Meio Empregado
    path("meios/", views.MeioEmpregadoListView.as_view(), name="meioempregado_list"),
    path(
        "meios/novo/",
        views.MeioEmpregadoCreateView.as_view(),
        name="meioempregado_create",
    ),
    path(
        "meios/<int:pk>/editar/",
        views.MeioEmpregadoUpdateView.as_view(),
        name="meioempregado_update",
    ),
    path(
        "meios/<int:pk>/excluir/",
        views.MeioEmpregadoDeleteView.as_view(),
        name="meioempregado_delete",
    ),
    # ORCRIM
    path("orcrins/", views.OrcrimListView.as_view(), name="orcrim_list"),
    path("orcrins/nova/", views.OrcrimCreateView.as_view(), name="orcrim_create"),
    path(
        "orcrins/<int:pk>/editar/",
        views.OrcrimUpdateView.as_view(),
        name="orcrim_update",
    ),
    path(
        "orcrins/<int:pk>/excluir/",
        views.OrcrimDeleteView.as_view(),
        name="orcrim_delete",
    ),
    # Causa do Fato
    path("causasfato/", views.CausaFatoListView.as_view(), name="causafato_list"),
    path(
        "causasfato/nova/", views.CausaFatoCreateView.as_view(), name="causafato_create"
    ),
    path(
        "causasfato/<int:pk>/editar/",
        views.CausaFatoUpdateView.as_view(),
        name="causafato_update",
    ),
    path(
        "causasfato/<int:pk>/excluir/",
        views.CausaFatoDeleteView.as_view(),
        name="causafato_delete",
    ),
    # Importação e Exportação
    path("importar/", views.ImportarDadosView.as_view(), name="importar_dados"),
    path("exportar/", views.ExportarDadosView.as_view(), name="exportar_dados"),
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/dados/", views.dashboard_dados, name="dashboard_dados"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # path('dashboard/dados/', views.dados_por_tipo, name='dados_por_tipo'),
    path("dashboard/dados/", views.dashboard_dados, name="dashboard_dados"),
    # path('dashboard/dados-tipo/', views.dados_por_tipo, name='dados_por_tipo'),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/dados/", views.dashboard_dados, name="dashboard_dados"),
    path(
        "ocorrencias/ajax/",
        views.OcorrenciaAjaxListView.as_view(),
        name="ocorrencia-ajax-list",
    ),
    # Autenticação
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # FORM COM FOTO
    path("clientes/", views.cliente_list, name="cliente_list"),
    path("clientes/novo/", views.cliente_create, name="cliente_create"),
    path("clientes/<int:pk>/editar/", views.cliente_edit, name="cliente_edit"),
    path("clientes/<int:pk>/excluir/", views.cliente_delete, name="cliente_delete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
