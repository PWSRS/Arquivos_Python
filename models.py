from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# ==== MODELOS AUXILIARES (LISTAS EDITÁVEIS) ====


class Tipo(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Cidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Sexo(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome


class FaixaEtaria(models.Model):
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao


class Turno(models.Model):
    descricao = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descricao


INTERVALO_CHOICES = [
    ("00-02", "00-02"),
    ("02-04", "02-04"),
    ("04-06", "04-06"),
    ("06-08", "06-08"),
    ("08-10", "08-10"),
    ("10-12", "10-12"),
    ("12-14", "12-14"),
    ("14-16", "14-16"),
    ("16-18", "16-18"),
    ("18-20", "18-20"),
    ("20-22", "20-22"),
    ("22-00", "22-00"),
]


class Intervalo(models.Model):
    descricao = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descricao


class DiaSemana(models.Model):
    descricao = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descricao


class LocalObito(models.Model):
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao


class CorPele(models.Model):
    descricao = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.descricao


class SituacaoCarceraria(models.Model):
    descricao = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descricao


class CausaFato(models.Model):
    descricao = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descricao


class TraficoPosse(models.Model):  # sem acento
    descricao = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.descricao


class Orcrim(models.Model):
    descricao = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descricao


class MeioEmpregado(models.Model):
    descricao = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.descricao


class Mes(models.Model):
    nome = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nome


# ==== MODELO PRINCIPAL ====


class Ocorrencia(models.Model):
    ano = models.IntegerField(choices=[(i, i) for i in range(2016, 2031)])
    nome = models.CharField(max_length=200)
    idade = models.IntegerField()
    faixa_etaria = models.ForeignKey(
        FaixaEtaria, on_delete=models.SET_NULL, null=True, blank=True
    )
    profissao = models.CharField(max_length=100, blank=True, null=True)
    sexo = models.ForeignKey(Sexo, on_delete=models.SET_NULL, null=True, blank=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    endereco_fato = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    opm = models.CharField(
        max_length=50,
        choices=[
            ("4º BPM", "4º BPM"),
            ("6º BPM", "6º BPM"),
            ("4ª Cia Ind.", "4ª Cia Ind."),
        ],
    )
    data_fato = models.DateField()
    mes = models.ForeignKey(Mes, on_delete=models.SET_NULL, null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    intervalo = models.ForeignKey(
        Intervalo, on_delete=models.SET_NULL, null=True, blank=True
    )
    turno = models.ForeignKey(Turno, on_delete=models.SET_NULL, null=True, blank=True)
    dia_semana = models.ForeignKey(
        DiaSemana, on_delete=models.SET_NULL, null=True, blank=True
    )
    tipo = models.ForeignKey(Tipo, on_delete=models.SET_NULL, null=True, blank=True)
    local_obito = models.ForeignKey(
        LocalObito, on_delete=models.SET_NULL, null=True, blank=True
    )
    cor_pele = models.ForeignKey(
        CorPele, on_delete=models.SET_NULL, null=True, blank=True
    )
    OPCOES_ANTECEDENTES = [
        ("SIM", "SIM"),
        ("NÃO", "NÃO"),
        ("NÃO INFORMADO", "NÃO INFORMADO"),
    ]
    possui_antecedentes = models.CharField(
        max_length=15,
        choices=OPCOES_ANTECEDENTES,
        default="NÃO INFORMADO",
        blank=True,
        null=True,
    )
    situacao_carceraria = models.ForeignKey(
        SituacaoCarceraria, on_delete=models.SET_NULL, null=True, blank=True
    )
    causa_fato = models.ForeignKey(
        CausaFato, on_delete=models.SET_NULL, null=True, blank=True
    )
    trafico_posse = models.ForeignKey(
        TraficoPosse, on_delete=models.SET_NULL, null=True, blank=True
    )
    orcrim = models.ForeignKey(Orcrim, on_delete=models.SET_NULL, null=True, blank=True)
    coordenadas_geograficas = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    historico = models.TextField(blank=True, null=True)
    orgao_registro = models.CharField(max_length=100, blank=True, null=True)
    ano_registro = models.IntegerField(blank=True, null=True)
    numero_registro = models.CharField(max_length=100, blank=True, null=True)
    meio_empregado = models.ForeignKey(
        MeioEmpregado, on_delete=models.SET_NULL, null=True, blank=True
    )

    nome_autor = models.CharField(max_length=200, blank=True, null=True)
    rg_autor = models.CharField(max_length=50, blank=True, null=True)
    criado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.nome} - {self.ano}"

    def get_absolute_url(self):
        return reverse("ocorrencia_detail", kwargs={"pk": self.pk})


class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, null=True, blank=True)
    foto = models.ImageField(
        upload_to="clientes_fotos/", null=True, blank=True
    )  # Campo para foto

    def __str__(self):
        return self.nome
