from django.contrib import admin
from .models import Paciente, Profissional, Agendamento, Transacao


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "email")


@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = ("nome",)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = (
        "paciente",
        "profissional",
        "data",
        "hora_inicio",
        "hora_fim",
    )
    list_filter = ("data", "profissional")


# 👇 ADICIONE ISSO AQUI EMBAIXO

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ("descricao", "tipo", "valor", "data", "pago")
    list_filter = ("tipo", "pago", "data")
    search_fields = ("descricao",)


from django.contrib import admin
from .models import Plano

@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ("id", "nome")
    search_fields = ("nome",)