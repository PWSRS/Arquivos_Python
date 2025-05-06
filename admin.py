from django.contrib import admin
from .models import Ocorrencia, Tipo, SituacaoCarceraria

# admin.site.register(Ocorrencia)
admin.site.register(Tipo)
admin.site.register(SituacaoCarceraria)


class OcorrenciaAdmin(admin.ModelAdmin):
    readonly_fields = [
        field.name for field in Ocorrencia._meta.fields
    ]  # Todos os campos como somente leitura

    def has_add_permission(self, request):
        return False  # Ninguém pode adicionar

    def has_change_permission(self, request, obj=None):
        return False  # Ninguém pode editar

    def has_delete_permission(self, request, obj=None):
        return False  # Ninguém pode deletar


admin.site.register(Ocorrencia, OcorrenciaAdmin)
