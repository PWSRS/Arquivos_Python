from django import forms
from .models import (
    Ocorrencia,
    Cidade,
    Tipo,
    Sexo,
    FaixaEtaria,
    Turno,
    Intervalo,
    DiaSemana,
    LocalObito,
    CorPele,
    SituacaoCarceraria,
    CausaFato,
    TraficoPosse,
    Orcrim,
    MeioEmpregado,
    Cliente,
)
from decimal import Decimal, InvalidOperation


class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = "__all__"
        widgets = {
            "data_fato": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "historico": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,  # aumenta a altura
                }
            ),
            "latitude": forms.TextInput(attrs={"placeholder": "Ex: -31.7476"}),
            "longitude": forms.TextInput(attrs={"placeholder": "Ex: -52.3155"}),
            "rg_autor": forms.TextInput(attrs={"placeholder": "Apenas números"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplica a classe Bootstrap a todos os campos
        for field in self.fields.values():
            if field.widget.__class__ != forms.Textarea:
                field.widget.attrs["class"] = "form-control"
                
        # Formata a data para o formato esperado pelo input type="date"
        if self.instance and self.instance.pk and self.instance.data_fato:
            self.initial['data_fato'] = self.instance.data_fato.strftime('%Y-%m-%d')

        # Define os labels personalizados dos selects
        self.fields["sexo"].empty_label = "Selecione o sexo"
        self.fields["faixa_etaria"].empty_label = "Selecione a faixa etária"
        self.fields["tipo"].empty_label = "Selecione o tipo"
        self.fields["turno"].empty_label = "Selecione o turno"
        self.fields["intervalo"].empty_label = "Selecione o intervalo"
        self.fields["dia_semana"].empty_label = "Selecione o dia da semana"
        self.fields["local_obito"].empty_label = "Selecione o local do óbito"
        self.fields["cor_pele"].empty_label = "Selecione a cor de pele"
        self.fields["situacao_carceraria"].empty_label = (
            "Selecione a situação carcerária"
        )
        self.fields["causa_fato"].empty_label = "Selecione a causa do fato"
        self.fields["trafico_posse"].empty_label = "Selecione tráfico ou posse"
        self.fields["orcrim"].empty_label = "Selecione a ORCRIM"
        self.fields["meio_empregado"].empty_label = "Selecione o meio empregado"
        self.fields["cidade"].empty_label = "Selecione a cidade"
        self.fields["mes"].empty_label = "Selecione o mês"
        self.fields["opm"].empty_label = "Selecione o OPM"
        self.fields["ano"].empty_label = "Selecione o Ano"

    def clean_latitude(self):
        valor = self.cleaned_data.get("latitude")
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            return Decimal(valor)
        except (InvalidOperation, TypeError):
            raise forms.ValidationError("Informe uma latitude válida (ex: -31.747611)")

    def clean_longitude(self):
        valor = self.cleaned_data.get("longitude")
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        try:
            return Decimal(valor)
        except (InvalidOperation, TypeError):
            raise forms.ValidationError("Informe uma longitude válida (ex: -52.315527)")
            
    def clean_rg_autor(self):
        valor = self.cleaned_data.get("rg_autor")
        if valor:
            # Remove qualquer caractere não numérico
            valor_limpo = ''.join(c for c in str(valor) if c.isdigit())
            
            # Verifica se o valor contém apenas dígitos
            if valor_limpo != str(valor):
                raise forms.ValidationError("O RG deve conter apenas números, sem pontos ou outros caracteres.")
                
            # Verifica se o valor é positivo
            if int(valor_limpo) <= 0:
                raise forms.ValidationError("O RG deve ser um número positivo.")
                
            return valor_limpo
        return valor


class CidadeForm(forms.ModelForm):
    class Meta:
        model = Cidade
        fields = ["nome"]


class TipoForm(forms.ModelForm):
    class Meta:
        model = Tipo
        fields = ["nome"]


class SexoForm(forms.ModelForm):
    class Meta:
        model = Sexo
        fields = ["nome"]


class FaixaEtariaForm(forms.ModelForm):
    class Meta:
        model = FaixaEtaria
        fields = ["descricao"]


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ["descricao"]


class IntervaloForm(forms.ModelForm):
    class Meta:
        model = Intervalo
        fields = ["descricao"]


class DiaSemanaForm(forms.ModelForm):
    class Meta:
        model = DiaSemana
        fields = ["descricao"]


class LocalObitoForm(forms.ModelForm):
    class Meta:
        model = LocalObito
        fields = ["descricao"]


class CorPeleForm(forms.ModelForm):
    class Meta:
        model = CorPele
        fields = ["descricao"]


class SituacaoCarcerariaForm(forms.ModelForm):
    class Meta:
        model = SituacaoCarceraria
        fields = ["descricao"]


class CausaFatoForm(forms.ModelForm):
    class Meta:
        model = CausaFato
        fields = ["descricao"]


class TraficoPosseForm(forms.ModelForm):
    class Meta:
        model = TraficoPosse
        fields = ["descricao"]


class OrcrimForm(forms.ModelForm):
    class Meta:
        model = Orcrim
        fields = ["descricao"]


class MeioEmpregadoForm(forms.ModelForm):
    class Meta:
        model = MeioEmpregado
        fields = ["descricao"]


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "email", "telefone", "foto"]
