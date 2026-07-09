from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.dispatch import receiver 
from datetime import time
from django.conf import settings


class SexoChoices(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMININO = 'F', 'Feminino'
    NAO_INFORMADO = 'N', 'Não informado'

class UFChoices(models.TextChoices):
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    AP = 'AP', 'Amapá'
    AM = 'AM', 'Amazonas'
    BA = 'BA', 'Bahia'
    CE = 'CE', 'Ceará'
    DF = 'DF', 'Distrito Federal'
    ES = 'ES', 'Espírito Santo'
    GO = 'GO', 'Goiás'
    MA = 'MA', 'Maranhão'
    MT = 'MT', 'Mato Grosso'
    MS = 'MS', 'Mato Grosso do Sul'
    MG = 'MG', 'Minas Gerais'
    PA = 'PA', 'Pará'
    PB = 'PB', 'Paraíba'
    PR = 'PR', 'Paraná'
    PE = 'PE', 'Pernambuco'
    PI = 'PI', 'Piauí'
    RJ = 'RJ', 'Rio de Janeiro'
    RN = 'RN', 'Rio Grande do Norte'
    RS = 'RS', 'Rio Grande do Sul'
    RO = 'RO', 'Rondônia'
    RR = 'RR', 'Roraima'
    SC = 'SC', 'Santa Catarina'
    SP = 'SP', 'São Paulo'
    SE = 'SE', 'Sergipe'
    TO = 'TO', 'Tocantins'
    NAO_INFORMADO = 'NI', 'Não informado'


def caminho_foto_usuario(instance, filename):
    user = instance.user

    if user.groups.filter(name='Administrador').exists():
        pasta = 'usuarios/administradores'
    elif user.groups.filter(name='Medico').exists():
        pasta = 'usuarios/medicos'
    elif user.groups.filter(name='Recepcionista').exists():
        pasta = 'usuarios/recepcionistas'
    else:
        pasta = 'usuarios/_interno'

    return f'{pasta}/{user.id}_{filename}'


class Pais(models.Model):
    nome = models.CharField(max_length=100) 
    sigla = models.CharField(max_length=2) 
    ddi = models.CharField(max_length=5)    

    def __str__(self):
        return self.nome

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to=caminho_foto_usuario, blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=SexoChoices.choices, default=SexoChoices.NAO_INFORMADO)
    cpf = models.CharField(max_length=11, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    codigo_pais_telefone = models.ForeignKey(Pais, on_delete=models.PROTECT, blank=True, null=True, related_name='telefone_pais')
    codigo_pais_whatsapp = models.ForeignKey(Pais, on_delete=models.PROTECT, blank=True, null=True, related_name='whatsapp_pais')

    # ENDEREÇO
    cep = models.CharField(max_length=8, blank=True, null=True)
    rua = models.CharField(max_length=150, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, choices=UFChoices.choices, default=UFChoices.NAO_INFORMADO, blank=True, null=True )

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def cpf_formatado(self):
        if not self.cpf or len(self.cpf) != 11:
            return ''
        return f'{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}'

    def telefone_formatado(self):
        if not self.telefone:
            return ''
        numeros = ''.join(filter(str.isdigit, self.telefone))
        if len(numeros) == 11:  # celular com DDD
            telefone = f'({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}'
        elif len(numeros) == 10:
            telefone = f'({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}'
        else:
            telefone = numeros
        if self.codigo_pais_telefone and self.codigo_pais_telefone.ddi:
            return f'+{self.codigo_pais_telefone.ddi} {telefone}'
        return telefone

    def whatsapp_formatado(self):
        if not self.whatsapp:
            return ''
        numeros = ''.join(filter(str.isdigit, self.whatsapp))
        if len(numeros) == 11:
            whats = f'({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}'
        elif len(numeros) == 10:
            whats = f'({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}'
        else:
            whats = numeros
        if self.codigo_pais_whatsapp and self.codigo_pais_whatsapp.ddi:
            return f'+{self.codigo_pais_whatsapp.ddi} {whats}'
        return whats

    def cep_formatado(self):
        if not self.cep:
            return ''
        return f'{self.cep[:5]}-{self.cep[5:]}'

class DentistaProfile(models.Model):

    class ConselhoChoices(models.TextChoices):
        CRM = 'CRM', 'CRM'
        CRO = 'CRO', 'CRO'
        NAO_INFORMADO = 'NI', 'Não informado'

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    conselho_tipo = models.CharField(max_length=3, choices=ConselhoChoices.choices, default=ConselhoChoices.NAO_INFORMADO)
    numero_conselho = models.CharField(max_length=50, blank=True, null=True)
    uf_conselho = models.CharField(max_length=2, choices=UFChoices.choices, default=UFChoices.NAO_INFORMADO)

    def __str__(self):
        return f"Dentista: {self.profile.user.get_full_name() or self.profile.user.username}"

# SIGNAL — garante 1 Profile por usuário
@receiver(post_save, sender=User)
def criar_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

class DadosDaClinica(models.Model):

    class FusoHorarioChoices(models.TextChoices):
        NORDESTE = 'ND', 'Nordeste'
        NORTE = 'NE', 'Norte'
        CENTRO_OESTE = 'CO', 'Centro-Oeste'
        SUDESTE = 'SD', 'Sudeste'
        SUL = 'SL', 'Sul'
        NAO_INFORMADO = 'NI', 'Não informado'

    class EmitirReciboChoices(models.TextChoices):
        CLINICA = 'CLINICA', 'Clínica'
        DENTISTA = 'DENTISTA', 'Dentista'
        NAO_INFORMADO = 'NI', 'Não informado'

    nome_clinica = models.CharField(max_length=150, blank=True, null=True)
    nome_comunicacoes = models.CharField(max_length=30, blank=True, null=True)
    responsavel_clinica = models.CharField(max_length=150, blank=True, null=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    logo = models.ImageField(upload_to='clinica/logos/', blank=True, null=True)
    horario_inicio = models.TimeField(null=True, blank=True)
    horario_fim = models.TimeField(null=True, blank=True)
    fuso_horario = models.CharField(max_length=2, choices=FusoHorarioChoices.choices, default=FusoHorarioChoices.NAO_INFORMADO, blank=True, null=True)
    emitir_recibo_em_nome_de = models.CharField(max_length=20, choices=EmitirReciboChoices.choices, default=EmitirReciboChoices.NAO_INFORMADO)

    # Contato
    email_clinica = models.EmailField(blank=True, null=True)
    codigo_pais_telefone_clinica = models.ForeignKey(Pais, on_delete=models.PROTECT, blank=True, null=True,
    related_name='clinicas_telefone')
    codigo_pais_celular_clinica = models.ForeignKey(Pais,on_delete=models.PROTECT, blank=True, null=True,
    related_name='clinicas_celular')
    telefone = models.CharField(max_length=15, blank=True, null=True)
    celular = models.CharField(max_length=15, blank=True, null=True)

    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    rua = models.CharField(max_length=120, blank=True, null=True)
    numero = models.CharField(max_length=5 , blank=True, null=True)
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=128, blank=True, null=True)
    cidade = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=2, choices=UFChoices.choices, default=UFChoices.NAO_INFORMADO, blank=True, null=True)

    def __str__(self):
        return self.nome_clinica

class ProdutoEstoque(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    quantidade_atual = models.PositiveIntegerField(default=0)
    quantidade_ideal = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome


class RetiradaEstoque(models.Model):
    produto = models.ForeignKey(ProdutoEstoque, on_delete=models.CASCADE, related_name='retiradas')
    quantidade_retirada = models.PositiveIntegerField()
    retirado_por = models.ForeignKey(User, on_delete=models.SET_NULL ,null=True,blank=True, related_name='retiradas_feitas')
    autorizado_por = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True, related_name='retiradas_autorizadas')
    data_retirada = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.quantidade_retirada > self.produto.quantidade_atual:
            raise ValidationError("Estoque insuficiente para retirada.")

    def save(self, *args, **kwargs):
        # Evita descontar estoque em edições
        if self.pk:
            return super().save(*args, **kwargs)

        self.full_clean()

        with transaction.atomic():
            produto = (
                ProdutoEstoque.objects
                .select_for_update()
                .get(pk=self.produto.pk)
            )

            if self.quantidade_retirada > produto.quantidade_atual:
                raise ValidationError("Estoque insuficiente para retirada.")

            produto.quantidade_atual -= self.quantidade_retirada
            produto.save(update_fields=["quantidade_atual"])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produto.nome} (-{self.quantidade_retirada})"
    
from django.db import models
from django.core.exceptions import ValidationError


class Paciente(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.nome



class Profissional(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome



class Etiqueta(models.Model):
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nome da Etiqueta"
    )

    cor = models.CharField(
        max_length=7,
        default="#28a745",
        verbose_name="Código Hex da Cor"
    )

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    TIPO_CHOICES = (
        ("consulta", "Consulta"),
        ("retorno", "Retorno"),
    )

    STATUS_CHOICES = (
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("atendido", "Atendido"),
        ("cancelado", "Cancelado"),
        ("retorno", "Retorno"),
    )

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="agendamentos"
    )

    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.CASCADE
    )

    etiqueta = models.ForeignKey(
        "Etiqueta",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agendamentos",
        verbose_name="Etiqueta"
    )

    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="consulta"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente"
    )

    observacoes = models.TextField(
        blank=True,
        null=True
    )

    def clean(self):
        if self.hora_inicio >= self.hora_fim:
            raise ValidationError(
                "A hora final deve ser maior que a inicial."
            )

        conflito = Agendamento.objects.filter(
            profissional=self.profissional,
            data=self.data,
            hora_inicio__lt=self.hora_fim,
            hora_fim__gt=self.hora_inicio,
        ).exclude(pk=self.pk)

        if conflito.exists():
            raise ValidationError(
                "Este profissional já possui agendamento nesse horário."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paciente} - {self.data} ({self.tipo})"

class CompromissoAgenda(models.Model):
    DISPONIBILIDADE_CHOICES = (
        ("ocupado", "Ocupado"),
        ("disponivel", "Disponível"),
    )

    PRIVACIDADE_CHOICES = (
        ("privado", "Privado"),
        ("publico", "Público"),
    )

    ALERTA_CHOICES = (
        ("sem_alerta", "Sem alerta"),
        ("1_minuto", "1 minuto antes"),
        ("5_minutos", "5 minutos antes"),
        ("30_minutos", "30 minutos antes"),
        ("1_hora", "1 hora antes"),
        ("1_dia", "1 dia antes"),
        ("personalizar", "Personalizar"),
    )

    REPETICAO_CHOICES = (
        ("todos_os_dias", "Todos os dias"),
        ("semanalmente", "Semanalmente"),
        ("quinzenalmente", "Quinzenalmente"),
        ("mensalmente", "Mensalmente"),
        ("anualmente", "Anualmente"),
    )

    TERMINAR_REPETICAO_CHOICES = (
        ("nunca", "Nunca"),
        ("data_especifica", "Data específica"),
    )

    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)

    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.CASCADE,
        related_name="compromissos"
    )

    data_inicio = models.DateField()
    hora_inicio = models.TimeField(blank=True, null=True)

    data_fim = models.DateField()
    hora_fim = models.TimeField(blank=True, null=True)

    dia_inteiro = models.BooleanField(default=False)

    repetir = models.BooleanField(default=False)
    tipo_repeticao = models.CharField(
        max_length=30,
        choices=REPETICAO_CHOICES,
        blank=True,
        null=True
    )

    terminar_repeticao = models.CharField(
        max_length=30,
        choices=TERMINAR_REPETICAO_CHOICES,
        default="nunca"
    )

    data_fim_repeticao = models.DateField(blank=True, null=True)

    disponibilidade = models.CharField(
        max_length=20,
        choices=DISPONIBILIDADE_CHOICES,
        default="ocupado"
    )

    privacidade = models.CharField(
        max_length=20,
        choices=PRIVACIDADE_CHOICES,
        default="privado"
    )

    alerta = models.CharField(
        max_length=30,
        choices=ALERTA_CHOICES,
        default="sem_alerta"
    )

    alerta_quantidade = models.PositiveIntegerField(blank=True, null=True)
    alerta_unidade = models.CharField(max_length=20, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.dia_inteiro:
            if not self.hora_inicio or not self.hora_fim:
                raise ValidationError("Informe horário de início e fim.")

            if self.data_inicio == self.data_fim and self.hora_inicio >= self.hora_fim:
                raise ValidationError("O horário final deve ser maior que o inicial.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} - {self.data_inicio}"
    
class EncaixeAgenda(models.Model):
    TURNO_CHOICES = [
        ("", "Qualquer turno"),
        ("manha", "Manhã"),
        ("tarde", "Tarde"),
        ("noite", "Noite"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="encaixes_agenda",
        verbose_name="Paciente"
    )

    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="encaixes_agenda",
        verbose_name="Profissional"
    )

    data_desejada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data desejada"
    )

    qualquer_data = models.BooleanField(
        default=False,
        verbose_name="Qualquer data"
    )

    turno = models.CharField(
        max_length=20,
        choices=TURNO_CHOICES,
        blank=True,
        default="",
        verbose_name="Turno desejado"
    )

    plano = models.CharField(
        max_length=100,
        blank=True,
        default="Particular",
        verbose_name="Plano"
    )

    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observação"
    )

    urgente = models.BooleanField(
        default=False,
        verbose_name="Encaixe urgente"
    )

    etiqueta = models.ForeignKey(
        "Etiqueta",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="encaixes_agenda",
        verbose_name="Rótulo"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Encaixe"
        verbose_name_plural = "Encaixes"
        ordering = ["-urgente", "data_desejada", "-criado_em"]

    def __str__(self):
        return f"Encaixe - {self.paciente}"
    
class AlertaRetorno(models.Model):
    TIPO_RETORNO_CHOICES = [
        ("data_especifica", "Data específica"),
        ("7_dias", "Em 7 dias"),
        ("15_dias", "Em 15 dias"),
        ("30_dias", "Em 30 dias"),
        ("3_meses", "Em 3 meses"),
        ("6_meses", "Em 6 meses"),
    ]

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("agendado", "Agendado"),
        ("concluido", "Concluído"),
        ("cancelado", "Cancelado"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="alertas_retorno",
        verbose_name="Paciente"
    )

    profissional = models.ForeignKey(
        Profissional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas_retorno",
        verbose_name="Profissional"
    )

    tipo_retorno = models.CharField(
        max_length=30,
        choices=TIPO_RETORNO_CHOICES,
        default="data_especifica",
        verbose_name="Retornar em"
    )

    data_retorno = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data aproximada para retorno"
    )

    motivo = models.TextField(
        blank=True,
        null=True,
        verbose_name="Motivo do retorno"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status"
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )

    class Meta:
        verbose_name = "Alerta de retorno"
        verbose_name_plural = "Alertas de retorno"
        ordering = ["data_retorno", "-criado_em"]

    def __str__(self):
        return f"Retorno - {self.paciente}"
    
from django.db import models
from django.contrib.auth.models import User


class CategoriaDespesa(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nome


class Transacao(models.Model):

    TIPO_CHOICES = (
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    )

    STATUS_PAGAMENTO = (
        ('dinheiro', 'Dinheiro'),
        ('credito_maquininha', 'Crédito Maquininha'),
        ('credito', 'Crédito'),
        ('debito_maquininha', 'Débito Maquininha'),
        ('debito', 'Débito'),
        ('pix', 'Pix'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
        ('cheque', 'Cheque'),  # ✅ ADICIONADO
    )

    CAIXA_CHOICES = (
        ('clinica', 'Clínica'),
        ('banco', 'Conta do banco'),
    )

    descricao = models.CharField(max_length=255)

    paciente_nome = models.CharField(max_length=255, null=True, blank=True) 

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    data = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)

    pago = models.BooleanField(default=False)

    categoria = models.ForeignKey(
        CategoriaDespesa,
        on_delete=models.PROTECT,
        related_name='transacoes',
        null=True,
        blank=True
    )

    plano = models.ForeignKey(
        "Plano",  # 👈 coloca como string
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transacoes"
    )

    meio_pagamento = models.CharField(
        max_length=50,
        choices=STATUS_PAGAMENTO,
        null=True,
        blank=True
    )

    caixa = models.CharField(
        max_length=20,
        choices=CAIXA_CHOICES,
        default='clinica'
    )

    profissional = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transacoes_profissional"
    )

    com_recibo = models.BooleanField(default=False)

    observacao = models.TextField(null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.descricao
    
class Plano(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome
    
# models.py
from django.conf import settings
from django.db import models

class PagamentoComissao(models.Model):
    profissional = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_pagamento = models.DateField(auto_now_add=True)

    # período que esse pagamento cobre
    de = models.DateField(null=True, blank=True)
    ate = models.DateField(null=True, blank=True)

    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    observacao = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_pagamento", "-id"]

    def __str__(self):
        return f"{self.profissional} - {self.valor} em {self.data_pagamento}"
    

